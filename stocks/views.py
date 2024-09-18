from django.shortcuts import render
import pandas as pd
import yfinance as yf  # type: ignore
from datetime import datetime, timedelta

# トップページのビュー
def index_view(request):
    # 有名企業のティッカーシンボルと名前をハードコード
    stocks = [
        {'name': 'Apple', 'code': 'AAPL'},
        {'name': 'Google', 'code': 'GOOGL'},
        {'name': 'Microsoft', 'code': 'MSFT'},
        {'name': 'Amazon', 'code': 'AMZN'},
        {'name': 'Facebook (Meta)', 'code': 'META'},
        {'name': 'Tesla', 'code': 'TSLA'},
        {'name': 'NVIDIA', 'code': 'NVDA'},
        {'name': 'Berkshire Hathaway', 'code': 'BRK-B'},
        {'name': 'Visa', 'code': 'V'},
        {'name': 'Johnson & Johnson', 'code': 'JNJ'},
        {'name': 'JPMorgan Chase', 'code': 'JPM'},
        {'name': 'Procter & Gamble', 'code': 'PG'},
        {'name': 'Walmart', 'code': 'WMT'},
        {'name': 'Mastercard', 'code': 'MA'},
        {'name': 'Disney', 'code': 'DIS'},
        {'name': 'Pfizer', 'code': 'PFE'},
        {'name': 'Coca-Cola', 'code': 'KO'},
        {'name': 'PepsiCo', 'code': 'PEP'},
        {'name': 'Intel', 'code': 'INTC'},
        {'name': 'Cisco', 'code': 'CSCO'},
        {'name': 'Verizon', 'code': 'VZ'},
        {'name': 'AT&T', 'code': 'T'},
        {'name': 'ExxonMobil', 'code': 'XOM'},
        {'name': 'Chevron', 'code': 'CVX'},
        {'name': 'McDonald\'s', 'code': 'MCD'},
        {'name': 'Nike', 'code': 'NKE'},
        {'name': 'Starbucks', 'code': 'SBUX'},
        {'name': 'IBM', 'code': 'IBM'},
        {'name': 'Adobe', 'code': 'ADBE'},
        {'name': 'Netflix', 'code': 'NFLX'}
    ]
    context = {
        'stocks': stocks,
    }
    return render(request, 'stocks/index.html', context)


# 株価詳細ページのビュー（detail.htmlを使用）
def stock_detail_view(request, ticker):
    # Yahoo Finance から株価データを取得
    try:
        start_date_str = request.GET.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date_str = request.GET.get('end_date', datetime.now().strftime('%Y-%m-%d'))

        # 日付を文字列から datetime オブジェクトに変換
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    except ValueError:
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

    # Yahoo Finance API を使って株価データを取得
    df = fetch_stock_data(ticker, start_date, end_date)

    # 最新の終値を取得
    latest_price = df[ticker].iloc[-1] if not df.empty else 'データなし'

    context = {
        'ticker': ticker,
        'latest_price': latest_price,
        'stock_data': df.to_html() if not df.empty else None,  # DataFrame を HTML に変換して渡す
    }
    return render(request, 'detail.html', context)

# 株価データ取得関数
def fetch_stock_data(ticker_symbol, start_date, end_date):
    try:
        tkr = yf.Ticker(ticker_symbol)
        hist = tkr.history(start=start_date, end=end_date)

        # インデックスを日付に変換し、時間部分を削除
        hist.index = pd.to_datetime(hist.index).date

        # 終値のみを選択し、列名をティッカーシンボルに設定
        hist = hist[['Close']]
        hist.columns = [ticker_symbol]

        # インデックスをリセットして日付を列として追加
        hist = hist.reset_index()

        return hist
    except Exception as e:
        print(f"{ticker_symbol} のデータ取得中にエラーが発生しました: {e}")
        return pd.DataFrame()  # エラーが発生した場合は空の DataFrame を返す
