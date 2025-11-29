import os
import zipfile
import tempfile
import logging
from datetime import datetime
from django.db import transaction
from .csv_processor import CSVProcessor
from .models import CsvFile

# Set up logger for bulk processing
logger = logging.getLogger('bulk_csv_processor')
logger.setLevel(logging.INFO)


class BulkCSVProcessor:
    """Utility class to process multiple CSV files from a ZIP archive"""
    
    def __init__(self):
        self.processed_files = []
        self.failed_files = []
        self.total_stocks = 0
        self.total_candlesticks = 0
        self.total_files_processed = 0
        self.warnings = []
        self.errors = []
    
    def process_zip_file(self, zip_file):
        """
        Process all CSV files in a ZIP archive
        
        Args:
            zip_file: Uploaded ZIP file containing CSV files
            
        Returns:
            dict: Processing results with detailed statistics
        """
        zip_filename = getattr(zip_file, 'name', 'Unknown ZIP file')
        
        try:
            print(f"\n🚀 [BULK UPLOAD] Starting ZIP file processing...")
            print(f"📦 ZIP File: {zip_filename}")
            print(f"📊 File Size: {zip_file.size if hasattr(zip_file, 'size') else 'Unknown'} bytes")
            logger.info(f"Starting bulk processing of ZIP file: {zip_filename}")
            
            # Reset counters
            self.processed_files = []
            self.failed_files = []
            self.total_stocks = 0
            self.total_candlesticks = 0
            self.total_files_processed = 0
            self.warnings = []
            self.errors = []
            
            # Create temporary directory for extracting files
            with tempfile.TemporaryDirectory() as temp_dir:
                print(f"📁 Extracting ZIP to temporary directory: {temp_dir}")
                logger.info(f"Extracting ZIP to: {temp_dir}")
                
                # Extract ZIP file
                with zipfile.ZipFile(zip_file, 'r') as zf:
                    print(f"📋 ZIP contents: {zf.namelist()}")
                    logger.info(f"ZIP file contains: {zf.namelist()}")
                    zf.extractall(temp_dir)
                    print(f"✅ ZIP extracted successfully")
                
                # Find all CSV files in the extracted directory
                csv_files = []
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.lower().endswith('.csv') and not file.startswith('.'):
                            csv_files.append(os.path.join(root, file))
                
                print(f"🔍 Found {len(csv_files)} CSV files:")
                for i, csv_path in enumerate(csv_files, 1):
                    filename = os.path.basename(csv_path)
                    file_size = os.path.getsize(csv_path)
                    print(f"   {i}. {filename} ({file_size} bytes)")
                    logger.info(f"Found CSV file {i}: {filename} ({file_size} bytes)")
                
                if not csv_files:
                    error_msg = f'No CSV files found in ZIP archive: {zip_filename}'
                    print(f"❌ {error_msg}")
                    logger.error(error_msg)
                    return {
                        'success': False,
                        'error': error_msg,
                        'processed_files': [],
                        'failed_files': [],
                        'total_files_processed': 0,
                        'total_stocks': 0,
                        'total_candlesticks': 0,
                        'warnings': [],
                        'errors': ['No CSV files found in ZIP archive']
                    }
                
                # Process each CSV file
                processor = CSVProcessor()
                print(f"\n🔄 Starting sequential processing of {len(csv_files)} CSV files...")
                logger.info(f"Starting sequential processing of {len(csv_files)} CSV files")
                
                for i, csv_file_path in enumerate(csv_files, 1):
                    filename = os.path.basename(csv_file_path)
                    print(f"\n📄 [{i}/{len(csv_files)}] Processing: {filename}")
                    logger.info(f"Processing file {i}/{len(csv_files)}: {filename}")
                    
                    try:
                        self._process_single_file(processor, csv_file_path, filename, i, len(csv_files))
                        print(f"✅ [{i}/{len(csv_files)}] Completed: {filename}")
                        logger.info(f"Successfully processed file {i}/{len(csv_files)}: {filename}")
                    except Exception as e:
                        error_msg = f"Failed to process {filename}: {str(e)}"
                        print(f"❌ [{i}/{len(csv_files)}] Failed: {filename} - {str(e)}")
                        logger.error(f"Failed to process file {i}/{len(csv_files)}: {filename} - {str(e)}")
                        self.failed_files.append({
                            'filename': filename,
                            'error': str(e),
                            'stocks_processed': 0,
                            'candlesticks_processed': 0
                        })
                        self.errors.append(error_msg)
                
                print(f"\n📊 Bulk processing summary:")
                print(f"   ✅ Successfully processed: {self.total_files_processed} files")
                print(f"   ❌ Failed: {len(self.failed_files)} files")
                print(f"   📈 Total stocks: {self.total_stocks}")
                print(f"   🕯️ Total candlesticks: {self.total_candlesticks}")
                logger.info(f"Bulk processing completed - Success: {self.total_files_processed}, Failed: {len(self.failed_files)}, Stocks: {self.total_stocks}, Candlesticks: {self.total_candlesticks}")
            
            # Create summary
            return {
                'success': True,
                'processed_files': self.processed_files,
                'failed_files': self.failed_files,
                'total_files_processed': self.total_files_processed,
                'total_files_failed': len(self.failed_files),
                'total_stocks': self.total_stocks,
                'total_candlesticks': self.total_candlesticks,
                'warnings': self.warnings,
                'errors': self.errors
            }
            
        except Exception as e:
            error_msg = f'Failed to process ZIP file {zip_filename}: {str(e)}'
            print(f"\n💥 CRITICAL ERROR: {error_msg}")
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'processed_files': self.processed_files,
                'failed_files': self.failed_files,
                'total_files_processed': self.total_files_processed,
                'total_files_failed': len(self.failed_files),
                'total_stocks': self.total_stocks,
                'total_candlesticks': self.total_candlesticks,
                'warnings': self.warnings,
                'errors': self.errors + [f'ZIP processing error: {str(e)}']
            }
    
    def _process_single_file(self, processor, file_path, filename, file_number=None, total_files=None):
        """Process a single CSV file and update statistics"""
        
        progress = f"[{file_number}/{total_files}]" if file_number and total_files else ""
        print(f"   🔍 {progress} Analyzing file structure: {filename}")
        logger.info(f"Analyzing CSV file {progress}: {filename}")
        
        try:
            # Log file size and basic info
            file_size = os.path.getsize(file_path)
            print(f"   📊 {progress} File size: {file_size} bytes")
            
            # Start processing
            print(f"   ⚡ {progress} Starting CSV processing...")
            result = processor.process_csv_file(file_path, filename)
            
            if result['success']:
                print(f"   ✅ {progress} CSV processing successful!")
                print(f"   📈 {progress} Results: {result['stocks_processed']} stocks, {result['candlesticks_processed']} candlesticks")
                print(f"   🏢 {progress} Exchange: {result['exchange']}, Date: {result['date']}")
                logger.info(f"Successfully processed {progress} {filename}: {result['stocks_processed']} stocks, {result['candlesticks_processed']} candlesticks")
                
                # Save file record for tracking (metadata only)
                print(f"   💾 {progress} Saving metadata to database...")
                csv_file = CsvFile.objects.create(
                    filename=filename,
                    date=result['date'],
                    exchange=result['exchange'],
                    stocks_processed=result['stocks_processed'],
                    candlesticks_processed=result['candlesticks_processed']
                )
                print(f"   ✅ {progress} Metadata saved successfully")
                
                # Update totals
                self.total_stocks += result['stocks_processed']
                self.total_candlesticks += result['candlesticks_processed']
                self.total_files_processed += 1
                
                # Add to processed files
                self.processed_files.append({
                    'filename': filename,
                    'date': result['date'],
                    'exchange': result['exchange'],
                    'stocks_processed': result['stocks_processed'],
                    'candlesticks_processed': result['candlesticks_processed'],
                    'warnings': result.get('warnings', [])
                })
                
                # Collect warnings
                if result.get('warnings'):
                    print(f"   ⚠️ {progress} {len(result['warnings'])} warnings found")
                    for warning in result['warnings'][:3]:  # Show first 3 warnings
                        print(f"      - {warning}")
                        self.warnings.append(f"{filename}: {warning}")
                    if len(result['warnings']) > 3:
                        print(f"      - ... and {len(result['warnings']) - 3} more warnings")
                else:
                    print(f"   ✅ {progress} No warnings")
            
            else:
                print(f"   ❌ {progress} CSV processing failed!")
                print(f"   💥 {progress} Error: {result.get('error', 'Unknown error')}")
                logger.error(f"Failed to process {progress} {filename}: {result.get('error', 'Unknown error')}")
                
                # File processing failed
                self.failed_files.append({
                    'filename': filename,
                    'error': result.get('error', 'Unknown error'),
                    'stocks_processed': result.get('stocks_processed', 0),
                    'candlesticks_processed': result.get('candlesticks_processed', 0)
                })
                
                # Add errors
                self.errors.append(f"{filename}: {result.get('error', 'Unknown error')}")
                
                # Add specific row errors if any
                if result.get('errors'):
                    print(f"   📋 {progress} Specific errors:")
                    for i, error in enumerate(result['errors'][:3], 1):  # Limit to first 3 errors per file
                        print(f"      {i}. {error}")
                        self.errors.append(f"{filename}: {error}")
                    if len(result['errors']) > 3:
                        print(f"      ... and {len(result['errors']) - 3} more errors")
        
        except Exception as e:
            error_msg = f"Unexpected error processing {filename}: {str(e)}"
            print(f"   💥 {progress} {error_msg}")
            logger.error(error_msg)
            raise
    
    def get_summary_stats(self):
        """Get summary statistics for the bulk upload"""
        return {
            'total_files': self.total_files_processed + len(self.failed_files),
            'successful_files': self.total_files_processed,
            'failed_files': len(self.failed_files),
            'total_stocks': self.total_stocks,
            'total_candlesticks': self.total_candlesticks,
            'success_rate': (self.total_files_processed / max(1, self.total_files_processed + len(self.failed_files))) * 100
        }