from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import JsonResponse
from django.utils import timezone
import json
import calendar
from datetime import date

from .models import Transaction, Budget, AIInsight, CATEGORY_CHOICES
from .forms import TransactionForm, BudgetForm, RegisterForm, FilterForm


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to IDKH2S, {user.username}! 💸')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'tracker/register.html', {'form': form})


@login_required
def dashboard(request):
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    transactions = Transaction.objects.filter(
        user=request.user, date__month=month, date__year=year
    )

    total_income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    # Category breakdown for expenses
    expense_by_category = (
        transactions.filter(transaction_type='expense')
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    category_labels = []
    category_data = []
    category_dict = dict(CATEGORY_CHOICES)
    for item in expense_by_category:
        cat_display = category_dict.get(item['category'], item['category'])
        category_labels.append(cat_display)
        category_data.append(float(item['total']))

    # Monthly trend (last 6 months)
    monthly_trend = []
    for i in range(5, -1, -1):
        m = month - i
        y = year
        while m <= 0:
            m += 12
            y -= 1
        t = Transaction.objects.filter(user=request.user, date__month=m, date__year=y)
        inc = t.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        exp = t.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_trend.append({
            'month': calendar.month_abbr[m],
            'income': float(inc),
            'expense': float(exp),
        })

    recent_transactions = transactions[:8]
    budgets = Budget.objects.filter(user=request.user, month=month, year=year)

    # Budget progress
    budget_progress = []
    for budget in budgets:
        spent = transactions.filter(
            transaction_type='expense', category=budget.category
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        pct = min(float(spent) / float(budget.monthly_limit) * 100, 100) if budget.monthly_limit else 0
        budget_progress.append({
            'budget': budget,
            'spent': spent,
            'pct': round(pct, 1),
            'over': spent > budget.monthly_limit,
        })

    # Latest AI insight
    latest_insight = AIInsight.objects.filter(
        user=request.user, month=month, year=year
    ).first()

    months_list = [(i, calendar.month_name[i]) for i in range(1, 13)]
    years_list = list(range(2020, today.year + 2))

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'recent_transactions': recent_transactions,
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        'monthly_trend': json.dumps(monthly_trend),
        'budget_progress': budget_progress,
        'latest_insight': latest_insight,
        'selected_month': month,
        'selected_year': year,
        'months_list': months_list,
        'years_list': years_list,
        'current_month_name': calendar.month_name[month],
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def transaction_list(request):
    form = FilterForm(request.GET)
    transactions = Transaction.objects.filter(user=request.user)

    if form.is_valid():
        if form.cleaned_data['month']:
            transactions = transactions.filter(date__month=form.cleaned_data['month'])
        if form.cleaned_data['year']:
            transactions = transactions.filter(date__year=form.cleaned_data['year'])
        if form.cleaned_data['transaction_type']:
            transactions = transactions.filter(transaction_type=form.cleaned_data['transaction_type'])
        if form.cleaned_data['category']:
            transactions = transactions.filter(category=form.cleaned_data['category'])
        if form.cleaned_data['search']:
            transactions = transactions.filter(
                Q(title__icontains=form.cleaned_data['search']) |
                Q(note__icontains=form.cleaned_data['search'])
            )

    total_income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    return render(request, 'tracker/transaction_list.html', {
        'transactions': transactions,
        'form': form,
        'total_income': total_income,
        'total_expense': total_expense,
    })


@login_required
def transaction_add(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.user = request.user
            t.save()
            messages.success(request, '✅ Transaction added!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(initial={'date': date.today()})
    return render(request, 'tracker/transaction_form.html', {'form': form, 'action': 'Add'})


@login_required
def transaction_edit(request, pk):
    t = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=t)
        if form.is_valid():
            form.save()
            messages.success(request, '✏️ Transaction updated!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=t)
    return render(request, 'tracker/transaction_form.html', {'form': form, 'action': 'Edit', 'transaction': t})


@login_required
def transaction_delete(request, pk):
    t = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        t.delete()
        messages.success(request, '🗑️ Transaction deleted.')
        return redirect('transaction_list')
    return render(request, 'tracker/transaction_confirm_delete.html', {'transaction': t})


@login_required
def reports(request):
    today = date.today()
    year = int(request.GET.get('year', today.year))

    # Full year monthly data
    monthly_data = []
    for m in range(1, 13):
        t = Transaction.objects.filter(user=request.user, date__month=m, date__year=year)
        inc = float(t.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0)
        exp = float(t.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0)
        monthly_data.append({'month': calendar.month_abbr[m], 'income': inc, 'expense': exp, 'savings': inc - exp})

    # Top spending categories this year
    top_categories = (
        Transaction.objects.filter(user=request.user, date__year=year, transaction_type='expense')
        .values('category')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')[:8]
    )

    cat_dict = dict(CATEGORY_CHOICES)
    pie_labels = [cat_dict.get(c['category'], c['category']) for c in top_categories]
    pie_data = [float(c['total']) for c in top_categories]

    yearly_income = sum(m['income'] for m in monthly_data)
    yearly_expense = sum(m['expense'] for m in monthly_data)
    yearly_savings = yearly_income - yearly_expense

    years_list = list(range(2020, today.year + 2))

    return render(request, 'tracker/reports.html', {
        'monthly_data': json.dumps(monthly_data),
        'pie_labels': json.dumps(pie_labels),
        'pie_data': json.dumps(pie_data),
        'yearly_income': yearly_income,
        'yearly_expense': yearly_expense,
        'yearly_savings': yearly_savings,
        'selected_year': year,
        'years_list': years_list,
    })


@login_required
def budget_list(request):
    today = date.today()
    budgets = Budget.objects.filter(user=request.user).order_by('-year', '-month')
    return render(request, 'tracker/budget_list.html', {'budgets': budgets})


@login_required
def budget_add(request):
    today = date.today()
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            b = form.save(commit=False)
            b.user = request.user
            b.save()
            messages.success(request, '💰 Budget set!')
            return redirect('budget_list')
    else:
        form = BudgetForm(initial={'month': today.month, 'year': today.year})
    return render(request, 'tracker/budget_form.html', {'form': form, 'action': 'Add'})


@login_required
def budget_edit(request, pk):
    b = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=b)
        if form.is_valid():
            form.save()
            messages.success(request, '✏️ Budget updated!')
            return redirect('budget_list')
    else:
        form = BudgetForm(instance=b)
    return render(request, 'tracker/budget_form.html', {'form': form, 'action': 'Edit'})


@login_required
def budget_delete(request, pk):
    b = get_object_or_404(Budget, pk=pk, user=request.user)
    if request.method == 'POST':
        b.delete()
        messages.success(request, '🗑️ Budget deleted.')
    return redirect('budget_list')


@login_required
def ai_insights(request):
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    transactions = Transaction.objects.filter(user=request.user, date__month=month, date__year=year)
    total_income = float(transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0)
    total_expense = float(transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0)

    cat_dict = dict(CATEGORY_CHOICES)
    expense_by_cat = (
        transactions.filter(transaction_type='expense')
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    spending_summary = [
        {'category': cat_dict.get(e['category'], e['category']), 'amount': float(e['total'])}
        for e in expense_by_cat
    ]

    existing_insights = AIInsight.objects.filter(user=request.user, month=month, year=year)
    months_list = [(i, calendar.month_name[i]) for i in range(1, 13)]

    context = {
        'existing_insights': existing_insights,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': total_income - total_expense,
        'spending_summary': spending_summary,
        'spending_summary_json': json.dumps(spending_summary),
        'selected_month': month,
        'selected_year': year,
        'month_name': calendar.month_name[month],
        'months_list': months_list,
        'years_list': list(range(2020, today.year + 2)),
    }
    return render(request, 'tracker/ai_insights.html', context)


@login_required
def save_ai_insight(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        insight_text = data.get('insight', '')
        month = data.get('month', date.today().month)
        year = data.get('year', date.today().year)
        if insight_text:
            AIInsight.objects.create(
                user=request.user,
                insight_text=insight_text,
                month=month,
                year=year,
            )
            return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def api_monthly_data(request):
    """API endpoint for chart data"""
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    transactions = Transaction.objects.filter(user=request.user, date__month=month, date__year=year)
    cat_dict = dict(CATEGORY_CHOICES)
    expense_by_cat = (
        transactions.filter(transaction_type='expense')
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    return JsonResponse({
        'labels': [cat_dict.get(e['category'], e['category']) for e in expense_by_cat],
        'data': [float(e['total']) for e in expense_by_cat],
    })
