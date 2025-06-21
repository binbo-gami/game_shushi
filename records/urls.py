# records/urls.py の正しい完全な内容

from django.urls import path
from . import views

app_name = 'records'

urlpatterns = [
    # 基本のページ
    path('', views.project_list, name='project_list'),
    
    # プロジェクト関連
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/<int:pk>/update/', views.project_update, name='project_update'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    
    # 収支記録関連
    path('projects/<int:project_pk>/records/create/', views.record_create, name='record_create'),
    path('records/<int:pk>/update/', views.record_update, name='record_update'),
    path('records/<int:pk>/delete/', views.record_delete, name='record_delete'), # この行が新しい
    
    # 共有ページ
    path('share/<uuid:token>/', views.share_project, name='share_project'),
]