from django.contrib import admin
from .models import Transaction, Budget, AIInsight


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['title', 'amount', 'transaction_type', 'category', 'date', 'user']
    list_filter = ['transaction_type', 'category', 'date']
    search_fields = ['title', 'note']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'monthly_limit', 'month', 'year']


@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = ['user', 'month', 'year', 'generated_at']
