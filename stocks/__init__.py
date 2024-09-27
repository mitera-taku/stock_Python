# __init__.py
# views, models, admin をインポートする代わりに関数内でインポート
__all__ = ['stock_detail_view', 'admin', 'StocksConfig']

def get_stock_model():
    from .models import Stock, StockHistory
    return Stock, StockHistory
