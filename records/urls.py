# records/urls.py の新しい完全な内容

from django.urls import path
from . import views

app_name = 'records'

urlpatterns = [
    # 基本のページ
    path('', views.project_list, name='project_list'),
    
    # ユーザー登録（サインアップ）ページ
    path('signup/', views.signup, name='signup'),
    
    # プロジェクト関連
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/update/', views.project_update, name='project_update'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('projects/<int:pk>/calculate-win-rate/', views.calculate_win_rate, name='calculate_win_rate'),
    path('projects/<int:pk>/reset/', views.project_reset_balance, name='project_reset_balance'), # この行が新しい
    

    
    # 収支記録関連
    path('projects/<int:project_pk>/records/create/', views.record_create, name='record_create'),
    path('records/<int:pk>/update/', views.record_update, name='record_update'),
    path('records/<int:pk>/delete/', views.record_delete, name='record_delete'),
    
    # 共有ページ
    path('share/<uuid:token>/', views.share_project, name='share_project'),
]
