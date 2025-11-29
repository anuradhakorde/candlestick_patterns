#!/usr/bin/env python
"""Test script for bulk CSV upload functionality"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'candlestickpattern.settings')
django.setup()

from csv_upload.bulk_processor import BulkCSVProcessor
from django.core.files.uploadedfile import SimpleUploadedFile

def test_bulk_upload():
    """Test bulk processor with our test ZIP"""
    processor = BulkCSVProcessor()

    # Read the ZIP file
    with open('test_bulk_upload.zip', 'rb') as f:
        zip_content = f.read()

    # Create a simulated uploaded file
    uploaded_zip = SimpleUploadedFile('test_bulk_upload.zip', zip_content, content_type='application/zip')

    # Process the ZIP file
    result = processor.process_zip_file(uploaded_zip)

    print('=== Bulk Upload Test Results ===')
    print(f'Success: {result["success"]}')
    print(f'Total files processed: {result["total_files_processed"]}')
    print(f'Total files failed: {result.get("total_files_failed", 0)}')
    print(f'Total stocks: {result["total_stocks"]}')
    print(f'Total candlesticks: {result["total_candlesticks"]}')

    print('\n--- Processed Files ---')
    for file_info in result.get('processed_files', []):
        print(f'{file_info["filename"]}: {file_info["stocks_processed"]} stocks, {file_info["candlesticks_processed"]} candlesticks ({file_info["exchange"]})')

    print('\n--- Failed Files ---')
    for file_info in result.get('failed_files', []):
        print(f'{file_info["filename"]}: {file_info["error"]}')

    if result.get('errors'):
        print('\n--- Errors ---')
        for error in result['errors'][:5]:
            print(f'- {error}')

if __name__ == '__main__':
    test_bulk_upload()