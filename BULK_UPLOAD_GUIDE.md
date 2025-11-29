# 📁 Folder Upload Feature - User Guide

## Overview
The CSV Upload system now supports both **single file** and **bulk folder** uploads to efficiently process multiple CSV files at once.

## 🎯 **Upload Methods**

### 1. Single File Upload 📄
- Upload individual CSV files
- Immediate processing and feedback
- Perfect for daily uploads

### 2. Bulk Folder Upload 📦
- Upload multiple CSV files in a ZIP archive
- Sequential processing of all CSV files
- Detailed per-file results and summary statistics
- Mixed BSE and NSE files supported in same ZIP

## 📋 **Requirements**

### Single File Upload
- **File Format**: `.csv`
- **Filename Pattern**: `YYYYMMDD_EXCHANGE.csv`
- **Max Size**: 10MB
- **Examples**: 
  - `20250126_BSE.csv`
  - `20250126_NSE.csv`

### Bulk Folder Upload
- **Archive Format**: `.zip`
- **Max ZIP Size**: 50MB
- **Content**: Multiple CSV files following the same naming pattern
- **Mixed Exchanges**: ZIP can contain both BSE and NSE files

## 🔄 **How to Use Bulk Upload**

### Step 1: Prepare Your Files
```
my_stock_data/
├── 20250101_BSE.csv
├── 20250101_NSE.csv
├── 20250102_BSE.csv
├── 20250102_NSE.csv
└── 20250103_BSE.csv
```

### Step 2: Create ZIP Archive
- Select all CSV files
- Create a ZIP archive (e.g., `stock_data_jan2025.zip`)
- Ensure ZIP is under 50MB

### Step 3: Upload via Web Interface
1. Go to **Upload Stock Data** page
2. Click **"Multiple Files (ZIP)"** tab
3. Select your ZIP file
4. Click **"Upload and Process ZIP"**

### Step 4: Review Results
- View detailed processing summary
- See per-file success/failure status
- Review any warnings or errors
- Access comprehensive statistics

## ✅ **Processing Results**

### Success Metrics
- **Total Files**: Number of CSV files found in ZIP
- **Successful**: Files processed without errors
- **Failed**: Files that couldn't be processed
- **Stocks Processed**: Total unique stocks added
- **Candlesticks**: Total candlestick records created

### Per-File Details
- ✅ **Successful Files**: Show filename, exchange, date, and processing counts
- ❌ **Failed Files**: Display filename and specific error reason
- ⚠️ **Warnings**: Individual file warnings (duplicates, data issues)

## 🛡️ **Error Handling**

### File-Level Validation
- **Filename Format**: Must follow `YYYYMMDD_EXCHANGE.csv` pattern
- **Exchange Support**: Only BSE and NSE currently supported
- **Column Validation**: Required columns checked per exchange type

### Data-Level Validation
- **Price Data**: Decimal validation for all price fields
- **Trade Data**: Integer validation for trade counts
- **Date Validation**: Date format and logic validation
- **Duplicate Prevention**: Prevents duplicate stock/candlestick entries

### ZIP-Level Validation
- **Archive Integrity**: Valid ZIP file structure
- **Content Check**: Must contain at least one CSV file
- **Size Limits**: ZIP under 50MB, individual CSVs under 10MB

## 📊 **Supported CSV Formats**

### BSE Format
```csv
SC_CODE,SC_NAME,SC_GROUP,SC_TYPE,OPEN,HIGH,LOW,CLOSE,LAST,PREVCLOSE,NO_TRADES,NO_OF_SHRS,NET_TURNOV,TDCLOINDI
500325,RELIANCE,A,EQ,2450.00,2485.50,2440.00,2475.75,2475.75,2450.00,25000,1250000,3087500000,N
```

### NSE Format
```csv
SYMBOL,SERIES,OPEN,HIGH,LOW,CLOSE,LAST,PREVCLOSE,TOTTRDQTY,TOTTRDVAL,TIMESTAMP,TOTALTRADES,ISIN
RELIANCE,EQ,2450.00,2485.50,2440.00,2475.75,2475.75,2450.00,1250000,3087500000,26-JAN-2025,25000,INE002A01018
```

## 🔧 **Technical Features**

### Performance Optimizations
- **Sequential Processing**: Files processed one at a time for memory efficiency
- **Temporary Storage**: ZIP extracted to temp directory, cleaned up automatically
- **Database Transactions**: Each file processed in its own transaction
- **Error Isolation**: One file failure doesn't affect others

### Space Management
- **No File Storage**: CSV files are processed and immediately deleted
- **Metadata Only**: Only filename, date, exchange, and statistics stored
- **ZIP Cleanup**: Uploaded ZIP files are not stored permanently
- **Temp Cleanup**: All temporary files automatically removed

### Security Features
- **ZIP Bomb Protection**: File size limits and content validation
- **Path Traversal Prevention**: Safe extraction to temporary directories
- **Content Validation**: Only CSV files processed, others ignored
- **Exchange Validation**: Only supported exchanges accepted

## 🚨 **Common Issues and Solutions**

### Issue: "No CSV files found in ZIP"
**Solution**: Ensure ZIP contains CSV files with correct extensions (not nested in folders)

### Issue: "Invalid filename format"
**Solution**: Rename files to follow `YYYYMMDD_EXCHANGE.csv` pattern exactly

### Issue: "Unsupported exchange"
**Solution**: Currently only BSE and NSE are supported. Check filename has correct exchange name

### Issue: "Missing required columns"
**Solution**: Verify CSV has all required columns for the specific exchange format

### Issue: "ZIP file too large"
**Solution**: Split into smaller ZIP files (under 50MB each) or compress better

## 📈 **Best Practices**

1. **Organize Files**: Keep files organized by date/exchange before zipping
2. **Test Small Batches**: Try with few files first to validate format
3. **Check Results**: Always review the results page for any issues
4. **Mixed Uploads**: You can mix BSE and NSE files in same ZIP
5. **Regular Backups**: Keep backup of source files since uploads are not stored

## 🔮 **Future Enhancements**

- Support for additional exchanges (NASDAQ, etc.)
- Progress indicators for large uploads
- Email notifications for bulk upload completion
- Scheduled/automated bulk uploads
- Advanced filtering and data transformation options

---

The bulk upload feature makes it easy to process large amounts of historical stock data efficiently while maintaining data integrity and providing comprehensive feedback on the processing results.