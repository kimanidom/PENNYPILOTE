from flask import Flask, render_template_string, request, redirect, url_for
from lib.db import session, init_db
from lib.models import User, Category, Transaction
from sqlalchemy import func

app = Flask(__name__)

# Initialize DB on start
init_db()

# --- HTML TEMPLATES (Embedded for simplicity) ---
base_html = """
<!DOCTYPE html>
<html>
<head>
    <title>PennyPilote</title>
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        nav { background: #333; padding: 10px; margin-bottom: 20px; }
        nav a { color: white; text-decoration: none; margin-right: 15px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .form-group { margin-bottom: 10px; }
        input, select { padding: 5px; width: 100%; }
        button { background: #28a745; color: white; border: none; padding: 10px 20px; cursor: pointer; }
        .expense { color: red; }
        .income { color: green; }
    </style>
</head>
<body>
    <h1>✈️ PennyPilote Finance</h1>
    <nav>
        <a href="/">Dashboard</a>
        <a href="/users">Users</a>
        <a href="/categories">Categories</a>
        <a href="/transactions">Transactions</a>
    </nav>
    {% block content %}{% endblock %}
</body>
</html>
"""

dashboard_html = base_html + """
{% block content %}
    <h2>Spending Summary</h2>
    <table>
        <tr><th>Category</th><th>Total Amount</th></tr>
        {% for row in summary %}
        <tr>
            <td>{{ row,[object Object], }}</td>
            <td>${{ row,[object Object], }}</td>
        </tr>
        {% endfor %}
    </table>
{% endblock %}
"""

users_html = base_html + """
{% block content %}
    <h2>Manage Users</h2>
    <form method="POST" style="background:#f9f9f9; padding:15px;">
        <div class="form-group"><input name="name" placeholder="Name" required></div>
        <div class="form-group"><input name="email" placeholder="Email" required></div>
        <button type="submit">Create User</button>
    </form>
    
    <h3>Existing Users</h3>
    <ul>
    {% for user in users %}
        <li>{{ user.name }} ({{ user.email }})</li>
    {% endfor %}
    </ul>
{% endblock %}
"""

categories_html = base_html + """
{% block content %}
    <h2>Manage Categories</h2>
    <form method="POST" style="background:#f9f9f9; padding:15px;">
        <div class="form-group"><input name="name" placeholder="Category Name (e.g. Rent)" required></div>
        <div class="form-group"><input name="desc" placeholder="Description"></div>
        <button type="submit">Add Category</button>
    </form>
    
    <h3>Existing Categories</h3>
    <ul>
    {% for cat in categories %}
        <li>{{ cat.name }}</li>
    {% endfor %}
    </ul>
{% endblock %}
"""

transactions_html = base_html + """
{% block content %}
    <h2>Transactions</h2>
    <form method="POST" style="background:#f9f9f9; padding:15px; display:grid; gap:10px;">
        <select name="user_id">
            {% for u in users %}<option value="{{u.id}}">{{u.name}}</option>{% endfor %}
        </select>
        <select name="category_id">
            {% for c in categories %}<option value="{{c.id}}">{{c.name}}</option>{% endfor %}
        </select>
        <input type="number" step="0.01" name="amount" placeholder="Amount (+/-)" required>
        <input type="date" name="date" required>
        <input name="desc" placeholder="Description">
        <button type="submit">Add Transaction</button>
    </form>

    <h3>History</h3>
    <table>
        <tr><th>Date</th><th>User</th><th>Category</th><th>Amount</th><th>Desc</th></tr>
        {% for t in transactions %}
        <tr>
            <td>{{ t.date }}</td>
            <td>{{ t.user.name }}</td>
            <td>{{ t.category.name }}</td>
            <td class="{{ 'income' if t.amount > 0 else 'expense' }}">${{ t.amount }}</td>
            <td>{{ t.description }}</td>
        </tr>
        {% endfor %}
    </table>
{% endblock %}
"""

# --- ROUTES ---

@app.route('/')
def index():
    # Summary Logic
    summary = session.query(Category.name, func.sum(Transaction.amount)).join(Transaction).group_by(Category.name).all()
    return render_template_string(dashboard_html, summary=summary)

@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        new_user = User(name=request.form['name'], email=request.form['email'])
        session.add(new_user)
        session.commit()
        return redirect(url_for('users'))
    
    all_users = session.query(User).all()
    return render_template_string(users_html, users=all_users)

@app.route('/categories', methods=['GET', 'POST'])
def categories():
    if request.method == 'POST':
        new_cat = Category(name=request.form['name'], description=request.form['desc'])
        session.add(new_cat)
        session.commit()
        return redirect(url_for('categories'))
    
    all_cats = session.query(Category).all()
    return render_template_string(categories_html, categories=all_cats)

@app.route('/transactions', methods=['GET', 'POST'])
def transactions():
    if request.method == 'POST':
        from datetime import datetime
        date_obj = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        
        new_trans = Transaction(
            amount=float(request.form['amount']),
            date=date_obj,
            description=request.form['desc'],
            user_id=int(request.form['user_id']),
            category_id=int(request.form['category_id'])
        )
        session.add(new_trans)
        session.commit()
        return redirect(url_for('transactions'))
    
    # Get data for dropdowns and list
    users = session.query(User).all()
    cats = session.query(Category).all()
    trans = session.query(Transaction).order_by(Transaction.date.desc()).all()
    
    return render_template_string(transactions_html, users=users, categories=cats, transactions=trans)

if __name__ == '__main__':
    # This makes the app "Go Live" on your local machine
    app.run(debug=True, port=5000)