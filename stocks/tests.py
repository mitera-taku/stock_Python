from django.shortcuts import render
import pandas as pd  # type: ignore
import yfinance as yf  # type: ignore
import numpy as np
import math
from datetime import datetime, timedelta
from tensorflow.keras.models import Sequential  # type: ignore
from tensorflow.keras.layers import LSTM, Dense  # type: ignore
import plotly.graph_objs as go  # type: ignore
import plotly.offline as pyo  # type: ignore

# インタラクティブなグラフの作成
def plot_interactive_graph(stock_data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Open'], mode='lines', name='Open Price'))
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Close'], mode='lines', name='Close Price'))
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['Low'], mode='lines', name='Low Price'))
    fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data['High'], mode='lines', name='High Price'))

    fig.update_layout(
        title='Stock Prices',
        xaxis_title='Date',
        yaxis_title='Price',
        showlegend=True
    )

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
    end_date_default = datetime.today().strftime('%Y-%m-%d')
    start_date_default = (datetime.today() - timedelta(days=90)).strftime('%Y-%m-%d')

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

    stock_data = yf.download(ticker, start=start_date, end=end_date)
    if stock_data.empty:
        return render(request, 'stocks/index.html', {'error': '指定された日付範囲でデータが見つかりません。'})

    stock_data = stock_data[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']].ffill()
    data = stock_data['Close'].values.reshape(-1, 1)

    def create_dataset(data, time_steps=60):
        X, y = [], []
        for i in range(len(data) - time_steps):
            X.append(data[i:i + time_steps, 0])
            y.append(data[i + time_steps, 0])
        return np.array(X), np.array(y)

    time_steps = 60
    X, y = create_dataset(data, time_steps)

    if X.shape[0] == 0:
        return render(request, 'stocks/index.html', {'error': 'データが不足しています。'})

    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X.shape[1], 1)))
    model.add(LSTM(units=50))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')

    X = X.reshape(X.shape[0], X.shape[1], 1)
    model.fit(X, y, epochs=10, batch_size=32)

    last_data = data[-time_steps:].reshape(1, time_steps, 1)
    predicted_price = model.predict(last_data)
    rounded_price = math.ceil(predicted_price[0][0] * 100) / 100

    previous_close = stock_data['Close'].iloc[-2] if len(stock_data) > 1 else 0
    change_today = stock_data['Close'].iloc[-1] - previous_close

    change_today_display = f"+{round(change_today, 2)}円" if change_today > 0 else f"{round(change_today, 2)}円"
    graph_html = plot_interactive_graph(stock_data)

    context = {
        'stock_symbol': ticker,
        'predicted_price': rounded_price,
        'change_today': round(change_today, 2),
        'stock_data': stock_data.to_html(classes="table table-striped"),
        'graph_html': graph_html,
        'start_date': start_date,
        'end_date': end_date
    }
    return render(request, 'stocks/detail.html', context)

# 株価の詳細ページのビュー
def stock_detail_view(request, ticker):
    return get_stock_data(request, ticker=ticker)

# テストコード
from django.test import TestCase
from django.urls import reverse, resolve
from unittest.mock import patch

class StockAppURLTests(TestCase):
    def test_index_url_resolves(self):
        response = self.client.get(reverse('stocks:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stocks/index.html')

    def test_detail_url_resolves(self):
        response = self.client.post(reverse('stocks:stock_detail', args=['AAPL']), {
            'stock_symbol': 'AAPL',
            'start_date': '2023-01-01',
            'end_date': '2023-01-31'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stocks/detail.html')
        self.assertContains(response, 'Apple')

class StockAppFormTests(TestCase):
    def test_valid_form_submission(self):
        response = self.client.post(reverse('stocks:stock_detail', args=['AAPL']), {
            'stock_symbol': 'AAPL',
            'start_date': '2023-01-01',
            'end_date': '2023-01-31'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AAPL')

    def test_invalid_form_submission(self):
        response = self.client.post(reverse('stocks:stock_detail', args=['AAPL']), {
            'stock_symbol': '',
            'start_date': '2023-01-01',
            'end_date': '2023-01-31'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '企業コードを入力してください')

class StockAppTemplateTests(TestCase):
    def test_index_template_renders_correctly(self):
        response = self.client.get(reverse('stocks:index'))
        self.assertTemplateUsed(response, 'stocks/index.html')
        self.assertContains(response, '株価情報検索')

    def test_detail_template_renders_correctly(self):
        response = self.client.post(reverse('stocks:stock_detail', args=['AAPL']), {
            'stock_symbol': 'AAPL',
            'start_date': '2023-01-01',
            'end_date': '2023-01-31'
        })
        self.assertTemplateUsed(response, 'stocks/detail.html')
        self.assertContains(response, 'AI予測値')

class StockPredictionTests(TestCase):
    @patch('yfinance.download')
    def test_stock_prediction(self, mock_yfinance):
        mock_yfinance.return_value = pd.DataFrame({
            'Open': [150], 'High': [155], 'Low': [145], 'Close': [152], 'Volume': [1000]
        })

        response = self.client.post(reverse('stocks:stock_detail', args=['AAPL']), {
            'stock_symbol': 'AAPL',
            'start_date': '2023-01-01',
            'end_date': '2023-01-31'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '152')
        mock_yfinance.assert_called_once()

class ChangeTodayTests(TestCase):
    @patch('yfinance.download')
    def test_change_today_display(self, mock_yfinance):
        mock_yfinance.return_value = pd.DataFrame({
            'Open': [150], 'High': [155], 'Low': [145], 'Close': [152], 'Volume': [1000]
        })

        response = self.client.post(reverse('stocks:stock_detail', args=['AAPL']), {
            'stock_symbol': 'AAPL',
            'start_date': '2023-01-01',
            'end_date': '2023-01-31'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '+2.00円')

class StockAppURLRoutingTests(TestCase):
    def test_index_url_is_resolved(self):
        url = reverse('stocks:index')
        self.assertEqual(resolve(url).func, index_view)

    def test_stock_detail_url_is_resolved(self):
        url = reverse('stocks:stock_detail', args=['AAPL'])
        self.assertEqual(resolve(url).func, stock_detail_view)
