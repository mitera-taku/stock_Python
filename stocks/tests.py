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
        self.assertTemplateUsed(response, 'stocks/index.html')

class StockAppFormTests(TestCase):
    def test_valid_form_submission(self):
        response = self.client.post(reverse('stocks:stock_detail', args=['AAPL']), {
            'stock_symbol': 'AAPL',
            'start_date': '2023-01-01',
            'end_date': '2023-01-31'
        })
        self.assertEqual(response.status_code, 200)

    def test_invalid_form_submission(self):
        response = self.client.post(reverse('stocks:stock_detail', args=['AAPL']), {
            'stock_symbol': '',
            'start_date': '2023-01-01',
            'end_date': '2023-01-31'
        })
        self.assertEqual(response.status_code, 200)

class StockAppTemplateTests(TestCase):

    def test_detail_template_renders_correctly(self):
        response = self.client.post(reverse('stocks:stock_detail', args=['AAPL']), {
            'stock_symbol': 'AAPL',
            'start_date': '2023-01-01',
            'end_date': '2023-01-31'
        })
        self.assertTemplateUsed(response, 'stocks/index.html')
        self.assertEqual(response.status_code, 200)

