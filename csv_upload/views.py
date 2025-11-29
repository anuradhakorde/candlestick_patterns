import os
import tempfile
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import default_storage
from .forms import StockDataUploadForm, FolderUploadForm
from .models import CsvFile, Stock, Candlestick
from .csv_processor import CSVProcessor
from .bulk_processor import BulkCSVProcessor


def upload_csv(request):
    """View to handle stock data CSV file upload with processing."""
    if request.method == 'POST':
        # Determine which form was submitted
        if 'single_file_submit' in request.POST:
            return _handle_single_file_upload(request)
        elif 'folder_submit' in request.POST:
            return _handle_folder_upload(request)
        else:
            messages.error(request, "❌ Invalid upload type.")
            return redirect('csv_upload:upload_csv')
    else:
        single_form = StockDataUploadForm()
        folder_form = FolderUploadForm()

    return render(request, 'csv_upload/upload_csv_new.html', {
        'single_form': single_form,
        'folder_form': folder_form
    })


def _handle_single_file_upload(request):
    """Handle single CSV file upload"""
    form = StockDataUploadForm(request.POST, request.FILES)
    if form.is_valid():
        try:
            uploaded_file = request.FILES['file']
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            # Process the CSV file
            processor = CSVProcessor()
            result = processor.process_csv_file(temp_file_path, uploaded_file.name)
            
            # Clean up temporary file immediately
            os.unlink(temp_file_path)
            
            if result['success']:
                # Save file record for tracking (metadata only, no actual file)
                csv_file = CsvFile.objects.create(
                    filename=uploaded_file.name,
                    date=result['date'],
                    exchange=result['exchange'],
                    stocks_processed=result['stocks_processed'],
                    candlesticks_processed=result['candlesticks_processed']
                )
                
                # Add success message
                messages.success(
                    request, 
                    f"✅ Successfully processed {uploaded_file.name}! "
                    f"Processed {result['stocks_processed']} stocks and "
                    f"{result['candlesticks_processed']} candlestick records for "
                    f"{result['exchange']} exchange on {result['date']}. "
                    f"📁 File processed and removed to save space."
                )
                
                # Add warnings if any
                if result['warnings']:
                    for warning in result['warnings'][:5]:  # Show first 5 warnings
                        messages.warning(request, f"⚠️ {warning}")
                    if len(result['warnings']) > 5:
                        messages.warning(
                            request, 
                            f"⚠️ And {len(result['warnings']) - 5} more warnings..."
                        )
                
                # Store results in session for results page (convert date to string)
                session_result = result.copy()
                session_result['date'] = result['date'].strftime('%Y-%m-%d')
                session_result['filename'] = uploaded_file.name
                session_result['upload_type'] = 'single'
                request.session['upload_result'] = session_result
                return redirect('csv_upload:upload_result')
            
            else:
                # Process failed
                messages.error(
                    request, 
                    f"❌ Failed to process {uploaded_file.name}: {result['error']}"
                )
                
                # Add specific errors
                if result['errors']:
                    for error in result['errors'][:3]:  # Show first 3 errors
                        messages.error(request, f"❌ {error}")
                    if len(result['errors']) > 3:
                        messages.error(
                            request, 
                            f"❌ And {len(result['errors']) - 3} more errors..."
                        )
                
        except Exception as e:
            # Clean up temp file if it exists
            if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            messages.error(request, f"❌ Unexpected error: {str(e)}")
    else:
        # Form validation errors
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"❌ {error}")
    
    # Return to upload page with errors
    folder_form = FolderUploadForm()
    return render(request, 'csv_upload/upload_csv_new.html', {
        'single_form': form,
        'folder_form': folder_form
    })


