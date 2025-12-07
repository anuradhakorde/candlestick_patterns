import pandas as pd
import logging
from django.db import connection
from csv_upload.models import Stock, Candlestick
from typing import List, Dict, Any

# Configure logger for pattern detection
logger = logging.getLogger('pattern_analysis')

class CandlestickPatternDetector:
    """
    Class to detect various candlestick patterns
    """
    
    @staticmethod
    def detect_hammer_pattern(df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect Hammer pattern:
        - Small body (close and open are close)
        - Long lower shadow (at least 2x body size)
        - Little to no upper shadow
        """
        if df.empty or len(df) < 1:
            return df.iloc[0:0]  # Return empty DataFrame with same structure
            
        # Calculate body and shadow sizes
        df = df.copy()
        df['body_size'] = abs(df['close_price'] - df['open_price'])
        df['upper_shadow'] = df['high_price'] - df[['close_price', 'open_price']].max(axis=1)
        df['lower_shadow'] = df[['close_price', 'open_price']].min(axis=1) - df['low_price']
        df['total_range'] = df['high_price'] - df['low_price']
        
        # Hammer pattern conditions
        hammer_conditions = (
            (df['lower_shadow'] >= 2 * df['body_size']) &  # Long lower shadow
            (df['upper_shadow'] <= 0.1 * df['total_range']) &  # Small upper shadow
            (df['body_size'] > 0.1 * df['total_range'])  # Body exists but is small
        )
        
        df['pattern_type'] = 'Hammer'
        df['pattern_strength'] = df['lower_shadow'] / df['body_size']  # Strength indicator
        
        return df[hammer_conditions]
    
    @staticmethod
    def detect_harami_pattern(df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect Bullish/Bearish Harami pattern:
        - Two candles: large body followed by small body
        - Small candle completely within large candle's body
        """
        if df.empty or len(df) < 2:
            return df.iloc[0:0]  # Return empty DataFrame with same structure
            
        df = df.copy().sort_values('candle_date')
        df = df.reset_index(drop=True)
        
        # Calculate body sizes
        df['body_size'] = abs(df['close_price'] - df['open_price'])
        df['body_high'] = df[['close_price', 'open_price']].max(axis=1)
        df['body_low'] = df[['close_price', 'open_price']].min(axis=1)
        
        harami_patterns = []
        
        for i in range(1, len(df)):
            current = df.iloc[i]
            previous = df.iloc[i-1]
            
            # Harami conditions:
            # 1. Previous candle has large body
            # 2. Current candle has smaller body
            # 3. Current candle's body is within previous candle's body
            if (previous['body_size'] > current['body_size'] * 1.5 and  # Large vs small body
                current['body_high'] <= previous['body_high'] and  # Current high within previous
                current['body_low'] >= previous['body_low']):  # Current low within previous
                
                # Determine if bullish or bearish harami
                pattern_type = 'Bullish Harami' if previous['close_price'] < previous['open_price'] else 'Bearish Harami'
                
                result_row = current.copy()
                result_row['pattern_type'] = pattern_type
                result_row['pattern_strength'] = previous['body_size'] / current['body_size']
                result_row['previous_candle_date'] = previous['candle_date']
                
                harami_patterns.append(result_row)
        
        if harami_patterns:
            return pd.DataFrame(harami_patterns)
        else:
            return df.iloc[0:0]  # Return empty DataFrame with same structure
    
    @staticmethod
    def detect_doji_pattern(df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect Doji pattern:
        - Open and close prices are very close
        - Small body relative to the total range
        """
        if df.empty:
            return df
            
        df = df.copy()
        df['body_size'] = abs(df['close_price'] - df['open_price'])
        df['total_range'] = df['high_price'] - df['low_price']
        
        # Doji condition: body is less than 5% of total range
        doji_conditions = (
            (df['body_size'] <= 0.05 * df['total_range']) &
            (df['total_range'] > 0)  # Avoid division by zero
        )
        
        df['pattern_type'] = 'Doji'
        df['pattern_strength'] = 1 - (df['body_size'] / df['total_range'])  # Closer to 1 is stronger doji
        
        return df[doji_conditions]


class PatternAnalysisService:
    """
    Service class to handle pattern analysis requests
    """
    
    AVAILABLE_PATTERNS = {
        'hammer': 'Hammer',
        'harami': 'Harami (Bullish/Bearish)',
        'doji': 'Doji'
    }
    
    @staticmethod
    def get_available_stocks() -> List[Dict[str, Any]]:
        """Get list of all available stocks"""
        stocks = Stock.objects.all().order_by('stock_symbol')
        return [
            {
                'id': stock.stock_id,
                'symbol': stock.stock_symbol,
                'name': stock.stock_name or stock.stock_symbol,
                'exchange': stock.stock_exchange
            }
            for stock in stocks
        ]
    
    @staticmethod
    def get_candlestick_data(stock_ids: List[int], date_from=None, date_to=None) -> pd.DataFrame:
        """Get candlestick data for specified stocks"""
        queryset = Candlestick.objects.filter(stock_id__in=stock_ids)
        
        if date_from:
            queryset = queryset.filter(candle_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(candle_date__lte=date_to)
            
        # Get data with stock information
        queryset = queryset.select_related('stock').order_by('stock_id', 'candle_date')
        
        if not queryset.exists():
            return pd.DataFrame()
        
        # Convert to DataFrame
        data = []
        for candle in queryset:
            data.append({
                'candle_id': candle.candle_id,
                'stock_id': candle.stock_id,
                'stock_symbol': candle.stock.stock_symbol,
                'stock_name': candle.stock.stock_name,
                'stock_exchange': candle.stock.stock_exchange,
                'candle_date': candle.candle_date,
                'open_price': float(candle.open_price),
                'high_price': float(candle.high_price),
                'low_price': float(candle.low_price),
                'close_price': float(candle.close_price),
                'prev_close_price': float(candle.prev_close_price),
                'number_of_trades': candle.number_of_trades,
                'number_of_shares': candle.number_of_shares,
                'net_turnover': float(candle.net_turnover) if candle.net_turnover else None
            })
        
        return pd.DataFrame(data)
    
    @classmethod
    def analyze_patterns(cls, pattern_types: List[str], stock_ids: List[int], 
                        date_from=None, date_to=None) -> Dict[str, Any]:
        """
        Analyze specified patterns for given stocks
        """
        logger.info(f"🔬 STARTING PATTERN DETECTION:")
        logger.info(f"  📊 Pattern types: {pattern_types}")
        logger.info(f"  🏢 Stock count: {len(stock_ids)}")
        logger.info(f"  📅 Date filter: {date_from} to {date_to}")
        
        # Get candlestick data
        df = cls.get_candlestick_data(stock_ids, date_from, date_to)
        
        logger.info(f"  💾 Candlestick records retrieved: {len(df)}")
        
        if df.empty:
            logger.warning("⚠️ No candlestick data found for the given criteria")
            return {
                'patterns_found': {},
                'total_patterns': 0,
                'stocks_analyzed': len(stock_ids),
                'date_range': {'from': date_from, 'to': date_to}
            }
        
        detector = CandlestickPatternDetector()
        patterns_found = {}
        total_patterns = 0
        
        # Group by stock for analysis
        for stock_id in stock_ids:
            stock_df = df[df['stock_id'] == stock_id].copy()
            if stock_df.empty:
                logger.info(f"  ⚠️ No data for stock ID {stock_id}")
                continue
                
            stock_symbol = stock_df.iloc[0]['stock_symbol']
            patterns_found[stock_symbol] = {}
            
            logger.info(f"  🔍 Analyzing {stock_symbol} ({len(stock_df)} candlesticks)")
            
            for pattern_type in pattern_types:
                if pattern_type == 'hammer':
                    pattern_df = detector.detect_hammer_pattern(stock_df)
                elif pattern_type == 'harami':
                    pattern_df = detector.detect_harami_pattern(stock_df)
                elif pattern_type == 'doji':
                    pattern_df = detector.detect_doji_pattern(stock_df)
                else:
                    logger.warning(f"    ❌ Unknown pattern type: {pattern_type}")
                    continue
                
                pattern_count = len(pattern_df)
                logger.info(f"    🎯 {pattern_type.title()}: {pattern_count} patterns found")
                
                if not pattern_df.empty:
                    patterns_found[stock_symbol][pattern_type] = pattern_df.to_dict('records')
                    total_patterns += len(pattern_df)
        
        logger.info(f"🏁 PATTERN DETECTION COMPLETE:")
        logger.info(f"  ✅ Total patterns found: {total_patterns}")
        logger.info(f"  📊 Stocks with patterns: {len(patterns_found)}")
        
        return {
            'patterns_found': patterns_found,
            'total_patterns': total_patterns,
            'stocks_analyzed': len(stock_ids),
            'date_range': {'from': date_from, 'to': date_to},
            'available_patterns': cls.AVAILABLE_PATTERNS
        }