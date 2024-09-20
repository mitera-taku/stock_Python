from django.shortcuts import render
import pandas as pd  # type: ignore
import yfinance as yf  # type: ignore
import numpy as np
import math

from django.test import TestCase
from django.urls import reverse
from django.urls import resolve
from stocks.views import index_view, stock_detail_view
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
        self.assertContains(response, 'Apple')  # テストで確認する内容に応じて適切な値に変更

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
            'stock_symbol': '',  # 無効な値
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
        # モックデータを設定
        mock_yfinance.return_value = pd.DataFrame({
            'Open': [150], 'High': [155], 'Low': [145], 'Close': [152], 'Volume': [1000]
        })

        response = self.client.post(reverse('stocks:stock_detail', args=['AAPL']), {
            'stock_symbol': 'AAPL',
            'start_date': '2023-01-01',
            'end_date': '2023-01-31'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '152')  # モックデータに基づく予測結果をチェック
        mock_yfinance.assert_called_once()
        
class ChangeTodayTests(TestCase):
    @patch('yfinance.download')
    def test_change_today_display(self, mock_yfinance):
        # モックデータを設定
        mock_yfinance.return_value = pd.DataFrame({
            'Open': [150], 'High': [155], 'Low': [145], 'Close': [152], 'Volume': [1000]
        })

        response = self.client.post(reverse('stocks:stock_detail', args=['AAPL']), {
            'stock_symbol': 'AAPL',
            'start_date': '2023-01-01',
            'end_date': '2023-01-31'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '+2.00円')  # 前日比が+で表示されることを確認

class StockAppURLRoutingTests(TestCase):
    def test_index_url_is_resolved(self):
        url = reverse('stocks:index')
        self.assertEqual(resolve(url).func, index_view)

    def test_stock_detail_url_is_resolved(self):
        url = reverse('stocks:stock_detail', args=['AAPL'])
        self.assertEqual(resolve(url).func, stock_detail_view)
