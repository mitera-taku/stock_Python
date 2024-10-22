from django.urls import path
from . import views

app_name = 'stocks'

urlpatterns = [
    path('', views.index_view, name='index'),  # トップページ
    path('stock/<str:ticker>/', views.stock_detail_view, name='stock_detail'),  # 詳細ページ
    path('chatgpt/consult/', views.chatgpt_consultation_view, name='chatgpt_consultation'),
    path('todo/', views.todo_list_view, name='todo_list'),
    path('todo/add/', views.add_todo_view, name='add_todo'),
    path('todo/update/<int:todo_id>/', views.update_todo_view, name='update_todo'),
    path('todo/delete/<int:todo_id>/', views.delete_todo_view, name='delete_todo'),
]
