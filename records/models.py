from django.db import models

# Create your models here.
# records/models.py

import uuid
from django.db import models
from django.contrib.auth.models import User

# プロジェクトのモデル
class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='オーナー')
    name = models.CharField('プロジェクト名', max_length=100)
    share_token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='共有トークン')
    created_at = models.DateTimeField('作成日', auto_now_add=True)

    def __str__(self):
        return self.name

# 収支記録のモデル
class Record(models.Model):
    # 収支タイプ（勝ちか負けか）の選択肢
    WIN = 'WIN'
    LOSE = 'LOSE'
    RECORD_TYPE_CHOICES = [
        (WIN, '勝ち'),
        (LOSE, '負け'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='プロジェクト')
    record_type = models.CharField('収支タイプ', max_length=4, choices=RECORD_TYPE_CHOICES)
    amount = models.PositiveIntegerField('金額')
    # 修正後のコード
    character_name = models.CharField('キャラ名(任意)', max_length=100, blank=True, null=True)
    character_id = models.CharField('キャラID(任意)', max_length=100, blank=True, null=True)
    memo = models.TextField('メモ(任意)', blank=True, null=True)
    created_at = models.DateTimeField('記録日時', auto_now_add=True)

    def __str__(self):
        # 管理画面などで見やすくするための表示設定
        return f"{self.project.name} - {self.get_record_type_display()} {self.amount}円"
    
    # records/models.py の Record クラス

class Record(models.Model):
    # --- ▼▼▼ 収支タイプの選択肢に「リセット」を追加 ▼▼▼ ---
    WIN = 'WIN'
    LOSE = 'LOSE'
    RESET = 'RSET' # ← 新しく追加
    RECORD_TYPE_CHOICES = [
        (WIN, '勝ち'),
        (LOSE, '負け'),
        (RESET, 'リセット'), # ← 新しく追加
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name='プロジェクト')
    record_type = models.CharField('収支タイプ', max_length=4, choices=RECORD_TYPE_CHOICES)
    amount = models.PositiveIntegerField('金額') # リセット時はリセット前の収支額を記録
    character_name = models.CharField('キャラ名(任意)', max_length=100, blank=True, null=True)
    character_id = models.CharField('キャラID(任意)', max_length=100, blank=True, null=True)
    memo = models.TextField('メモ', blank=True, null=True)
    created_at = models.DateTimeField('記録日時', auto_now_add=True)

    def __str__(self):
        if self.record_type == self.RESET:
            return f"{self.project.name} - リセット実行"
        return f"{self.project.name} - {self.get_record_type_display()} {self.amount}円"