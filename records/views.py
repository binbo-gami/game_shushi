# records/views.py の最終的な正しい内容

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .models import Project, Record
from .forms import ProjectForm, RecordForm

@login_required
def project_list(request):
    projects = Project.objects.filter(owner=request.user).order_by('-created_at')
    for project in projects:
        records = project.record_set.all()
        total_win = sum(record.amount for record in records if record.record_type == 'WIN')
        total_lose = sum(record.amount for record in records if record.record_type == 'LOSE')
        project.total_balance = total_win - total_lose
    return render(request, 'records/project_list.html', {'projects': projects})

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    records = project.record_set.all().order_by('-created_at')
    total_win = sum(record.amount for record in records if record.record_type == 'WIN')
    total_lose = sum(record.amount for record in records if record.record_type == 'LOSE')
    total_balance = total_win - total_lose
    context = {
        'project': project,
        'records': records,
        'total_balance': total_balance,
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
    # ↓↓ 修正対象でした ↓↓
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
    # ↓↓ 修正対象でした ↓↓
    return render(request, 'records/project_update.html', {'form': form, 'project': project})

@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'プロジェクトを削除しました。')
        return redirect('records:project_list')
    # ↓↓ 修正対象でした ↓↓
    return render(request, 'records/project_confirm_delete.html', {'project': project})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'アカウントを作成しました。ログインしてください。')
            return redirect('login')
    else:
        form = UserCreationForm()
    # このファイルは `templates/registration/` にあるので、このままでOK
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def record_create(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk, owner=request.user)
    records = project.record_set.all()
    total_win = sum(record.amount for record in records if record.record_type == 'WIN')
    total_lose = sum(record.amount for record in records if record.record_type == 'LOSE')
    total_balance = total_win - total_lose
    if request.method == 'POST':
        form = RecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.project = project
            record.save()
            messages.success(request, '収支を記録しました。')
            return redirect('records:project_detail', pk=project.pk)
    else:
        form = RecordForm()
    context = {
        'form': form,
        'project': project,
        'total_balance': total_balance,
    }
    # ↓↓ 今回エラーが出たのはここです。「records/」を追加します ↓↓
    return render(request, 'records/record_create.html', context)

@login_required
def record_update(request, pk):
    record = get_object_or_404(Record, pk=pk, project__owner=request.user)
    project = record.project
    records = project.record_set.all()
    total_win = sum(record.amount for record in records if record.record_type == 'WIN')
    total_lose = sum(record.amount for record in records if record.record_type == 'LOSE')
    total_balance = total_win - total_lose
    if request.method == 'POST':
        form = RecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, '記録を修正しました。')
            return redirect('records:project_detail', pk=record.project.pk)
    else:
        form = RecordForm(instance=record)
    context = {
        'form': form,
        'record': record,
        'total_balance': total_balance,
    }
    # ↓↓ 修正対象でした。「records/」を追加します ↓↓
    return render(request, 'records/record_update.html', context)

@login_required
def record_delete(request, pk):
    record = get_object_or_404(Record, pk=pk, project__owner=request.user)
    if request.method == 'POST':
        project_pk = record.project.pk
        record.delete()
        messages.success(request, '記録を削除しました。')
        return redirect('records:project_detail', pk=project_pk)
    # ↓↓ 修正対象でした。「records/」を追加します ↓↓
    return render(request, 'records/record_confirm_delete.html', {'record': record})

def share_project(request, token):
    project = get_object_or_404(Project, share_token=token)
    records = project.record_set.all().order_by('-created_at')
    total_win = sum(record.amount for record in records if record.record_type == 'WIN')
    total_lose = sum(record.amount for record in records if record.record_type == 'LOSE')
    total_balance = total_win - total_lose
    context = {
        'project': project,
        'records': records,
        'total_balance': total_balance,
    }
    # ↓↓ 修正対象でした ↓↓
    return render(request, 'records/share_project.html', context)