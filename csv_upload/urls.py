from django.urls import path
from . import views
from . import stock_views

app_name = 'csv_upload'

urlpatterns = [
    # CSV Upload functionality
    path('upload/', views.upload_csv, name='upload_csv'),
    path('upload/result/', views.upload_result, name='upload_result'),
    path('list/', views.csv_list, name='csv_list'),
    
    # Stock CRUD operations
    path('stocks/', stock_views.stock_list, name='stock_list'),
    path('stocks/create/', stock_views.stock_create, name='stock_create'),
    path('stocks/<int:stock_id>/', stock_views.stock_detail, name='stock_detail'),
    path('stocks/<int:stock_id>/edit/', stock_views.stock_edit, name='stock_edit'),
    path('stocks/<int:stock_id>/delete/', stock_views.stock_delete, name='stock_delete'),
    
    # Candlestick CRUD operations
    path('candlesticks/', stock_views.candlestick_list, name='candlestick_list'),
    path('candlesticks/create/', stock_views.candlestick_create, name='candlestick_create'),
    path('candlesticks/<int:candle_id>/', stock_views.candlestick_detail, name='candlestick_detail'),
    path('candlesticks/<int:candle_id>/edit/', stock_views.candlestick_edit, name='candlestick_edit'),
    path('candlesticks/<int:candle_id>/delete/', stock_views.candlestick_delete, name='candlestick_delete'),
    
    # AJAX endpoints
    path('api/stocks/search/', stock_views.stock_search_ajax, name='stock_search_ajax'),
]
