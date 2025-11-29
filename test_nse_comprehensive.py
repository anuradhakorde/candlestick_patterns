#!/usr/bin/env python
"""Comprehensive test script for NSE CSV processing"""

import os
import sys
import tempfile
from datetime import datetime

# Add the project directory to Python path
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'candlestickpattern.settings')

import django
django.setup()

from csv_upload.csv_processor import CSVProcessor
from csv_upload.models import Stock, Candlestick


def test_nse_comprehensive():
    """Test NSE CSV processing with various scenarios"""
    processor = CSVProcessor()
    
    # Test 1: Complete NSE CSV
    print("=== Test 1: Complete NSE CSV ===")
    nse_data = """SYMBOL,SERIES,OPEN,HIGH,LOW,CLOSE,LAST,PREVCLOSE,TOTTRDQTY,TOTTRDVAL,TIMESTAMP,TOTALTRADES,ISIN
TCSTEST,EQ,3450.00,3475.50,3440.00,3465.75,3465.75,3450.00,750000,2599312500,01-JAN-2025,12000,INE467B01029
HDFCTEST,EQ,1580.00,1595.00,1575.00,1587.25,1587.25,1580.00,900000,1428525000,01-JAN-2025,18000,INE040A01034"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='_NSE.csv', delete=False) as f:
        f.write(nse_data)
        nse_file = f.name
    
    try:
        result = processor.process_csv_file(nse_file, '20250102_NSE.csv')
        print(f"Result: {result}")
        
        if result['success']:
            print(f"✅ NSE processing: {result['stocks_processed']} stocks, {result['candlesticks_processed']} candlesticks")
            
            # Verify the data was inserted correctly
            tcs_stock = Stock.objects.filter(stock_symbol='TCSTEST', stock_exchange='NSE').first()
            if tcs_stock:
                print(f"✅ TCS Stock created: {tcs_stock.stock_name} ({tcs_stock.stock_group})")
                
                candlestick = Candlestick.objects.filter(stock=tcs_stock).first()
                if candlestick:
                    print(f"✅ Candlestick data: O:{candlestick.open_price} H:{candlestick.high_price} L:{candlestick.low_price} C:{candlestick.close_price}")
                else:
                    print("❌ No candlestick data found")
            else:
                print("❌ TCS stock not found")
        else:
            print(f"❌ NSE processing failed: {result.get('error', 'Unknown error')}")
    
    finally:
        os.unlink(nse_file)
    
    # Test 2: Missing required columns
    print("\n=== Test 2: Missing Required Columns ===")
    nse_data_incomplete = """SYMBOL,SERIES,OPEN,HIGH,LOW
INCOMPLETETEST,EQ,1000.00,1010.00,990.00"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='_NSE.csv', delete=False) as f:
        f.write(nse_data_incomplete)
        nse_file = f.name
    
    try:
        result = processor.process_csv_file(nse_file, '20250102_NSE.csv')
        if not result['success']:
            print(f"✅ Correctly rejected incomplete NSE CSV: {result['error']}")
        else:
            print(f"❌ Should have failed with missing columns")
    
    finally:
        os.unlink(nse_file)
    
    # Test 3: Invalid data values
    print("\n=== Test 3: Invalid Data Values ===")
    nse_data_invalid = """SYMBOL,SERIES,OPEN,HIGH,LOW,CLOSE,LAST,PREVCLOSE,TOTTRDQTY,TOTTRDVAL,TIMESTAMP,TOTALTRADES,ISIN
INVALIDTEST,EQ,INVALID,3475.50,3440.00,3465.75,3465.75,3450.00,750000,2599312500,01-JAN-2025,12000,INE467B01029"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='_NSE.csv', delete=False) as f:
        f.write(nse_data_invalid)
        nse_file = f.name
    
    try:
        result = processor.process_csv_file(nse_file, '20250102_NSE.csv')
        print(f"Result with invalid data: success={result['success']}, errors={len(result.get('errors', []))}")
        if result.get('errors'):
            print(f"✅ Correctly captured error: {result['errors'][0]}")
        elif result.get('warnings'):
            print(f"✅ Correctly captured warning: {result['warnings'][0]}")
    
    finally:
        os.unlink(nse_file)


def test_field_mapping():
    """Test that NSE fields are mapped correctly to database fields"""
    print("\n=== Test 4: Field Mapping Verification ===")
    
    # Check that stock name is correctly mapped from SYMBOL for NSE
    tcs_stock = Stock.objects.filter(stock_symbol='TCSTEST', stock_exchange='NSE').first()
    if tcs_stock:
        if tcs_stock.stock_name == tcs_stock.stock_symbol:
            print("✅ NSE stock_name correctly mapped to SYMBOL")
        else:
            print(f"❌ NSE stock_name mapping incorrect: expected '{tcs_stock.stock_symbol}', got '{tcs_stock.stock_name}'")
        
        if tcs_stock.stock_group == 'EQ':
            print("✅ NSE stock_group correctly mapped to SERIES")
        else:
            print(f"❌ NSE stock_group mapping incorrect: expected 'EQ', got '{tcs_stock.stock_group}'")
    else:
        print("❌ TCS stock not found for field mapping test")


def test_extensibility():
    """Test the extensibility features for future exchanges"""
    print("\n=== Test 5: Extensibility Features ===")
    
    # Test adding a new exchange
    new_exchange_mapping = {
        'TICKER': 'stock_symbol',
        'NAME': 'stock_name',
        'SECTOR': 'stock_group',
        'O': 'open_price',
        'H': 'high_price',
        'L': 'low_price',
        'C': 'close_price',
        'PC': 'prev_close_price',
        'VOL': 'number_of_shares',
        'TRADES': 'number_of_trades',
        'VALUE': 'net_turnover'
    }
    
    # Add support for a hypothetical new exchange
    CSVProcessor.add_exchange_support('NEWEXCHANGE', new_exchange_mapping)
    
    supported = CSVProcessor.get_supported_exchanges()
    if 'NEWEXCHANGE' in supported:
        print("✅ Successfully added new exchange support")
        
        columns = CSVProcessor().get_exchange_columns('NEWEXCHANGE')
        expected_columns = list(new_exchange_mapping.keys())
        if set(columns) == set(expected_columns):
            print("✅ New exchange columns correctly configured")
        else:
            print(f"❌ New exchange columns mismatch: {columns} vs {expected_columns}")
    else:
        print("❌ Failed to add new exchange support")


if __name__ == '__main__':
    print("=== Comprehensive NSE Testing ===")
    test_nse_comprehensive()
    test_field_mapping()
    test_extensibility()
    print("\n=== NSE Tests Complete ===")