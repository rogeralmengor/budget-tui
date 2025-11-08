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

class Income(Base):
    __tablename__ = "incomes"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)


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
    def add_expense(self, date, description, amount):
        exp = Expense(date=date, description=description, amount=amount)
        self.session.add(exp)
        self.session.commit()

    def add_income(self, date, description, amount):
        inc = Income(date=date, description=description, amount=amount)
        self.session.add(inc)
        self.session.commit()

    # ─────────────────────────────
    # UPDATE METHODS
    # ─────────────────────────────
    def update_expense(self, expense_id, description=None, amount=None):
        exp = self.session.query(Expense).filter_by(id=expense_id).first()
        if not exp:
            return False
        if description:
            exp.description = description
        if amount is not None:
            exp.amount = amount
        self.session.commit()
        return True

    def update_income(self, income_id, description=None, amount=None):
        inc = self.session.query(Income).filter_by(id=income_id).first()
        if not inc:
            return False
        if description:
            inc.description = description
        if amount is not None:
            inc.amount = amount
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
