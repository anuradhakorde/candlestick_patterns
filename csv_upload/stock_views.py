from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Stock, Candlestick
from .stock_forms import StockForm, CandlestickForm, StockFilterForm, CandlestickFilterForm


def staff_required(user):
    """Check if user is staff or superuser"""
    return user.is_staff or user.is_superuser


# ========== STOCK CRUD VIEWS ==========

@login_required
@user_passes_test(staff_required)
def stock_list(request):
    """List all stocks with search and filtering"""
    form = StockFilterForm(request.GET)
    stocks = Stock.objects.all()
    
    # Apply filters
    if form.is_valid():
        search = form.cleaned_data.get('search')
        exchange = form.cleaned_data.get('exchange')
        group = form.cleaned_data.get('group')
        
        if search:
            stocks = stocks.filter(
                Q(stock_symbol__icontains=search) |
                Q(stock_name__icontains=search)
            )
        
        if exchange:
            stocks = stocks.filter(stock_exchange__icontains=exchange)
        
        if group:
            stocks = stocks.filter(stock_group__icontains=group)
    
    # Add candlestick counts
    stocks = stocks.annotate(candlestick_count=Count('candlestick'))
    stocks = stocks.order_by('stock_exchange', 'stock_symbol')
    
    # Pagination
    paginator = Paginator(stocks, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    stats = {
        'total_stocks': Stock.objects.count(),
        'total_exchanges': Stock.objects.values('stock_exchange').distinct().count(),
        'total_candlesticks': Candlestick.objects.count(),
        'filtered_count': stocks.count()
    }
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'stats': stats,
        'is_filtered': any([
            request.GET.get('search'),
            request.GET.get('exchange'),
            request.GET.get('group')
        ])
    }
    
    return render(request, 'csv_upload/stock_list.html', context)


@login_required
@user_passes_test(staff_required)
def stock_detail(request, stock_id):
    """View details of a specific stock"""
    stock = get_object_or_404(Stock, stock_id=stock_id)
    
    # Get recent candlestick data
    candlesticks = Candlestick.objects.filter(stock=stock).order_by('-candle_date')[:50]
    
    # Calculate statistics
    total_candlesticks = Candlestick.objects.filter(stock=stock).count()
    
    # Get price range if candlesticks exist
    price_stats = None
    if candlesticks.exists():
        all_candlesticks = Candlestick.objects.filter(stock=stock)
        price_stats = {
            'highest_price': max(c.high_price for c in all_candlesticks),
            'lowest_price': min(c.low_price for c in all_candlesticks),
            'latest_close': candlesticks.first().close_price if candlesticks else None,
            'date_range': {
                'from': all_candlesticks.order_by('candle_date').first().candle_date.date(),
                'to': all_candlesticks.order_by('-candle_date').first().candle_date.date()
            }
        }
    
    context = {
        'stock': stock,
        'candlesticks': candlesticks,
        'total_candlesticks': total_candlesticks,
        'price_stats': price_stats
    }
    
    return render(request, 'csv_upload/stock_detail.html', context)


@login_required
@user_passes_test(staff_required)
def stock_create(request):
    """Create a new stock"""
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save()
            messages.success(
                request, 
                f'✅ Stock {stock.stock_symbol} created successfully!'
            )
            return redirect('csv_upload:stock_detail', stock_id=stock.stock_id)
    else:
        form = StockForm()
    
    context = {
        'form': form,
        'title': 'Create New Stock',
        'submit_text': 'Create Stock'
    }
    
    return render(request, 'csv_upload/stock_form.html', context)


@login_required
@user_passes_test(staff_required)
def stock_edit(request, stock_id):
    """Edit an existing stock"""
    stock = get_object_or_404(Stock, stock_id=stock_id)
    
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            stock = form.save()
            messages.success(
                request, 
                f'✅ Stock {stock.stock_symbol} updated successfully!'
            )
            return redirect('csv_upload:stock_detail', stock_id=stock.stock_id)
    else:
        form = StockForm(instance=stock)
    
    context = {
        'form': form,
        'stock': stock,
        'title': f'Edit {stock.stock_symbol}',
        'submit_text': 'Update Stock'
    }
    
    return render(request, 'csv_upload/stock_form.html', context)


@login_required
@user_passes_test(staff_required)
def stock_delete(request, stock_id):
    """Delete a stock"""
    stock = get_object_or_404(Stock, stock_id=stock_id)
    
    if request.method == 'POST':
        symbol = stock.stock_symbol
        candlestick_count = Candlestick.objects.filter(stock=stock).count()
        stock.delete()
        messages.success(
            request, 
            f'🗑️ Stock {symbol} and {candlestick_count} related candlestick records deleted successfully!'
        )
        return redirect('csv_upload:stock_list')
    
    # Get related data count
    candlestick_count = Candlestick.objects.filter(stock=stock).count()
    
    context = {
        'stock': stock,
        'candlestick_count': candlestick_count
    }
    
    return render(request, 'csv_upload/stock_delete.html', context)


# ========== CANDLESTICK CRUD VIEWS ==========

