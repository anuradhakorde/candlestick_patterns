from django import forms
from django.db import models
from csv_upload.models import Stock
from csv_upload.pattern_detector import PatternAnalysisService

class PatternAnalysisForm(forms.Form):
    """
    Form for selecting candlestick patterns and stocks for analysis
    """
    
    PATTERN_CHOICES = [
        ('hammer', 'Hammer Pattern'),
        ('harami', 'Harami Pattern (Bullish/Bearish)'),
        ('doji', 'Doji Pattern'),
    ]
    
    patterns = forms.MultipleChoiceField(
        choices=PATTERN_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input',
            'id': 'pattern-checkboxes'
        }),
        label="Select Candlestick Patterns",
        help_text="Choose one or more patterns to analyze",
        required=True
    )
    
    stocks = forms.ModelMultipleChoiceField(
        queryset=Stock.objects.all().order_by('stock_symbol'),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-select',
            'multiple': True,
            'size': '10',
            'id': 'stock-selector'
        }),
        label="Select Stocks",
        help_text="Hold Ctrl/Cmd to select multiple stocks",
        required=True
    )
    
    date_from = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label="From Date",
        required=False,
        help_text="Optional: Filter patterns from this date"
    )
    
    date_to = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label="To Date",
        required=False,
        help_text="Optional: Filter patterns up to this date"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Order stocks by name if available, otherwise by symbol
        self.fields['stocks'].queryset = Stock.objects.all().order_by('stock_name', 'stock_symbol')
        
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if field_name != 'patterns':  # patterns already have custom widget
                field.widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        # Validate date range
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("From date cannot be later than To date.")
        
        # Limit number of stocks to prevent performance issues
        stocks = cleaned_data.get('stocks')
        if stocks and len(stocks) > 20:
            raise forms.ValidationError("Please select maximum 20 stocks for analysis.")
        
        return cleaned_data


class QuickPatternSearchForm(forms.Form):
    """
    Simplified form for quick pattern searches
    """
    
    pattern = forms.ChoiceField(
        choices=[
            ('hammer', 'Hammer'),
            ('harami', 'Harami'),
            ('doji', 'Doji'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Pattern Type"
    )
    
    stock_symbol = forms.CharField(
        max_length=16,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter stock symbol (e.g., RELIANCE, TCS)'
        }),
        label="Stock Symbol",
        help_text="Enter a single stock symbol"
    )
    
    days_back = forms.ChoiceField(
        choices=[
            (7, 'Last 7 days'),
            (30, 'Last 30 days'),
            (90, 'Last 3 months'),
            (180, 'Last 6 months'),
            (365, 'Last 1 year'),
        ],
        initial=30,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Time Period"
    )
    
    def clean_stock_symbol(self):
        symbol = self.cleaned_data['stock_symbol'].upper().strip()
        
        # Check if stock exists
        if not Stock.objects.filter(stock_symbol__iexact=symbol).exists():
            raise forms.ValidationError(f"Stock symbol '{symbol}' not found in database.")
        
        return symbol