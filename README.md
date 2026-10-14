# 💸 I Don't Know How To Spend

> A full-featured personal expense tracker built with Django — with AI-powered spending insights via Claude.

![Theme: Dark green dollar aesthetic]

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Create Superuser (optional)
```bash
python manage.py createsuperuser
```

### 4. Start Development Server
```bash
python manage.py runserver
```

Visit → http://127.0.0.1:8000

---

## 📁 Project Structure

```
idkhowtospend/
├── idkhowtospend/          # Project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── tracker/                # Main app
│   ├── models.py           # Transaction, Budget, AIInsight
│   ├── views.py            # All CRUD + reports + AI views
│   ├── forms.py            # Django forms
│   ├── urls.py             # URL routing
│   └── admin.py            # Admin panel config
├── templates/tracker/      # HTML templates
│   ├── base.html           # Sidebar layout + theme
│   ├── dashboard.html      # Main dashboard with charts
│   ├── transaction_list.html
│   ├── transaction_form.html
│   ├── transaction_confirm_delete.html
│   ├── reports.html        # Annual reports with charts
│   ├── budget_list.html
│   ├── budget_form.html
│   ├── ai_insights.html    # 🤖 Claude AI analysis
│   ├── login.html
│   └── register.html
├── static/                 # Static files (CSS/JS)
├── manage.py
└── requirements.txt
```

---

## ✨ Features

### 💰 Transactions (Full CRUD)
- Add income or expenses
- 15 categories: Food, Travel, Shopping, Health, etc.
- Date, title, amount, optional notes
- Filter by type, category, month, year, search

### 🎯 Budget Tracking
- Set monthly limits per category
- Visual progress bars on dashboard
- Over-budget warnings (turns red)

### 📊 Reports & Charts (Chart.js)
- **Dashboard**: Income vs Expense bar chart (last 6 months)
- **Dashboard**: Spending by category donut chart
- **Reports**: Full year monthly bar chart
- **Reports**: Monthly savings trend line chart
- **Reports**: Top spending categories pie chart

### 🤖 AI Insights (Claude API)
- Sends your spending data to Claude (claude-sonnet-4)
- Gets personalized analysis:
  - Spending health overview
  - Areas of concern
  - Actionable improvement tips
  - Next month financial goal
- Save insights for future reference

---

## 🎨 Design Theme
- **Dark green** palette inspired by dollar bills
- `Space Mono` monospace for numbers/money
- `Syne` sans-serif for UI text
- Dollar sign (`$`) background pattern
- Gold accent for balance/savings

---

## 🧠 What You Learn

| Concept | Where |
|---|---|
| Django Models | `tracker/models.py` |
| CRUD Views | `tracker/views.py` |
| Forms & Validation | `tracker/forms.py` |
| Aggregations (Sum, Count) | `views.py` → dashboard, reports |
| ORM Filters (Q objects) | `transaction_list` view |
| Chart.js Visualization | `dashboard.html`, `reports.html` |
| Claude AI API | `ai_insights.html` |
| User Authentication | Built-in Django auth |
| URL Routing | `tracker/urls.py` |
| Template Inheritance | All templates extend `base.html` |

---

## 🔮 Future Improvements
- [ ] Recurring transactions
- [ ] CSV export
- [ ] Email monthly reports
- [ ] Multiple currencies
- [ ] Mobile-responsive sidebar
- [ ] Dark/light theme toggle

---

## 📝 Notes
- SQLite by default — switch to PostgreSQL for production
- AI Insights use the Anthropic API (no API key needed in claude.ai artifacts)
- All data is per-user (login required for all views)
