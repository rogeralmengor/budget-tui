from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False, default="Other")  # New category column

class Income(Base):
    __tablename__ = "incomes"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False, default="Salary")  # New category column


class Database:
    def __init__(self, db_path="budget.db"):
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # expose models so tui.py can access them (self.app.db.Expense)
        self.Expense = Expense
        self.Income = Income

    # ─────────────────────────────
    # ADD METHODS
    # ─────────────────────────────
    def add_expense(self, date, description, amount, category="Other"):
        exp = Expense(date=date, description=description, amount=amount, category=category)
        self.session.add(exp)
        self.session.commit()

    def add_income(self, date, description, amount, category="Salary"):
        inc = Income(date=date, description=description, amount=amount, category=category)
        self.session.add(inc)
        self.session.commit()

    # ─────────────────────────────
    # UPDATE METHODS
    # ─────────────────────────────
    def update_expense(self, expense_id, description=None, amount=None, category=None):
        exp = self.session.query(Expense).filter_by(id=expense_id).first()
        if not exp:
            return False
        if description:
            exp.description = description
        if amount is not None:
            exp.amount = amount
        if category:
            exp.category = category
        self.session.commit()
        return True

    def update_income(self, income_id, description=None, amount=None, category=None):
        inc = self.session.query(Income).filter_by(id=income_id).first()
        if not inc:
            return False
        if description:
            inc.description = description
        if amount is not None:
            inc.amount = amount
        if category:
            inc.category = category
        self.session.commit()
        return True

    # ─────────────────────────────
    # FETCH METHODS
    # ─────────────────────────────
    def get_expenses(self, limit=None):
        q = self.session.query(Expense).order_by(Expense.date.desc())
        return q.limit(limit).all() if limit else q.all()

    def get_incomes(self, limit=None):
        q = self.session.query(Income).order_by(Income.date.desc())
        return q.limit(limit).all() if limit else q.all()

    def get_monthly_expenses(self, year, month):
        start = datetime(year, month, 1).date()
        if month == 12:
            end = datetime(year + 1, 1, 1).date()
        else:
            end = datetime(year, month + 1, 1).date()
        return self.session.query(Expense).filter(Expense.date >= start, Expense.date < end).all()

    def get_monthly_incomes(self, year, month):
        start = datetime(year, month, 1).date()
        if month == 12:
            end = datetime(year + 1, 1, 1).date()
        else:
            end = datetime(year, month + 1, 1).date()
        return self.session.query(Income).filter(Income.date >= start, Income.date < end).all()

    # ─────────────────────────────
    # CATEGORY METHODS
    # ─────────────────────────────
    def get_expense_categories(self):
        """Get all unique expense categories"""
        return [cat[0] for cat in self.session.query(Expense.category).distinct().all()]

    def get_income_categories(self):
        """Get all unique income categories"""
        return [cat[0] for cat in self.session.query(Income.category).distinct().all()]

    def get_expenses_by_category(self, year=None, month=None):
        """Get expenses grouped by category"""
        query = self.session.query(Expense)
        if year and month:
            start = datetime(year, month, 1).date()
            if month == 12:
                end = datetime(year + 1, 1, 1).date()
            else:
                end = datetime(year, month + 1, 1).date()
            query = query.filter(Expense.date >= start, Expense.date < end)
        
        expenses = query.all()
        categories = {}
        for exp in expenses:
            categories[exp.category] = categories.get(exp.category, 0) + exp.amount
        return categories

    def get_incomes_by_category(self, year=None, month=None):
        """Get incomes grouped by category"""
        query = self.session.query(Income)
        if year and month:
            start = datetime(year, month, 1).date()
            if month == 12:
                end = datetime(year + 1, 1, 1).date()
            else:
                end = datetime(year, month + 1, 1).date()
            query = query.filter(Income.date >= start, Income.date < end)
        
        incomes = query.all()
        categories = {}
        for inc in incomes:
            categories[inc.category] = categories.get(inc.category, 0) + inc.amount
        return categories