# records/views.py の新しい完全な内容

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum
from .models import Project, Record
from .forms import ProjectForm, RecordForm
from django.http import JsonResponse

# --- ▼▼▼ 合計収支を計算するための、新しい共通関数 ▼▼▼ ---
def calculate_balance(project):
    """
    最新のリセット記録以降の収支を合計して返す関数
    """
    # 最新のリセット記録を探す
    latest_reset = project.record_set.filter(record_type=Record.RESET).order_by('-created_at').first()
    
    # リセット記録があれば、それ以降の記録を対象にする
    if latest_reset:
        records_to_sum = project.record_set.filter(created_at__gt=latest_reset.created_at)
    else:
        # なければ全ての記録を対象にする
        records_to_sum = project.record_set.all()

    # 対象記録の勝ちと負けを合計
    total_win = records_to_sum.filter(record_type=Record.WIN).aggregate(total=Sum('amount'))['total'] or 0
    total_lose = records_to_sum.filter(record_type=Record.LOSE).aggregate(total=Sum('amount'))['total'] or 0
    
    return total_win - total_lose

# --- ▼▼▼ これ以降の各ビューも、新しいロジックに合わせて修正 ▼▼▼ ---

@login_required
def project_list(request):
    projects = Project.objects.filter(owner=request.user).order_by('-created_at')
    # 新しい計算関数を呼び出すように変更
    for project in projects:
        project.total_balance = calculate_balance(project)
    return render(request, 'records/project_list.html', {'projects': projects})

# records/views.py の project_detail 関数

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    
    # このプロジェクトの全収支記録を基本データとして取得
    all_records = project.record_set.all().order_by('-created_at')
    
    # --- ▼▼▼ 日付フィルタと、その日の収支計算ロジック ▼▼▼ ---
    target_date_str = request.GET.get('date')
    records_to_display = all_records  # 表示するレコード（デフォルトは全て）
    target_date = None                # 選択された日付（デフォルトはなし）
    daily_balance = None              # その日の収支（デフォルトはなし）

    if target_date_str:
        from django.utils.dateparse import parse_date
        from django.db.models import Sum

        target_date = parse_date(target_date_str)
        if target_date:
            # 1. 記録をフィルタリングする
            records_to_display = all_records.filter(created_at__date=target_date)
            
            # 2. その日の収支だけを計算する
            daily_win = records_to_display.filter(record_type=Record.WIN).aggregate(total=Sum('amount'))['total'] or 0
            daily_lose = records_to_display.filter(record_type=Record.LOSE).aggregate(total=Sum('amount'))['total'] or 0
            daily_balance = daily_win - daily_lose
    # --- ▲▲▲ ここまで ▲▲▲ ---

    # プロジェクト全体の合計収支は常に計算する
    total_balance = calculate_balance(project)
    
    context = {
        'project': project,
        'records': records_to_display,  # 表示用レコード
        'total_balance': total_balance, # 全体の合計収支
        'target_date': target_date,     # 選択された日付
        'daily_balance': daily_balance, # その日の合計収支
    }
    
    return render(request, 'records/project_detail.html', context)

@login_required
def project_create(request):
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

@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'プロジェクトを削除しました。')
        return redirect('records:project_list')
    return render(request, 'records/project_confirm_delete.html', {'project': project})

# --- ▼▼▼ リセット機能のロジックを全面的に変更 ▼▼▼ ---
@login_required
def project_reset_balance(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == 'POST':
        # 現在の合計収支を計算
        total_balance = calculate_balance(project)
        
        # 新しい「リセット」タイプの記録を作成
        Record.objects.create(
            project=project,
            record_type=Record.RESET,
            amount=abs(total_balance), # リセット時の金額を記録（絶対値）
            memo=f'収支をリセットしました。 (リセット前: {total_balance}万ゴールド)'
        )
        messages.success(request, '合計収支をリセットしました。')
    return redirect('records:project_detail', pk=project.pk)

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'アカウントを作成しました。ログインしてください。')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def record_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk, owner=request.user)
    # 新しい計算関数を呼び出すように変更
    total_balance = calculate_balance(project)
    if request.method == 'POST':
        form = RecordForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['record_type'] == Record.RESET:
                messages.error(request, '無効な操作です。')
            else:
                record = form.save(commit=False)
                record.project = project
                record.save()
                messages.success(request, '収支を記録しました。')
                return redirect('records:project_detail', pk=project.pk)
    else:
        form = RecordForm()
    context = {'form': form, 'project': project, 'total_balance': total_balance}
    return render(request, 'records/record_create.html', context)

@login_required
def record_update(request, pk):
    record = get_object_or_404(Record, pk=pk, project__owner=request.user)
    project = record.project
    # 新しい計算関数を呼び出すように変更
    total_balance = calculate_balance(project)
    if request.method == 'POST':
        form = RecordForm(request.POST, instance=record)
        if form.is_valid():
            if form.cleaned_data['record_type'] == Record.RESET:
                messages.error(request, 'リセット記録は修正できません。')
            else:
                form.save()
                messages.success(request, '記録を修正しました。')
                return redirect('records:project_detail', pk=record.project.pk)
    else:
        form = RecordForm(instance=record)
    context = {'form': form, 'record': record, 'total_balance': total_balance}
    return render(request, 'records/record_update.html', context)

@login_required
def record_delete(request, pk):
    record = get_object_or_404(Record, pk=pk, project__owner=request.user)
    if request.method == 'POST':
        project_pk = record.project.pk
        record.delete()
        messages.success(request, '記録を削除しました。')
        return redirect('records:project_detail', pk=project_pk)
    return render(request, 'records/record_confirm_delete.html', {'record': record})

def share_project(request, token):
    project = get_object_or_404(Project, share_token=token)
    records = project.record_set.all().order_by('-created_at')
    # 新しい計算関数を呼び出すように変更
    total_balance = calculate_balance(project)
    context = {'project': project, 'records': records, 'total_balance': total_balance}
    return render(request, 'records/share_project.html', context)

@login_required
def calculate_win_rate(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    
    # 日付フィルタのパラメータを取得
    target_date_str = request.GET.get('date')
    
    # 対象となるレコードセットを準備
    records_to_calculate = project.record_set.exclude(record_type=Record.RESET)

    if target_date_str:
        from django.utils.dateparse import parse_date
        target_date = parse_date(target_date_str)
        if target_date:
            # 日付が指定されていれば、その日のレコードに絞り込む
            records_to_calculate = records_to_calculate.filter(created_at__date=target_date)

    # 勝ちと負けの数を数える
    win_count = records_to_calculate.filter(record_type=Record.WIN).count()
    lose_count = records_to_calculate.filter(record_type=Record.LOSE).count()
    
    total_games = win_count + lose_count
    
    # 勝率を計算（0除算を避ける）
    if total_games > 0:
        win_rate = (win_count / total_games) * 100
    else:
        win_rate = 0
        
    # JSON形式でデータを返す
    return JsonResponse({
        'win_count': win_count,
        'lose_count': lose_count,
        'total_games': total_games,
        'win_rate': f'{win_rate:.2f}' # 小数点第2位まで表示
    })