@login_required
@user_passes_test(staff_required)
def candlestick_list(request):
    """List all candlesticks with filtering"""
    form = CandlestickFilterForm(request.GET)
    candlesticks = Candlestick.objects.select_related('stock').all()
    
    # Apply filters
    if form.is_valid():
        stock = form.cleaned_data.get('stock')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        exchange = form.cleaned_data.get('exchange')
        
        if stock:
            candlesticks = candlesticks.filter(stock=stock)
        
        if date_from:
            candlesticks = candlesticks.filter(candle_date__date__gte=date_from)
        
        if date_to:
            candlesticks = candlesticks.filter(candle_date__date__lte=date_to)
        
        if exchange:
            candlesticks = candlesticks.filter(stock__stock_exchange__icontains=exchange)
    
    candlesticks = candlesticks.order_by('-candle_date', 'stock__stock_symbol')
    
    # Pagination
    paginator = Paginator(candlesticks, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics
    stats = {
        'total_candlesticks': Candlestick.objects.count(),
        'total_stocks': Stock.objects.count(),
        'filtered_count': candlesticks.count()
    }
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'stats': stats,
        'is_filtered': any([
            request.GET.get('stock'),
            request.GET.get('date_from'),
            request.GET.get('date_to'),
            request.GET.get('exchange')
        ])
    }
    
    return render(request, 'csv_upload/candlestick_list.html', context)


@login_required
@user_passes_test(staff_required)
def candlestick_detail(request, candle_id):
    """View details of a specific candlestick"""
    candlestick = get_object_or_404(Candlestick, candle_id=candle_id)
    
    # Get neighboring candlesticks for the same stock
    prev_candlestick = Candlestick.objects.filter(
        stock=candlestick.stock,
        candle_date__lt=candlestick.candle_date
    ).order_by('-candle_date').first()
    
    next_candlestick = Candlestick.objects.filter(
        stock=candlestick.stock,
        candle_date__gt=candlestick.candle_date
    ).order_by('candle_date').first()
    
    # Calculate price changes
    price_change = None
    price_change_pct = None
    if prev_candlestick:
        price_change = candlestick.close_price - prev_candlestick.close_price
        if prev_candlestick.close_price > 0:
            price_change_pct = (price_change / prev_candlestick.close_price) * 100
    
    context = {
        'candlestick': candlestick,
        'prev_candlestick': prev_candlestick,
        'next_candlestick': next_candlestick,
        'price_change': price_change,
        'price_change_pct': price_change_pct
    }
    
    return render(request, 'csv_upload/candlestick_detail.html', context)


@login_required
@user_passes_test(staff_required)
def candlestick_create(request):
    """Create a new candlestick"""
    if request.method == 'POST':
        form = CandlestickForm(request.POST)
        if form.is_valid():
            candlestick = form.save()
            messages.success(
                request, 
                f'✅ Candlestick data for {candlestick.stock.stock_symbol} on {candlestick.candle_date.date()} created successfully!'
            )
            return redirect('csv_upload:candlestick_detail', candle_id=candlestick.candle_id)
    else:
        form = CandlestickForm()
    
    context = {
        'form': form,
        'title': 'Create New Candlestick Data',
        'submit_text': 'Create Candlestick'
    }
    
    return render(request, 'csv_upload/candlestick_form.html', context)


@login_required
@user_passes_test(staff_required)
def candlestick_edit(request, candle_id):
    """Edit an existing candlestick"""
    candlestick = get_object_or_404(Candlestick, candle_id=candle_id)
    
    if request.method == 'POST':
        form = CandlestickForm(request.POST, instance=candlestick)
        if form.is_valid():
            candlestick = form.save()
            messages.success(
                request, 
                f'✅ Candlestick data for {candlestick.stock.stock_symbol} updated successfully!'
            )
            return redirect('csv_upload:candlestick_detail', candle_id=candlestick.candle_id)
    else:
        form = CandlestickForm(instance=candlestick)
    
    context = {
        'form': form,
        'candlestick': candlestick,
        'title': f'Edit {candlestick.stock.stock_symbol} - {candlestick.candle_date.date()}',
        'submit_text': 'Update Candlestick'
    }
    
    return render(request, 'csv_upload/candlestick_form.html', context)


@login_required
@user_passes_test(staff_required)
def candlestick_delete(request, candle_id):
    """Delete a candlestick"""
    candlestick = get_object_or_404(Candlestick, candle_id=candle_id)
    
    if request.method == 'POST':
        symbol = candlestick.stock.stock_symbol
        date = candlestick.candle_date.date()
        candlestick.delete()
        messages.success(
            request, 
            f'🗑️ Candlestick data for {symbol} on {date} deleted successfully!'
        )
        return redirect('csv_upload:candlestick_list')
    
    context = {
        'candlestick': candlestick
    }
    
    return render(request, 'csv_upload/candlestick_delete.html', context)


# ========== AJAX VIEWS ==========

@require_http_methods(["GET"])
def stock_search_ajax(request):
    """AJAX endpoint for stock search"""
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'stocks': []})
    
    stocks = Stock.objects.filter(
        Q(stock_symbol__icontains=query) |
        Q(stock_name__icontains=query)
    ).order_by('stock_symbol')[:10]
    
    stock_data = [
        {
            'id': stock.stock_id,
            'symbol': stock.stock_symbol,
            'name': stock.stock_name,
            'exchange': stock.stock_exchange,
            'text': f"{stock.stock_symbol} - {stock.stock_name} ({stock.stock_exchange})"
        }
        for stock in stocks
    ]
    
    return JsonResponse({'stocks': stock_data})