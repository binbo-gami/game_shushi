# records/admin.py の新しい内容

from django.contrib import admin
from .models import Project, Record

# Projectモデルの管理サイト表示をカスタマイズ
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    # 一覧ページに表示する項目
    list_display = ('name', 'owner', 'created_at')
    
    # ページの右側に表示される絞り込みフィルター
    list_filter = ('owner',)
    
    # ページの上部に表示される検索バーの対象項目
    search_fields = ('name', 'owner__username')
    
    # 並び順（作成日の降順 = 新しいものが上）
    ordering = ('-created_at',)


# Recordモデルの管理サイト表示をカスタマイズ
@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    # 一覧ページに表示する項目
    list_display = ('get_project_name', 'record_type', 'amount', 'character_name', 'created_at')
    
    # 絞り込みフィルター
    list_filter = ('project', 'record_type', 'created_at')

    # 検索バーの対象項目
    search_fields = ('character_name', 'character_id', 'memo', 'project__name')
    
    # 並び順
    ordering = ('-created_at',)
    
    # 編集画面のレイアウトを整える
    fieldsets = (
        ('基本情報', {
            'fields': ('project', 'record_type', 'amount')
        }),
        ('キャラクター・メモ情報（任意）', {
            'fields': ('character_name', 'character_id', 'memo'),
            'classes': ('collapse',) # デフォルトでこのセクションを折りたたむ
        }),
    )

    # 一覧ページでプロジェクト名を表示するためのカスタムメソッド
    def get_project_name(self, obj):
        return obj.project.name
    get_project_name.short_description = 'プロジェクト名' # 列の見出し
    get_project_name.admin_order_field = 'project' # この列での並び替えを有効にする