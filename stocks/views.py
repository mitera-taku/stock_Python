from django.shortcuts import render
import pandas as pd  # type: ignore
import yfinance as yf  # type: ignore
import numpy as np
import math
from datetime import datetime, timedelta
from tensorflow.keras.models import Sequential  # type: ignore
from tensorflow.keras.layers import LSTM, Dense  # type: ignore
import plotly.graph_objs as go # type: ignore
import plotly.offline as pyo # type: ignore

# インタラクティブなグラフの作成
def plot_interactive_graph(stock_data):
    fig = go.Figure()

    # Open, Close, High, Low データの追加
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Open'], mode='lines', name='Open Price'))
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'], mode='lines', name='Close Price'))
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Low'], mode='lines', name='Low Price'))
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['High'], mode='lines', name='High Price'))

    fig.update_layout(
        title='Stock Prices',
        xaxis_title='Date',
        yaxis_title='Price',
        showlegend=True  # レジェンド（凡例）を表示
    )

    # HTML形式で出力
    graph_html = pyo.plot(fig, include_plotlyjs=False, output_type='div')
    return graph_html


# トップページのビュー
def index_view(request):
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
    ]
    # デフォルトの日付を設定（60日前から今日まで）
    end_date_default = datetime.today().strftime('%Y-%m-%d')
    start_date_default = (datetime.today() - timedelta(days=60)).strftime('%Y-%m-%d')

    context = {
        'stocks': stocks,
        'start_date_default': start_date_default,
        'end_date_default': end_date_default
    }
    return render(request, 'stocks/index.html', context)

# 株価データ取得とAI予測値の計算
def get_stock_data(request, ticker=None):
    if request.method == 'POST':
        ticker = request.POST.get('stock_symbol')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # 日付フォーマットの確認
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            return render(request, 'stocks/index.html', {'error': '日付形式が正しくありません。'})

    if not ticker:
        return render(request, 'stocks/index.html', {'error': 'ティッカーシンボルが指定されていません。'})

    # 株価データの取得（始値、高値、安値、終値、出来高、調整後終値）
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    if stock_data.empty:
        return render(request, 'stocks/index.html', {'error': '指定された日付範囲でデータが見つかりません。'})

    # 必要な列のみを取得
    stock_data = stock_data[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']].fillna(method='ffill')

    # AI予測のためのデータ準備
    data = stock_data['Close'].values.reshape(-1, 1)

    # AI用データセットの作成
    def create_dataset(data, time_steps=1):
        X, y = [], []
        for i in range(len(data) - time_steps - 1):
            X.append(data[i:(i + time_steps), 0])
            y.append(data[i + time_steps, 0])
        return np.array(X), np.array(y)

    time_steps = 60  # 過去60日分のデータを使用して予測
    X, y = create_dataset(data, time_steps)

    if X.shape[0] == 0:
        return render(request, 'stocks/index.html', {'error': 'データが不足しています。'})

    # LSTMモデルの構築
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], 1)))
    model.add(LSTM(units=50))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mean_squared_error')

    # データの整形
    X = X.reshape(X.shape[0], X.shape[1], 1)

    # モデルのトレーニング
    model.fit(X, y, epochs=10, batch_size=32)

    # 最新の株価データで次の日の株価を予測
    last_data = data[-time_steps:].reshape(1, time_steps, 1)
    predicted_price = model.predict(last_data)

    # 予測結果を小数点2位で切り上げ
    rounded_price = math.ceil(predicted_price[0][0] * 100) / 100

    # 前日比の計算
    previous_close = stock_data['Close'].iloc[-2] if len(stock_data) > 1 else 0
    change_today = stock_data['Close'].iloc[-1] - previous_close

    # インタラクティブグラフの生成
    graph_html = plot_interactive_graph(stock_data)

    context = {
        'stock_symbol': ticker,
        'predicted_price': rounded_price,  # AI予測値
        'change_today': round(change_today, 2),  # 前日比
        'stock_data': stock_data.to_html(classes="table table-striped"),
        'graph_html': graph_html,  # グラフHTML
        'start_date': start_date,
        'end_date': end_date
    }
    return render(request, 'stocks/detail.html', context)

# 株価の詳細ページのビュー
def stock_detail_view(request, ticker):
    # get_stock_data 関数を呼び出して、株価データを取得する
    return get_stock_data(request, ticker=ticker)
