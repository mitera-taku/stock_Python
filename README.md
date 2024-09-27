# stock_Python

プロジェクト概要
このプロジェクトは、Djangoフレームワークを使用して構築されたWebアプリケーションです。ASGI と WSGI の両方に対応しており、サーバーの設定やルーティング、アプリケーションの設定がファイルごとに管理されています。
適宜修正させていただきますのでご指摘いただけると幸いです。

ファイル構成
以下の重要なファイルを説明します：

1. asgi.py
ASGI（Asynchronous Server Gateway Interface）は、Djangoアプリケーションが非同期サーバーと連携できるようにするためのエントリーポイントです。主な役割は、アプリケーションを非同期に処理するための準備をすることです。

get_asgi_application: DjangoのASGIアプリケーションを返します。これにより、非同期通信を処理することが可能になります。
python
コードをコピーする
from django.core.asgi import get_asgi_application

application = get_asgi_application()
2. wsgi.py
WSGI（Web Server Gateway Interface）は、Djangoアプリケーションが同期サーバーと通信するためのエントリーポイントです。多くの従来のサーバー（Gunicornなど）はWSGIを介してDjangoアプリケーションを実行します。

get_wsgi_application: DjangoのWSGIアプリケーションを返し、同期通信を処理します。
python
コードをコピーする
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
3. settings.py
このファイルは、Djangoプロジェクト全体の設定を管理します。データベース設定、インストールされているアプリケーション、ミドルウェア、テンプレート、静的ファイルの設定など、アプリケーションの動作に関する主要な設定が記述されています。

INSTALLED_APPS: プロジェクト内で使用されているアプリケーションがリストアップされています。
MIDDLEWARE: 各リクエスト/レスポンスの処理フローを管理するためのミドルウェアが定義されています。
DATABASES: アプリケーションで使用するデータベースの設定です。
python
コードをコピーする
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "db.sqlite3",
    }
}
4. urls.py
このファイルでは、URLのルーティングを設定しています。ユーザーがアクセスしたURLに基づいて、どのビューを表示するかを決定します。urlpatterns にはURLとそれに対応するビューの対応が記述されています。

path(): ルートURLに対応するビューを定義します。
python
コードをコピーする
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
インストールと実行手順
必要な依存関係をインストールします:
bash
コードをコピーする
pip install -r requirements.txt
マイグレーションを適用します:
bash
コードをコピーする
python manage.py migrate
サーバーを起動します:
bash
コードをコピーする
python manage.py runserver
使用技術

画面
![image](https://github.com/user-attachments/assets/ebf69948-2735-4a65-968f-01d87adf2e06)

![image](https://github.com/user-attachments/assets/26252870-67f3-4bee-8591-7ed4bc1c1c05)

![image](https://github.com/user-attachments/assets/76a64294-d517-4f69-8eac-b4925f1df9ba)

Python 3.x
Django 4.x
SQLite（デフォルトのデータベース）
ASGI と WSGI 両対応
