from django.shortcuts import render, get_object_or_404
from .models import Stock, StockHistory
import pandas as pd
import yfinance as yf  # type: ignore
from datetime import datetime, timedelta

# トップページのビュー
def index_view(request):
    # 全ての株式データを取得してテンプレートに渡す
    stocks = Stock.objects.all()
    context = {
        'stocks': stocks,
    }
    return render(request, 'stocks/index.html', context)

# 株価詳細ページのビュー
def stock_detail_view(request, ticker):
    # 指定された株式コードで株式を取得し、見つからなければ404エラーを返す
    stock = get_object_or_404(Stock, code=ticker)

    # 株式の履歴データを取得し、日付の降順でソート
    history = StockHistory.objects.filter(stock=stock).order_by('-date')

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

    # Yahoo Finance API を使って株価を取得
    df = fetch_stock_data(stock.code, start_date, end_date)

    context = {
        'ticker': stock.code,
        'latest_price': stock.latest_price,
        'history': history,
        'stock_data': df.to_html() if not df.empty else None,  # DataFrame を HTML に変換して渡す
    }
    return render(request, 'stocks/detail.html', context)

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
