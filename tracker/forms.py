from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Transaction, Budget, CATEGORY_CHOICES


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['title', 'amount', 'transaction_type', 'category', 'date', 'note']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Lunch at restaurant'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0.00', 'step': '0.01', 'min': '0'}),
            'transaction_type': forms.Select(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'note': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Optional note...'}),
        }


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'monthly_limit', 'month', 'year']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-input'}),
            'monthly_limit': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0.00', 'step': '0.01'}),
            'month': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 12}),
            'year': forms.NumberInput(attrs={'class': 'form-input', 'min': 2020, 'max': 2100}),
        }


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'your@email.com'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-input', 'placeholder': '••••••••'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input', 'placeholder': '••••••••'})


class FilterForm(forms.Form):
    MONTH_CHOICES = [('', 'All Months')] + [(i, f'{i:02d}') for i in range(1, 13)]
    YEAR_CHOICES = [('', 'All Years')] + [(y, y) for y in range(2020, 2031)]
    TYPE_CHOICES_FILTER = [('', 'All Types'), ('income', 'Income'), ('expense', 'Expense')]

    month = forms.ChoiceField(choices=MONTH_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-input'}))
    year = forms.ChoiceField(choices=YEAR_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-input'}))
    transaction_type = forms.ChoiceField(choices=TYPE_CHOICES_FILTER, required=False, widget=forms.Select(attrs={'class': 'form-input'}))
    category = forms.ChoiceField(choices=[('', 'All Categories')] + CATEGORY_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-input'}))
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Search transactions...'}))
