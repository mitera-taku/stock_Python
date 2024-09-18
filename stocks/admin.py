from django.contrib import admin
from .models import Stock, StockHistory

admin.site.register(Stock)
admin.site.register(StockHistory)
