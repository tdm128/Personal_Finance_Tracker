from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


CATEGORY_CHOICES = [
    ('food', '🍔 Food & Dining'),
    ('travel', '✈️ Travel'),
    ('shopping', '🛍️ Shopping'),
    ('entertainment', '🎬 Entertainment'),
    ('health', '💊 Health & Medical'),
    ('utilities', '⚡ Utilities & Bills'),
    ('education', '📚 Education'),
    ('housing', '🏠 Housing & Rent'),
    ('transport', '🚗 Transport'),
    ('savings', '💰 Savings'),
    ('salary', '💼 Salary / Income'),
    ('freelance', '💻 Freelance'),
    ('investment', '📈 Investment Returns'),
    ('gift', '🎁 Gift / Bonus'),
    ('other', '📦 Other'),
]

TYPE_CHOICES = [
    ('income', 'Income'),
    ('expense', 'Expense'),
]


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    date = models.DateField(default=timezone.now)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} - ${self.amount} ({self.transaction_type})"

    @property
    def is_income(self):
        return self.transaction_type == 'income'

    @property
    def category_display(self):
        return dict(CATEGORY_CHOICES).get(self.category, self.category)


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    monthly_limit = models.DecimalField(max_digits=12, decimal_places=2)
    month = models.IntegerField()
    year = models.IntegerField()

    class Meta:
        unique_together = ['user', 'category', 'month', 'year']

    def __str__(self):
        return f"{self.category} budget: ${self.monthly_limit}"


class AIInsight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='insights')
    insight_text = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)
    month = models.IntegerField()
    year = models.IntegerField()

    class Meta:
        ordering = ['-generated_at']

    def __str__(self):
        return f"Insight for {self.user.username} - {self.month}/{self.year}"
