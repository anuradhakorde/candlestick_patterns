import re
from django import forms
from .models import CsvFile

# Note: CsvFile model no longer has a file field, it only stores metadata


class StockDataUploadForm(forms.Form):
    """Enhanced form for stock data CSV upload"""
    file = forms.FileField(
        label="Stock Data CSV File",
        help_text="Upload CSV file with filename format: YYYYMMDD_EXCHANGE.csv (e.g., 20250101_BSE.csv, 20251125_NSE.csv). Supported exchanges: BSE, NSE. Files are processed and removed to save space - only metadata is kept.",
        widget=forms.FileInput(attrs={
            'accept': '.csv',
            'class': 'form-control',
            'style': 'padding: 15px; border: 2px dashed #3498db; border-radius: 8px;'
        })
    )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        
        if not file:
            raise forms.ValidationError("Please select a file to upload.")
        
        # Check file extension
        if not file.name.lower().endswith('.csv'):
            raise forms.ValidationError("Only CSV files are allowed.")
        
        # Check file size (10MB limit)
        if file.size > 10 * 1024 * 1024:
            raise forms.ValidationError("File size cannot exceed 10MB.")
        
        # Validate filename pattern: YYYYMMDD_EXCHANGE.csv
        filename_pattern = r'^(\d{8})_([A-Z]+)\.csv$'
        match = re.match(filename_pattern, file.name, re.IGNORECASE)
        if not match:
            raise forms.ValidationError(
                "Filename must follow the pattern YYYYMMDD_EXCHANGE.csv "
                "(e.g., 20250101_BSE.csv, 20251125_NSE.csv). Supported exchanges: BSE, NSE"
            )
        
        # Validate date format
        date_str = match.group(1)
        try:
            from datetime import datetime
            datetime.strptime(date_str, '%Y%m%d')
        except ValueError:
            raise forms.ValidationError(f"Invalid date in filename: {date_str}")
        
        # Validate exchange name
        exchange = match.group(2)
        if len(exchange) > 10:
            raise forms.ValidationError(f"Exchange name too long (max 10 chars): {exchange}")
        
        return file


class FolderUploadForm(forms.Form):
    """Form for uploading multiple CSV files in a ZIP archive"""
    folder_zip = forms.FileField(
        label="CSV Files Folder (ZIP)",
        help_text="Upload a ZIP file containing CSV files with filename format: YYYYMMDD_EXCHANGE.csv. All CSV files in the ZIP will be processed. Maximum ZIP size: 50MB.",
        widget=forms.FileInput(attrs={
            'accept': '.zip',
            'class': 'form-control',
            'style': 'padding: 15px; border: 2px dashed #9b59b6; border-radius: 8px;'
        })
    )
    
    def clean_folder_zip(self):
        zip_file = self.cleaned_data.get('folder_zip')
        
        if not zip_file:
            raise forms.ValidationError("Please select a ZIP file to upload.")
        
        # Check file extension
        if not zip_file.name.lower().endswith('.zip'):
            raise forms.ValidationError("Only ZIP files are allowed.")
        
        # Check file size (50MB limit for ZIP)
        if zip_file.size > 50 * 1024 * 1024:
            raise forms.ValidationError("ZIP file size cannot exceed 50MB.")
        
        # Validate ZIP file content
        import zipfile
        import io
        
        try:
            zip_content = io.BytesIO(zip_file.read())
            with zipfile.ZipFile(zip_content, 'r') as zf:
                file_list = zf.namelist()
                
                # Check if there are any CSV files
                csv_files = [f for f in file_list if f.lower().endswith('.csv') and not f.startswith('__MACOSX/')]
                
                if not csv_files:
                    raise forms.ValidationError("No CSV files found in the ZIP archive.")
                
                # Validate filename patterns for CSV files
                filename_pattern = r'^.*?(\d{8})_([A-Z]+)\.csv$'
                invalid_files = []
                
                for csv_file in csv_files:
                    filename = csv_file.split('/')[-1]  # Get just the filename, not the path
                    if not re.match(filename_pattern, filename, re.IGNORECASE):
                        invalid_files.append(filename)
                
                if invalid_files:
                    if len(invalid_files) <= 3:
                        raise forms.ValidationError(
                            f"Invalid filename format: {', '.join(invalid_files)}. "
                            f"Files must follow pattern YYYYMMDD_EXCHANGE.csv"
                        )
                    else:
                        raise forms.ValidationError(
                            f"Invalid filename format for {len(invalid_files)} files (including: {', '.join(invalid_files[:3])}, ...). "
                            f"Files must follow pattern YYYYMMDD_EXCHANGE.csv"
                        )
                
                # Reset file pointer
                zip_file.seek(0)
                
        except zipfile.BadZipFile:
            raise forms.ValidationError("Invalid ZIP file format.")
        except Exception as e:
            raise forms.ValidationError(f"Error validating ZIP file: {str(e)}")
        
        return zip_file