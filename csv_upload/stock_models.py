from django.db import models

class Stock(models.Model):
    """Model for stocks table"""
    stock_id = models.AutoField(primary_key=True)
    stock_symbol = models.CharField(max_length=16, null=False)
    stock_name = models.CharField(max_length=500, null=True, blank=True)
    stock_exchange = models.CharField(max_length=10, null=True, blank=True)
    stock_group = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        db_table = 'stocks'
        unique_together = ('stock_symbol', 'stock_exchange')

    def __str__(self):
        return f"{self.stock_symbol} ({self.stock_exchange})"


class Candlestick(models.Model):
    """Model for candlesticks table"""
    candle_id = models.AutoField(primary_key=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, db_column='stock_id')
    candle_date = models.DateTimeField(null=False)
    open_price = models.DecimalField(max_digits=16, decimal_places=4, null=False)
    high_price = models.DecimalField(max_digits=16, decimal_places=4, null=False)
    low_price = models.DecimalField(max_digits=16, decimal_places=4, null=False)
    close_price = models.DecimalField(max_digits=16, decimal_places=4, null=False)
    prev_close_price = models.DecimalField(max_digits=16, decimal_places=4, null=False)
    number_of_trades = models.BigIntegerField(null=True, blank=True)
    number_of_shares = models.BigIntegerField(null=True, blank=True)
    net_turnover = models.DecimalField(max_digits=16, decimal_places=4, null=True, blank=True)

    class Meta:
        db_table = 'candlesticks'
        unique_together = ('stock', 'candle_date')

    def __str__(self):
        return f"{self.stock.stock_symbol} - {self.candle_date.date()}"