from django.urls import path
from . import views

app_name = 'stocks'

urlpatterns = [
    path('', views.index_view, name='index'),  # トップページ
    path('stock/<str:ticker>/', views.stock_detail_view, name='stock_detail'),  # 詳細ページ
]
