# records/forms.py の新しい内容

from django import forms
from .models import Project, Record

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name']
        labels = {
            'name': 'プロジェクト名',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # このフォームの全ての入力欄に 'form-control' クラスを追加
        self.fields['name'].widget.attrs['class'] = 'form-control'


class RecordForm(forms.ModelForm):
    class Meta:
        model = Record
        fields = ['record_type', 'amount', 'character_name', 'character_id', 'memo']
        labels = {
            'record_type': '収支タイプ',
            'amount': '金額(万ゴールド)',
            'character_name': 'キャラ名(任意)',
            'character_id': 'キャラID(任意)',
            'memo': 'メモ(任意)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # このフォームの全ての入力欄に Bootstrap のクラスを追加していく
        self.fields['record_type'].widget.attrs['class'] = 'form-select'
        self.fields['amount'].widget.attrs['class'] = 'form-control'
        self.fields['character_name'].widget.attrs['class'] = 'form-control'
        self.fields['character_id'].widget.attrs['class'] = 'form-control'
        self.fields['memo'].widget.attrs['class'] = 'form-control'