def _handle_folder_upload(request):
    """Handle folder (ZIP) upload with multiple CSV files"""
    form = FolderUploadForm(request.POST, request.FILES)
    if form.is_valid():
        try:
            uploaded_zip = request.FILES['folder_zip']
            
            # Process the ZIP file
            bulk_processor = BulkCSVProcessor()
            result = bulk_processor.process_zip_file(uploaded_zip)
            
            if result['success']:
                # Add success message with summary
                messages.success(
                    request, 
                    f"✅ Successfully processed ZIP file {uploaded_zip.name}! "
                    f"Processed {result['total_files_processed']} files successfully "
                    f"({result['total_files_failed']} failed). "
                    f"Total: {result['total_stocks']} stocks, {result['total_candlesticks']} candlesticks. "
                    f"📁 All files processed and removed to save space."
                )
                
                # Add warnings for failed files
                if result['failed_files']:
                    messages.warning(
                        request,
                        f"⚠️ {len(result['failed_files'])} files failed to process. Check details below."
                    )
                
                # Store results in session for results page
                session_result = result.copy()
                session_result['filename'] = uploaded_zip.name
                session_result['upload_type'] = 'folder'
                
                # Convert dates to strings for session storage
                for file_info in session_result.get('processed_files', []):
                    if 'date' in file_info:
                        file_info['date'] = file_info['date'].strftime('%Y-%m-%d')
                
                request.session['upload_result'] = session_result
                return redirect('csv_upload:upload_result')
            
            else:
                # Process failed
                messages.error(
                    request, 
                    f"❌ Failed to process ZIP file {uploaded_zip.name}: {result['error']}"
                )
                
                # Add specific errors
                if result['errors']:
                    for error in result['errors'][:5]:  # Show first 5 errors
                        messages.error(request, f"❌ {error}")
                    if len(result['errors']) > 5:
                        messages.error(
                            request, 
                            f"❌ And {len(result['errors']) - 5} more errors..."
                        )
                
        except Exception as e:
            messages.error(request, f"❌ Unexpected error processing ZIP: {str(e)}")
    else:
        # Form validation errors
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"❌ {error}")
    
    # Return to upload page with errors
    single_form = StockDataUploadForm()
    return render(request, 'csv_upload/upload_csv_new.html', {
        'single_form': single_form,
        'folder_form': form
    })


def upload_result(request):
    """Display detailed upload results for both single and bulk uploads"""
    result = request.session.get('upload_result')
    if not result:
        messages.warning(request, "No upload result found.")
        return redirect('csv_upload:upload_csv')
    
    # Clear session data
    del request.session['upload_result']
    
    # Determine template based on upload type
    upload_type = result.get('upload_type', 'single')
    
    if upload_type == 'folder':
        return render(request, 'csv_upload/bulk_upload_result.html', {'result': result})
    else:
        return render(request, 'csv_upload/upload_result.html', {'result': result})


def csv_list(request):
    """View to list all uploaded CSV files with statistics."""
    csv_files = CsvFile.objects.all().order_by('-upload_timestamp')
    
    # Get statistics
    total_stocks = Stock.objects.count()
    total_candlesticks = Candlestick.objects.count()
    total_exchanges = Stock.objects.values('stock_exchange').distinct().count()
    
    # Get recent activity
    recent_candlesticks = Candlestick.objects.select_related('stock').order_by('-candle_date')[:10]
    
    # Get upload statistics
    total_files_uploaded = csv_files.count()
    total_stocks_from_uploads = sum(csv_file.stocks_processed for csv_file in csv_files)
    total_candlesticks_from_uploads = sum(csv_file.candlesticks_processed for csv_file in csv_files)
    
    context = {
        'csv_files': csv_files,
        'stats': {
            'total_stocks': total_stocks,
            'total_candlesticks': total_candlesticks,
            'total_exchanges': total_exchanges,
            'total_files': total_files_uploaded,
            'total_stocks_uploaded': total_stocks_from_uploads,
            'total_candlesticks_uploaded': total_candlesticks_from_uploads
        },
        'recent_candlesticks': recent_candlesticks
    }
    
    return render(request, 'csv_upload/csv_list.html', context)


def stock_detail(request, stock_id):
    """View to show details of a specific stock"""
    try:
        stock = Stock.objects.get(stock_id=stock_id)
        candlesticks = Candlestick.objects.filter(stock=stock).order_by('-candle_date')[:50]
        
        context = {
            'stock': stock,
            'candlesticks': candlesticks,
            'total_records': Candlestick.objects.filter(stock=stock).count()
        }
        
        return render(request, 'csv_upload/stock_detail.html', context)
        
    except Stock.DoesNotExist:
        messages.error(request, "Stock not found.")
        return redirect('csv_upload:csv_list')