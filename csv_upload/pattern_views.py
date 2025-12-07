from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime, timedelta
import json
import logging

from csv_upload.pattern_forms import PatternAnalysisForm, QuickPatternSearchForm
from csv_upload.pattern_detector import PatternAnalysisService
from csv_upload.models import Stock, Candlestick

# Configure logger for pattern analysis
logger = logging.getLogger('pattern_analysis')


def pattern_analysis_home(request):
    """
    Main pattern analysis page with form selection
    """
    form = PatternAnalysisForm()
    quick_form = QuickPatternSearchForm()
    
    context = {
        'form': form,
        'quick_form': quick_form,
        'total_stocks': Stock.objects.count(),
        'available_patterns': PatternAnalysisService.AVAILABLE_PATTERNS
    }
    
    return render(request, 'csv_upload/pattern_analysis.html', context)


def pattern_analysis_results(request):
    """
    Process pattern analysis form and show results
    """
    if request.method != 'POST':
        return redirect('csv_upload:pattern_analysis_home')
    
    form = PatternAnalysisForm(request.POST)
    
    if not form.is_valid():
        messages.error(request, "Please correct the errors in the form.")
        quick_form = QuickPatternSearchForm()
        context = {
            'form': form,
            'quick_form': quick_form,
            'total_stocks': Stock.objects.count(),
            'available_patterns': PatternAnalysisService.AVAILABLE_PATTERNS
        }
        return render(request, 'csv_upload/pattern_analysis.html', context)
    
    # Extract form data
    patterns = form.cleaned_data['patterns']
    stocks = form.cleaned_data['stocks']
    date_from = form.cleaned_data.get('date_from')
    date_to = form.cleaned_data.get('date_to')
    
    # Convert stocks queryset to list of IDs and symbols for logging
    stock_ids = [stock.stock_id for stock in stocks]
    stock_symbols = [stock.stock_symbol for stock in stocks]
    
    # Log the pattern search parameters
    logger.info(f"🔍 PATTERN ANALYSIS SEARCH:")
    logger.info(f"  📊 Patterns: {', '.join(patterns)}")
    logger.info(f"  🏢 Stocks ({len(stocks)}): {', '.join(stock_symbols[:10])}{'...' if len(stock_symbols) > 10 else ''}")
    logger.info(f"  📅 Date Range: {date_from or 'All time'} to {date_to or 'Present'}")
    logger.info(f"  🔢 Stock IDs: {stock_ids[:5]}{'...' if len(stock_ids) > 5 else ''}")
    
    try:
        # Perform pattern analysis
        analysis_results = PatternAnalysisService.analyze_patterns(
            pattern_types=patterns,
            stock_ids=stock_ids,
            date_from=date_from,
            date_to=date_to
        )
        
        # Log the analysis results
        logger.info(f"✅ PATTERN ANALYSIS RESULTS:")
        logger.info(f"  📈 Total patterns found: {analysis_results['total_patterns']}")
        logger.info(f"  🎯 Stocks analyzed: {analysis_results['stocks_analyzed']}")
        patterns_by_stock = analysis_results['patterns_found']
        for stock_symbol, stock_patterns in patterns_by_stock.items():
            pattern_counts = {pattern_type: len(instances) for pattern_type, instances in stock_patterns.items()}
            logger.info(f"  📊 {stock_symbol}: {pattern_counts}")
        
        # Prepare chart data for each stock with patterns
        chart_data = prepare_chart_data(analysis_results['patterns_found'])
        
        # Get stock details for display
        stock_details = {
            stock.stock_id: {
                'symbol': stock.stock_symbol,
                'name': stock.stock_name or stock.stock_symbol,
                'exchange': stock.stock_exchange
            }
            for stock in stocks
        }
        
        context = {
            'analysis_results': analysis_results,
            'chart_data': chart_data,
            'selected_patterns': patterns,
            'selected_stocks': stocks,
            'stock_details': stock_details,
            'available_patterns': PatternAnalysisService.AVAILABLE_PATTERNS,
            'date_range': {
                'from': date_from,
                'to': date_to
            }
        }
        
        return render(request, 'csv_upload/pattern_results.html', context)
        
    except Exception as e:
        logger.error(f"❌ ERROR during pattern analysis: {str(e)}")
        logger.error(f"  📊 Attempted patterns: {patterns}")
        logger.error(f"  🏢 Attempted stocks: {[s.stock_symbol for s in stocks]}")
        logger.error(f"  📅 Date range: {date_from} to {date_to}")
        messages.error(request, f"Error during pattern analysis: {str(e)}")
        return redirect('csv_upload:pattern_analysis_home')


