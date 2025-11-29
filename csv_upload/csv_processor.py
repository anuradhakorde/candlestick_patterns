import csv
import os
import re
import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.db import transaction, IntegrityError
from django.utils import timezone
from .models import Stock, Candlestick

# Set up logger for CSV processing
logger = logging.getLogger('csv_processor')


class CSVProcessor:
    """Utility class to process CSV files with stock data"""
    
    # Exchange-specific CSV column mappings
    EXCHANGE_MAPPINGS = {
        'BSE': {
            # BSE column mapping (existing)
            'SC_CODE': 'stock_symbol',
            'SC_NAME': 'stock_name', 
            'SC_GROUP': 'stock_group',
            'SC_TYPE': 'stock_type',  # Not used in database
            'OPEN': 'open_price',
            'HIGH': 'high_price',
            'LOW': 'low_price',
            'CLOSE': 'close_price',
            'LAST': 'last_price',  # Not used in database
            'PREVCLOSE': 'prev_close_price',
            'NO_TRADES': 'number_of_trades',
            'NO_OF_SHRS': 'number_of_shares',
            'NET_TURNOV': 'net_turnover',
            'TDCLOINDI': 'ignore'  # Ignored column
        },
        'NSE': {
            # NSE column mapping (new)
            'SYMBOL': 'stock_symbol',
            'SERIES': 'stock_group',
            'OPEN': 'open_price',
            'HIGH': 'high_price',
            'LOW': 'low_price',
            'CLOSE': 'close_price',
            'LAST': 'last_price',  # Not used in database
            'PREVCLOSE': 'prev_close_price',
            'TOTTRDQTY': 'number_of_shares',
            'TOTTRDVAL': 'net_turnover',
            'TIMESTAMP': 'timestamp',  # Not used in database (date comes from filename)
            'TOTALTRADES': 'number_of_trades',
            'ISIN': 'ignore'  # Ignored column
        }
    }
    
    # Supported exchanges (for validation)
    SUPPORTED_EXCHANGES = list(EXCHANGE_MAPPINGS.keys())
    
    def __init__(self):
        self.processed_stocks = 0
        self.processed_candlesticks = 0
        self.errors = []
        self.warnings = []
    
    @classmethod
    def add_exchange_support(cls, exchange_name, column_mapping):
        """
        Add support for a new exchange by adding its column mapping
        
        Args:
            exchange_name (str): Name of the exchange (e.g., 'NSE', 'BSE')
            column_mapping (dict): Mapping of CSV columns to database fields
        """
        exchange_name = exchange_name.upper()
        cls.EXCHANGE_MAPPINGS[exchange_name] = column_mapping
        if exchange_name not in cls.SUPPORTED_EXCHANGES:
            cls.SUPPORTED_EXCHANGES.append(exchange_name)
    
    @classmethod
    def get_supported_exchanges(cls):
        """Get list of currently supported exchanges"""
        return cls.SUPPORTED_EXCHANGES.copy()
    
    def get_exchange_columns(self, exchange):
        """Get required columns for a specific exchange"""
        return list(self.EXCHANGE_MAPPINGS.get(exchange.upper(), {}).keys())
    
    def parse_filename(self, filename):
        """
        Parse filename to extract date and exchange
        Expected format: YYYYMMDD_EXCHANGE.csv
        Example: 20250101_BSE.csv
        """
        try:
            # Remove .csv extension
            name_without_ext = filename.replace('.csv', '').replace('.CSV', '')
            
            # Split by underscore
            parts = name_without_ext.split('_')
            
            if len(parts) != 2:
                raise ValueError(f"Filename must follow pattern YYYYMMDD_EXCHANGE.csv, got: {filename}")
            
            date_str, exchange = parts
            
            # Parse date
            if len(date_str) != 8:
                raise ValueError(f"Date part must be 8 digits (YYYYMMDD), got: {date_str}")
            
            try:
                parsed_date = datetime.strptime(date_str, '%Y%m%d').date()
            except ValueError:
                raise ValueError(f"Invalid date format in filename: {date_str}")
            
            # Validate exchange
            if not exchange or len(exchange) > 10:
                raise ValueError(f"Exchange name must be 1-10 characters, got: {exchange}")
            
            exchange_upper = exchange.upper()
            if exchange_upper not in self.SUPPORTED_EXCHANGES:
                raise ValueError(f"Unsupported exchange '{exchange_upper}'. Supported exchanges: {', '.join(self.SUPPORTED_EXCHANGES)}")
            
            return parsed_date, exchange_upper
            
        except Exception as e:
            raise ValueError(f"Error parsing filename '{filename}': {str(e)}")
    
    def validate_decimal(self, value, field_name):
        """Convert and validate decimal values"""
        if not value or value.strip() == '':
            return None
        
        try:
            return Decimal(str(value).strip())
        except (InvalidOperation, ValueError):
            self.warnings.append(f"Invalid decimal value for {field_name}: '{value}' - skipping row")
            return None
    
    def validate_integer(self, value, field_name):
        """Convert and validate integer values"""
        if not value or value.strip() == '':
            return None
        
        try:
            return int(float(str(value).strip()))
        except (ValueError, TypeError):
            self.warnings.append(f"Invalid integer value for {field_name}: '{value}' - using None")
            return None
    
    def process_csv_file(self, file_path, filename):
        """
        Process uploaded CSV file and insert data into database
        
        Args:
            file_path: Path to the uploaded CSV file
            filename: Original filename of the uploaded file
            
        Returns:
            dict: Processing results with counts and errors
        """
        try:
            print(f"         🎯 CSV Processor: Starting analysis of {filename}")
            logger.info(f"Starting CSV processing: {filename}")
            
            # Reset counters
            self.processed_stocks = 0
            self.processed_candlesticks = 0
            self.errors = []
            self.warnings = []
            
            # Parse filename for date and exchange
            print(f"         📅 Parsing filename for date and exchange...")
            candle_date, exchange = self.parse_filename(filename)
            print(f"         ✅ Parsed - Date: {candle_date}, Exchange: {exchange}")
            logger.info(f"Parsed filename - Date: {candle_date}, Exchange: {exchange}")
            
            # Get exchange-specific column mapping
            csv_columns = self.EXCHANGE_MAPPINGS.get(exchange)
            if not csv_columns:
                raise ValueError(f"No column mapping found for exchange: {exchange}")
            
            print(f"         🗂️ Using {exchange} column mapping with {len(csv_columns)} columns")
            
            # Process CSV file
            print(f"         📖 Opening and reading CSV file...")
            with open(file_path, 'r', encoding='utf-8') as csvfile:
                # Detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                delimiter = ',' if ',' in sample else '\t'
                print(f"         🔍 Detected delimiter: '{delimiter}'")
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                # Validate headers based on exchange
                expected_headers = set(csv_columns.keys())
                actual_headers = set(reader.fieldnames or [])
                print(f"         📋 CSV Headers: {list(actual_headers)}")
                print(f"         📋 Expected Headers for {exchange}: {list(expected_headers)}")
                
                missing_headers = expected_headers - actual_headers
                if missing_headers:
                    error_msg = f"Missing required columns for {exchange} exchange: {', '.join(missing_headers)}"
                    print(f"         ❌ {error_msg}")
                    logger.error(f"Missing headers for {filename}: {error_msg}")
                    raise ValueError(error_msg)
                
                print(f"         ✅ All required headers found for {exchange}")
                
                # Count total rows first
                rows = list(reader)
                total_rows = len(rows)
                print(f"         📊 Found {total_rows} data rows to process")
                logger.info(f"Processing {total_rows} rows from {filename}")
                
                # Process rows in transaction
                print(f"         💾 Starting database transaction...")
                with transaction.atomic():
                    row_number = 1
                    processed_count = 0
                    error_count = 0
                    
                    for row in rows:
                        row_number += 1
                        try:
                            self._process_row(row, candle_date, exchange, csv_columns)
                            processed_count += 1
                            
                            # Show progress every 100 rows for large files
                            if processed_count % 100 == 0:
                                print(f"         📈 Processed {processed_count}/{total_rows} rows...")
                                
                        except Exception as e:
                            error_count += 1
                            error_msg = f"Row {row_number}: {str(e)}"
                            self.errors.append(error_msg)
                            if error_count <= 3:  # Show first 3 row errors
                                print(f"         ⚠️ Row {row_number} error: {str(e)}")
                            continue
                    
                    print(f"         ✅ Transaction completed - Processed: {processed_count}, Errors: {error_count}")
                    logger.info(f"Database transaction completed for {filename} - Success: {processed_count}, Errors: {error_count}")
            
            print(f"         🎉 CSV processing completed successfully!")
            print(f"         📈 Final results - Stocks: {self.processed_stocks}, Candlesticks: {self.processed_candlesticks}")
            logger.info(f"CSV processing completed for {filename} - Stocks: {self.processed_stocks}, Candlesticks: {self.processed_candlesticks}")
            
            return {
                'success': True,
                'stocks_processed': self.processed_stocks,
                'candlesticks_processed': self.processed_candlesticks,
                'errors': self.errors,
                'warnings': self.warnings,
                'date': candle_date,
                'exchange': exchange
            }
            
        except Exception as e:
            error_msg = f"CSV processing failed for {filename}: {str(e)}"
            print(f"         💥 {error_msg}")
            logger.error(error_msg)
            return {
                'success': False,
                'error': str(e),
                'stocks_processed': self.processed_stocks,
                'candlesticks_processed': self.processed_candlesticks,
                'errors': self.errors,
                'warnings': self.warnings
            }
    
    def _process_row(self, row, candle_date, exchange, csv_columns):
        """Process a single CSV row with exchange-specific column mapping"""
        
        # Helper function to get column value by mapping
        def get_mapped_value(db_field):
            csv_column = None
            for csv_col, db_field_mapped in csv_columns.items():
                if db_field_mapped == db_field:
                    csv_column = csv_col
                    break
            return row.get(csv_column, '').strip() if csv_column else ''
        
        # Extract and validate required fields based on exchange
        stock_symbol = get_mapped_value('stock_symbol')
        stock_group = get_mapped_value('stock_group')
        
        # For NSE, stock_name is same as stock_symbol, for BSE use mapped value
        if exchange == 'NSE':
            stock_name = stock_symbol  # NSE uses SYMBOL for both symbol and name
        else:
            stock_name = get_mapped_value('stock_name')
        
        if not stock_symbol:
            symbol_column = next((col for col, field in csv_columns.items() if field == 'stock_symbol'), 'SYMBOL')
            raise ValueError(f"{symbol_column} (stock symbol) is required")
        
        # Validate price fields
        open_price = self.validate_decimal(get_mapped_value('open_price'), 'OPEN')
        high_price = self.validate_decimal(get_mapped_value('high_price'), 'HIGH')
        low_price = self.validate_decimal(get_mapped_value('low_price'), 'LOW')
        close_price = self.validate_decimal(get_mapped_value('close_price'), 'CLOSE')
        prev_close_price = self.validate_decimal(get_mapped_value('prev_close_price'), 'PREVCLOSE')
        
        # Check for required price fields
        required_prices = [open_price, high_price, low_price, close_price, prev_close_price]
        if any(price is None for price in required_prices):
            raise ValueError("Missing required price data")
        
        # Validate trade data
        number_of_trades = self.validate_integer(get_mapped_value('number_of_trades'), 'number_of_trades')
        number_of_shares = self.validate_integer(get_mapped_value('number_of_shares'), 'number_of_shares')
        net_turnover = self.validate_decimal(get_mapped_value('net_turnover'), 'net_turnover')
        
        # Get or create stock
        stock, created = Stock.objects.get_or_create(
            stock_symbol=stock_symbol,
            stock_exchange=exchange,
            defaults={
                'stock_name': stock_name,
                'stock_group': stock_group
            }
        )
        
        if created:
            self.processed_stocks += 1
        
        # Create candlestick data (check for duplicates)
        candlestick, created = Candlestick.objects.get_or_create(
            stock=stock,
            candle_date=timezone.make_aware(datetime.combine(candle_date, datetime.min.time())),
            defaults={
                'open_price': open_price,
                'high_price': high_price,
                'low_price': low_price,
                'close_price': close_price,
                'prev_close_price': prev_close_price,
                'number_of_trades': number_of_trades,
                'number_of_shares': number_of_shares,
                'net_turnover': net_turnover
            }
        )
        
        if created:
            self.processed_candlesticks += 1
        else:
            self.warnings.append(f"Duplicate candlestick data for {stock_symbol} on {candle_date} - skipped")