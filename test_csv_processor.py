#!/usr/bin/env python
"""Test script to verify CSV processor functionality for both BSE and NSE exchanges"""

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


def test_filename_parsing():
    """Test filename parsing for both exchanges"""
    processor = CSVProcessor()
    
    # Test BSE filename
    try:
        date, exchange = processor.parse_filename('20250101_BSE.csv')
        print(f"✅ BSE filename parsing: {date} | {exchange}")
        assert exchange == 'BSE'
        assert date == datetime(2025, 1, 1).date()
    except Exception as e:
        print(f"❌ BSE filename parsing failed: {e}")
    
    # Test NSE filename
    try:
        date, exchange = processor.parse_filename('20250101_NSE.csv')
        print(f"✅ NSE filename parsing: {date} | {exchange}")
        assert exchange == 'NSE'
        assert date == datetime(2025, 1, 1).date()
    except Exception as e:
        print(f"❌ NSE filename parsing failed: {e}")
    
    # Test unsupported exchange
    try:
        date, exchange = processor.parse_filename('20250101_NASDAQ.csv')
        print(f"❌ Should have failed for NASDAQ: {exchange}")
    except ValueError as e:
        print(f"✅ Correctly rejected NASDAQ: {e}")
    
    # Test invalid filename format
    try:
        date, exchange = processor.parse_filename('invalid_format.csv')
        print(f"❌ Should have failed for invalid format")
    except ValueError as e:
        print(f"✅ Correctly rejected invalid format: {e}")


def test_exchange_mappings():
    """Test exchange column mappings"""
    processor = CSVProcessor()
    
    # Test BSE mapping
    bse_columns = processor.get_exchange_columns('BSE')
    print(f"✅ BSE columns: {bse_columns}")
    expected_bse = ['SC_CODE', 'SC_NAME', 'SC_GROUP', 'SC_TYPE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'LAST', 'PREVCLOSE', 'NO_TRADES', 'NO_OF_SHRS', 'NET_TURNOV', 'TDCLOINDI']
    assert set(bse_columns) == set(expected_bse), f"BSE columns mismatch: {set(bse_columns)} != {set(expected_bse)}"
    
    # Test NSE mapping
    nse_columns = processor.get_exchange_columns('NSE')
    print(f"✅ NSE columns: {nse_columns}")
    expected_nse = ['SYMBOL', 'SERIES', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'LAST', 'PREVCLOSE', 'TOTTRDQTY', 'TOTTRDVAL', 'TIMESTAMP', 'TOTALTRADES', 'ISIN']
    assert set(nse_columns) == set(expected_nse), f"NSE columns mismatch: {set(nse_columns)} != {set(expected_nse)}"


def test_bse_csv_creation():
    """Create a sample BSE CSV file for testing"""
    bse_data = """SC_CODE,SC_NAME,SC_GROUP,SC_TYPE,OPEN,HIGH,LOW,CLOSE,LAST,PREVCLOSE,NO_TRADES,NO_OF_SHRS,NET_TURNOV,TDCLOINDI
500325,RELIANCE,A,EQ,2450.00,2475.50,2440.00,2465.75,2465.75,2450.00,15000,1000000,2465750000,N
500034,BAJFINANCE,A,EQ,6800.00,6850.00,6780.00,6825.50,6825.50,6800.00,8500,500000,3412750000,N"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='_BSE.csv', delete=False) as f:
        f.write(bse_data)
        return f.name


def test_nse_csv_creation():
    """Create a sample NSE CSV file for testing"""
    nse_data = """SYMBOL,SERIES,OPEN,HIGH,LOW,CLOSE,LAST,PREVCLOSE,TOTTRDQTY,TOTTRDVAL,TIMESTAMP,TOTALTRADES,ISIN
RELIANCE,EQ,2450.00,2475.50,2440.00,2465.75,2465.75,2450.00,1000000,2465750000,01-JAN-2025,15000,INE002A01018
BAJFINANCE,EQ,6800.00,6850.00,6780.00,6825.50,6825.50,6800.00,500000,3412750000,01-JAN-2025,8500,INE296A01024"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='_NSE.csv', delete=False) as f:
        f.write(nse_data)
        return f.name


def test_csv_processing():
    """Test actual CSV processing for both exchanges"""
    processor = CSVProcessor()
    
    # Test BSE processing
    print("\n=== Testing BSE CSV Processing ===")
    try:
        bse_file = test_bse_csv_creation()
        result = processor.process_csv_file(bse_file, '20250101_BSE.csv')
        print(f"BSE Result: {result}")
        
        if result['success']:
            print(f"✅ BSE processing successful: {result['stocks_processed']} stocks, {result['candlesticks_processed']} candlesticks")
        else:
            print(f"❌ BSE processing failed: {result.get('error', 'Unknown error')}")
        
        os.unlink(bse_file)
    except Exception as e:
        print(f"❌ BSE test failed with exception: {e}")
    
    # Test NSE processing
    print("\n=== Testing NSE CSV Processing ===")
    try:
        nse_file = test_nse_csv_creation()
        result = processor.process_csv_file(nse_file, '20250101_NSE.csv')
        print(f"NSE Result: {result}")
        
        if result['success']:
            print(f"✅ NSE processing successful: {result['stocks_processed']} stocks, {result['candlesticks_processed']} candlesticks")
        else:
            print(f"❌ NSE processing failed: {result.get('error', 'Unknown error')}")
            if result.get('errors'):
                for error in result['errors']:
                    print(f"  Error: {error}")
        
        os.unlink(nse_file)
    except Exception as e:
        print(f"❌ NSE test failed with exception: {e}")


if __name__ == '__main__':
    print("=== CSV Processor Tests ===")
    print(f"Supported exchanges: {CSVProcessor.get_supported_exchanges()}")
    
    print("\n1. Testing filename parsing...")
    test_filename_parsing()
    
    print("\n2. Testing exchange mappings...")
    test_exchange_mappings()
    
    print("\n3. Testing CSV processing...")
    test_csv_processing()
    
    print("\n=== Tests Complete ===")