def quick_pattern_search(request):
    """
    Handle quick pattern search for single stock
    """
    if request.method != 'POST':
        return redirect('csv_upload:pattern_analysis_home')
    
    quick_form = QuickPatternSearchForm(request.POST)
    
    if not quick_form.is_valid():
        messages.error(request, "Please check your search parameters.")
        return redirect('csv_upload:pattern_analysis_home')
    
    pattern = quick_form.cleaned_data['pattern']
    stock_symbol = quick_form.cleaned_data['stock_symbol']
    days_back = int(quick_form.cleaned_data['days_back'])
    
    # Log quick search parameters
    logger.info(f"⚡ QUICK PATTERN SEARCH:")
    logger.info(f"  📊 Pattern: {pattern}")
    logger.info(f"  🏢 Stock: {stock_symbol}")
    logger.info(f"  📅 Time Period: Last {days_back} days")
    
    try:
        # Get stock
        stock = Stock.objects.get(stock_symbol__iexact=stock_symbol)
        
        # Calculate date range
        date_to = datetime.now().date()
        date_from = date_to - timedelta(days=days_back)
        
        logger.info(f"  📅 Date Range: {date_from} to {date_to}")
        logger.info(f"  🔢 Stock ID: {stock.stock_id} ({stock.stock_name})")
        
        # Perform analysis
        analysis_results = PatternAnalysisService.analyze_patterns(
            pattern_types=[pattern],
            stock_ids=[stock.stock_id],
            date_from=date_from,
            date_to=date_to
        )
        
        # Prepare chart data
        chart_data = prepare_chart_data(analysis_results['patterns_found'])
        
        context = {
            'analysis_results': analysis_results,
            'chart_data': chart_data,
            'selected_patterns': [pattern],
            'selected_stocks': [stock],
            'stock_details': {
                stock.stock_id: {
                    'symbol': stock.stock_symbol,
                    'name': stock.stock_name or stock.stock_symbol,
                    'exchange': stock.stock_exchange
                }
            },
            'available_patterns': PatternAnalysisService.AVAILABLE_PATTERNS,
            'is_quick_search': True,
            'date_range': {
                'from': date_from,
                'to': date_to
            }
        }
        
        return render(request, 'csv_upload/pattern_results.html', context)
        
    except Stock.DoesNotExist:
        logger.error(f"❌ Stock not found: {stock_symbol}")
        messages.error(request, f"Stock symbol '{stock_symbol}' not found.")
        return redirect('csv_upload:pattern_analysis_home')
    except Exception as e:
        logger.error(f"❌ ERROR during quick search: {str(e)}")
        logger.error(f"  📊 Pattern: {pattern}")
        logger.error(f"  🏢 Stock: {stock_symbol}")
        messages.error(request, f"Error during search: {str(e)}")
        return redirect('csv_upload:pattern_analysis_home')


def get_stock_data_api(request):
    """
    API endpoint to get candlestick data for charting
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Only GET method allowed'}, status=405)
    
    stock_symbol = request.GET.get('symbol')
    days = int(request.GET.get('days', 30))
    
    if not stock_symbol:
        return JsonResponse({'error': 'Stock symbol required'}, status=400)
    
    try:
        stock = Stock.objects.get(stock_symbol__iexact=stock_symbol)
        
        # Get recent candlestick data
        date_from = datetime.now().date() - timedelta(days=days)
        candlesticks = Candlestick.objects.filter(
            stock=stock,
            candle_date__gte=date_from
        ).order_by('candle_date')[:100]  # Limit to prevent large responses
        
        data = []
        for candle in candlesticks:
            data.append({
                'date': candle.candle_date.strftime('%Y-%m-%d'),
                'open': float(candle.open_price),
                'high': float(candle.high_price),
                'low': float(candle.low_price),
                'close': float(candle.close_price),
                'volume': candle.number_of_shares or 0
            })
        
        return JsonResponse({
            'stock_symbol': stock.stock_symbol,
            'stock_name': stock.stock_name,
            'data': data
        })
        
    except Stock.DoesNotExist:
        return JsonResponse({'error': 'Stock not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def prepare_chart_data(patterns_found):
    """
    Prepare chart data structure for frontend visualization
    """
    chart_data = {}
    
    for stock_symbol, patterns in patterns_found.items():
        stock_chart_data = {
            'symbol': stock_symbol,
            'patterns': {},
            'candlesticks': []
        }
        
        # Process each pattern type
        for pattern_type, pattern_instances in patterns.items():
            if pattern_instances:
                stock_chart_data['patterns'][pattern_type] = []
                
                for pattern in pattern_instances:
                    stock_chart_data['patterns'][pattern_type].append({
                        'date': pattern['candle_date'].strftime('%Y-%m-%d') if hasattr(pattern['candle_date'], 'strftime') else str(pattern['candle_date']),
                        'open': float(pattern['open_price']),
                        'high': float(pattern['high_price']),
                        'low': float(pattern['low_price']),
                        'close': float(pattern['close_price']),
                        'strength': pattern.get('pattern_strength', 1),
                        'type': pattern.get('pattern_type', pattern_type)
                    })
                    
                    # Add to candlesticks for chart
                    stock_chart_data['candlesticks'].append({
                        'date': pattern['candle_date'].strftime('%Y-%m-%d') if hasattr(pattern['candle_date'], 'strftime') else str(pattern['candle_date']),
                        'open': float(pattern['open_price']),
                        'high': float(pattern['high_price']),
                        'low': float(pattern['low_price']),
                        'close': float(pattern['close_price']),
                        'isPattern': True,
                        'patternType': pattern.get('pattern_type', pattern_type)
                    })
        
        if stock_chart_data['patterns']:  # Only add if patterns were found
            chart_data[stock_symbol] = stock_chart_data
    
    return chart_data


def pattern_history(request, stock_id):
    """
    View pattern history for a specific stock
    """
    try:
        stock = Stock.objects.get(stock_id=stock_id)
        
        # Get recent patterns for all types
        analysis_results = PatternAnalysisService.analyze_patterns(
            pattern_types=['hammer', 'harami', 'doji'],
            stock_ids=[stock_id],
            date_from=datetime.now().date() - timedelta(days=365)  # Last year
        )
        
        context = {
            'stock': stock,
            'analysis_results': analysis_results,
            'patterns_found': analysis_results['patterns_found'].get(stock.stock_symbol, {}),
        }
        
        return render(request, 'csv_upload/pattern_history.html', context)
        
    except Stock.DoesNotExist:
        messages.error(request, "Stock not found.")
        return redirect('csv_upload:pattern_analysis_home')