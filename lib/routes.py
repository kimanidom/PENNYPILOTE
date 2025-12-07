from flask import Blueprint, request, jsonify
from .models import db, Account, Category, Transaction
import datetime

api = Blueprint("api", __name__)

# --- User Endpoints ---
@api.route("/users", methods=["POST"])
def create_user():
    data = request.json
    user = Account(name=data["name"], email=data["email"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created", "user": {"id": user.id, "name": user.name, "email": user.email}})

@api.route("/users", methods=["GET"])
def list_users():
    users = Account.query.all()
    return jsonify([{"id": u.id, "name": u.name, "email": u.email} for u in users])

# --- Category Endpoints ---
@api.route("/categories", methods=["POST"])
def create_category():
    data = request.json
    category = Category(name=data["name"])
    db.session.add(category)
    db.session.commit()
    return jsonify({"message": "Category created", "category": {"id": category.id, "name": category.name}})

@api.route("/categories", methods=["GET"])
def list_categories():
    categories = Category.query.all()
    return jsonify([{"id": c.id, "name": c.name} for c in categories])

# --- Transaction Endpoints ---
@api.route("/transactions", methods=["POST"])
def add_transaction():
    data = request.json
    date = datetime.datetime.strptime(data.get("date"), "%Y-%m-%d").date() if data.get("date") else datetime.date.today()
    transaction = Transaction(
        amount=data["amount"],
        account_id=data["account_id"],
        category_id=data.get("category_id"),
        date=date,
        description=data.get("description")
    )
    db.session.add(transaction)
    db.session.commit()
    return jsonify({"message": "Transaction added", "transaction_id": transaction.id})

@api.route("/transactions", methods=["GET"])
def list_transactions():
    transactions = Transaction.query.all()
    result = []
    for t in transactions:
        result.append({
            "id": t.id,
            "amount": t.amount,
            "date": str(t.date),
            "description": t.description,
            "account_id": t.account_id,
            "category": t.category.name if t.category else None
        })
    return jsonify(result)

# --- Monthly Summary ---
@api.route("/summary/<int:user_id>/<int:year>/<int:month>", methods=["GET"])
def monthly_summary(user_id, year, month):
    from sqlalchemy import extract
    transactions = Transaction.query.filter(
        Transaction.account_id==user_id,
        extract("year", Transaction.date)==year,
        extract("month", Transaction.date)==month
    ).all()
    summary = {}
    for t in transactions:
        key = t.category.name if t.category else "Uncategorized"
        summary[key] = summary.get(key, 0) + t.amount
    return jsonify(summary)

# --- Filtering / Search ---
@api.route("/transactions/filter", methods=["POST"])
def filter_transactions():
    data = request.json
    query = Transaction.query
    if data.get("user_id"):
        query = query.filter(Transaction.account_id==data["user_id"])
    if data.get("category_id"):
        query = query.filter(Transaction.category_id==data["category_id"])
    if data.get("start_date") and data.get("end_date"):
        start = datetime.datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        end = datetime.datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        query = query.filter(Transaction.date.between(start, end))
    if data.get("keyword"):
        query = query.filter(Transaction.description.contains(data["keyword"]))
    transactions = query.all()
    result = []
    for t in transactions:
        result.append({
            "id": t.id,
            "amount": t.amount,
            "date": str(t.date),
            "description": t.description,
            "account_id": t.account_id,
            "category": t.category.name if t.category else None
        })
    return jsonify(result)
