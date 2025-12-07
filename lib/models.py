from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Account(db.Model):
    __tablename__ = "accounts"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    transactions = db.relationship("Transaction", back_populates="account", cascade="all, delete-orphan")

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    transactions = db.relationship("Transaction", back_populates="category", cascade="all, delete-orphan")

class Transaction(db.Model):
    __tablename__ = "transactions"
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id"))
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    account = db.relationship("Account", back_populates="transactions")
    category = db.relationship("Category", back_populates="transactions")
