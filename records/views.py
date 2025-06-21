from django.shortcuts import render

# Create your views here.
# records/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Project

@login_required
def project_list(request):
    # ログインしているユーザーがオーナーであるプロジェクトのみを取得
    projects = Project.objects.filter(owner=request.user).order_by('-created_at')
    
    # 取得したプロジェクトリストをHTMLに渡す
    return render(request, 'records/project_list.html', {'projects': projects})

# records/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project
from .forms import ProjectForm # forms.py から ProjectForm をインポート

# project_listビューの下に、以下の関数を追加します

@login_required
def project_create(request):
    # プロジェクト数の上限チェック
    if request.user.project_set.count() >= 3:
        messages.error(request, '作成できるプロジェクトは3つまでです。')
        return redirect('records:project_list')

    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, '新しいプロジェクトを作成しました。')
            return redirect('records:project_list')
    else:
        form = ProjectForm()

    return render(request, 'records/project_create.html', {'form': form})

# records/views.py

from django.shortcuts import render, redirect, get_object_or_404 # get_object_or_404を追加
# ... (他のimport文)
from .models import Project, Record # Recordを追加
# ... (他のビュー関数)


@login_required
def project_detail(request, pk):
    # 指定されたpkを持ち、かつ自分がオーナーであるプロジェクトを取得。存在しなければ404エラー。
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    
    # そのプロジェクトに紐づく収支記録を全て取得
    records = project.record_set.all().order_by('-created_at')
    
    # 合計収支を計算
    total_win = sum(record.amount for record in records if record.record_type == 'WIN')
    total_lose = sum(record.amount for record in records if record.record_type == 'LOSE')
    total_balance = total_win - total_lose
    
    context = {
        'project': project,
        'records': records,
        'total_balance': total_balance,
    }
    
    return render(request, 'records/project_detail.html', context)

# records/views.py
# ... (他のimport文)
from .forms import ProjectForm, RecordForm # RecordForm をインポートに追加
# ... (他のビュー関数)

@login_required
def record_create(request, project_pk):
    # 対象のプロジェクトを取得（もちろん、自分がオーナーのものしか取得できない）
    project = get_object_or_404(Project, pk=project_pk, owner=request.user)
    
    if request.method == 'POST':
        form = RecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.project = project  # この記録がどのプロジェクトに属するかを設定
            record.save()
            messages.success(request, '収支を記録しました。')
            # 記録を追加したプロジェクトの詳細ページに戻る
            return redirect('records:project_detail', pk=project.pk)
    else:
        form = RecordForm()
        
    context = {
        'form': form,
        'project': project,
    }
    return render(request, 'records/record_create.html', context)


# records/views.py
# ... (他のビュー関数の下に追加)

def share_project(request, token):
    # 指定された共有トークンを持つプロジェクトを取得。存在しなければ404エラー。
    project = get_object_or_404(Project, share_token=token)
    
    # --- 以下のロジックは project_detail と全く同じ ---
    # そのプロジェクトに紐づく収支記録を全て取得
    records = project.record_set.all().order_by('-created_at')
    
    # 合計収支を計算
    total_win = sum(record.amount for record in records if record.record_type == 'WIN')
    total_lose = sum(record.amount for record in records if record.record_type == 'LOSE')
    total_balance = total_win - total_lose
    
    context = {
        'project': project,
        'records': records,
        'total_balance': total_balance,
    }
    
    return render(request, 'records/share_project.html', context)

# records/views.py
# ... (他のビュー関数の下に追加)

@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'プロジェクトを削除しました。')
        return redirect('records:project_list')
    
    return render(request, 'records/project_confirm_delete.html', {'project': project})

# records/views.py
# ... (他のビュー関数の下に追加)

@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'プロジェクト名を更新しました。')
            return redirect('records:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(request, 'records/project_update.html', {'form': form, 'project': project})

# records/views.py

# ... (他のimport文はそのまま)

@login_required
def project_list(request):
    # まず、ログインしているユーザーのプロジェクトを全て取得
    projects = Project.objects.filter(owner=request.user).order_by('-created_at')
    
    # 各プロジェクトの合計収支を計算して、プロジェクトオブジェクトに新しい属性として追加する
    for project in projects:
        records = project.record_set.all()
        total_win = sum(record.amount for record in records if record.record_type == 'WIN')
        total_lose = sum(record.amount for record in records if record.record_type == 'LOSE')
        project.total_balance = total_win - total_lose
    
    # 計算結果が追加されたプロジェクトリストをHTMLに渡す
    return render(request, 'records/project_list.html', {'projects': projects})

# records/views.py
# ... (他のビュー関数の下に追加)

@login_required
def record_update(request, pk):
    # 修正対象の記録を取得。ただし、その記録が自分のプロジェクトのものであることを確認
    record = get_object_or_404(Record, pk=pk, project__owner=request.user)
    
    if request.method == 'POST':
        # 既存のインスタンスを上書きする形でフォームを初期化
        form = RecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, '記録を修正しました。')
            # 修正した記録が属するプロジェクトの詳細ページに戻る
            return redirect('records:project_detail', pk=record.project.pk)
    else:
        # 既存のインスタンスを元にフォームを初期化
        form = RecordForm(instance=record)
        
    context = {
        'form': form,
        'record': record, # テンプレートで record オブジェクトを使えるように渡す
    }
    return render(request, 'records/record_update.html', context)

# records/views.py
# ... (他のビュー関数の下に追加)

@login_required
def record_delete(request, pk):
    # 削除対象の記録を取得（もちろん、自分がオーナーのプロジェクトの記録のみ）
    record = get_object_or_404(Record, pk=pk, project__owner=request.user)
    
    if request.method == 'POST':
        project_pk = record.project.pk # リダイレクト用にプロジェクトのpkを保持
        record.delete()
        messages.success(request, '記録を削除しました。')
        return redirect('records:project_detail', pk=project_pk)
    
    return render(request, 'records/record_confirm_delete.html', {'record': record})