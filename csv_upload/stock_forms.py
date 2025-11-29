from django import forms
from django.core.exceptions import ValidationError
from .models import Stock, Candlestick


class StockForm(forms.ModelForm):
    """Form for creating and editing Stock records"""
    
    class Meta:
        model = Stock
        fields = ['stock_symbol', 'stock_name', 'stock_exchange', 'stock_group']
        widgets = {
            'stock_symbol': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., RELIANCE, TCS',
                'maxlength': '16',
                'style': 'text-transform: uppercase;'
            }),
            'stock_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Reliance Industries Ltd',
                'maxlength': '500'
            }),
            'stock_exchange': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., BSE, NSE',
                'maxlength': '10',
                'style': 'text-transform: uppercase;'
            }),
            'stock_group': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., A, B, T',
                'maxlength': '10',
                'style': 'text-transform: uppercase;'
            }),
        }
        labels = {
            'stock_symbol': 'Stock Symbol*',
            'stock_name': 'Company Name',
            'stock_exchange': 'Exchange',
            'stock_group': 'Stock Group',
        }
        help_texts = {
            'stock_symbol': 'Unique stock ticker symbol (required)',
            'stock_name': 'Full company name',
            'stock_exchange': 'Stock exchange where it\'s traded',
            'stock_group': 'Classification group of the stock',
        }

    def clean_stock_symbol(self):
        symbol = self.cleaned_data.get('stock_symbol')
        if symbol:
            symbol = symbol.upper().strip()
            if not symbol.replace('&', '').replace('-', '').replace('.', '').isalnum():
                raise ValidationError("Stock symbol can only contain letters, numbers, &, -, and .")
        return symbol

    def clean_stock_exchange(self):
        exchange = self.cleaned_data.get('stock_exchange')
        if exchange:
            exchange = exchange.upper().strip()
        return exchange

    def clean_stock_group(self):
        group = self.cleaned_data.get('stock_group')
        if group:
            group = group.upper().strip()
        return group

    def clean(self):
        cleaned_data = super().clean()
        symbol = cleaned_data.get('stock_symbol')
        exchange = cleaned_data.get('stock_exchange')
        
        if symbol and exchange:
            # Check for duplicate symbol-exchange combination
            existing = Stock.objects.filter(
                stock_symbol=symbol, 
                stock_exchange=exchange
            )
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError(
                    f"Stock {symbol} already exists on {exchange} exchange."
                )
        
        return cleaned_data


class CandlestickForm(forms.ModelForm):
    """Form for creating and editing Candlestick records"""
    
    class Meta:
        model = Candlestick
        fields = [
            'stock', 'candle_date', 'open_price', 'high_price', 
            'low_price', 'close_price', 'prev_close_price',
            'number_of_trades', 'number_of_shares', 'net_turnover'
        ]
        widgets = {
            'stock': forms.Select(attrs={
                'class': 'form-control',
            }),
            'candle_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'open_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'high_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'low_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'close_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'prev_close_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'number_of_trades': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
            'number_of_shares': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
            'net_turnover': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
        }
        labels = {
            'stock': 'Stock*',
            'candle_date': 'Trading Date & Time*',
            'open_price': 'Opening Price*',
            'high_price': 'High Price*',
            'low_price': 'Low Price*',
            'close_price': 'Closing Price*',
            'prev_close_price': 'Previous Close*',
            'number_of_trades': 'Number of Trades',
            'number_of_shares': 'Volume (Shares)',
            'net_turnover': 'Net Turnover',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Order stocks by symbol for better UX
        self.fields['stock'].queryset = Stock.objects.all().order_by('stock_exchange', 'stock_symbol')
        self.fields['stock'].empty_label = "Select a stock"

    def clean(self):
        cleaned_data = super().clean()
        
        # Validate price relationships
        open_price = cleaned_data.get('open_price')
        high_price = cleaned_data.get('high_price')
        low_price = cleaned_data.get('low_price')
        close_price = cleaned_data.get('close_price')
        
        if all([open_price, high_price, low_price, close_price]):
            # High should be >= all other prices
            if high_price < max(open_price, low_price, close_price):
                raise ValidationError("High price must be greater than or equal to all other prices.")
            
            # Low should be <= all other prices
            if low_price > min(open_price, high_price, close_price):
                raise ValidationError("Low price must be less than or equal to all other prices.")
        
        # Check for duplicate stock-date combination
        stock = cleaned_data.get('stock')
        candle_date = cleaned_data.get('candle_date')
        
        if stock and candle_date:
            existing = Candlestick.objects.filter(
                stock=stock,
                candle_date=candle_date
            )
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise ValidationError(
                    f"Candlestick data for {stock.stock_symbol} on {candle_date.date()} already exists."
                )
        
        return cleaned_data


class StockFilterForm(forms.Form):
    """Form for filtering stocks"""
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by symbol or name...',
        })
    )
    exchange = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by exchange...',
        })
    )
    group = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by group...',
        })
    )


class CandlestickFilterForm(forms.Form):
    """Form for filtering candlestick data"""
    stock = forms.ModelChoiceField(
        queryset=Stock.objects.all().order_by('stock_exchange', 'stock_symbol'),
        required=False,
        empty_label="All stocks",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )
    exchange = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by exchange...',
        })
    )