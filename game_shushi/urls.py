# game_shushi/urls.py の正しい完全な内容

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ↓↓ ログアウト機能には、この行が絶対に必要です ↓↓
    path('accounts/', include('django.contrib.auth.urls')),
    
    path('', include('records.urls')),
]