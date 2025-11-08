from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Expense(Base):
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    description = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    
    def __repr__(self):
        return f"<Expense(id={self.id}, date={self.date}, description={self.description}, amount={self.amount})>"

class Income(Base):
    __tablename__ = 'incomes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    description = Column(String(200), nullable=False)
    amount = Column(Float, nullable=False)
    
    def __repr__(self):
        return f"<Income(id={self.id}, date={self.date}, description={self.description}, amount={self.amount})>"

class Database:
    def __init__(self, db_url='sqlite:///budget.db'):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def add_expense(self, date, description, amount):
        expense = Expense(date=date, description=description, amount=amount)
        self.session.add(expense)
        self.session.commit()
        return expense
    
    def get_expenses(self, limit=None):
        query = self.session.query(Expense).order_by(Expense.date.desc(), Expense.id.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def get_expense_by_id(self, expense_id):
        return self.session.query(Expense).filter(Expense.id == expense_id).first()
    
    def get_monthly_expenses(self, year, month):
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date()
        else:
            end_date = datetime(year, month + 1, 1).date()
        
        return self.session.query(Expense).filter(
            Expense.date >= start_date,
            Expense.date < end_date
        ).all()
    
    def update_expense(self, expense_id, date=None, description=None, amount=None):
        expense = self.session.query(Expense).filter(Expense.id == expense_id).first()
        if expense:
            if date is not None:
                expense.date = date
            if description is not None:
                expense.description = description
            if amount is not None:
                expense.amount = amount
            self.session.commit()
            return expense
        return None
    
    def delete_expense(self, expense_id):
        expense = self.session.query(Expense).filter(Expense.id == expense_id).first()
        if expense:
            self.session.delete(expense)
            self.session.commit()
            return True
        return False
    
    def add_income(self, date, description, amount):
        income = Income(date=date, description=description, amount=amount)
        self.session.add(income)
        self.session.commit()
        return income
    
    def get_incomes(self, limit=None):
        query = self.session.query(Income).order_by(Income.date.desc(), Income.id.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def get_income_by_id(self, income_id):
        return self.session.query(Income).filter(Income.id == income_id).first()
    
    def get_monthly_incomes(self, year, month):
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date()
        else:
            end_date = datetime(year, month + 1, 1).date()
        
        return self.session.query(Income).filter(
            Income.date >= start_date,
            Income.date < end_date
        ).all()
    
    def update_income(self, income_id, date=None, description=None, amount=None):
        income = self.session.query(Income).filter(Income.id == income_id).first()
        if income:
            if date is not None:
                income.date = date
            if description is not None:
                income.description = description
            if amount is not None:
                income.amount = amount
            self.session.commit()
            return income
        return None
    
    def delete_income(self, income_id):
        income = self.session.query(Income).filter(Income.id == income_id).first()
        if income:
            self.session.delete(income)
            self.session.commit()
            return True
        return False
    
    def close(self):
        self.session.close()

if __name__ == "__main__":
    db = Database()
    print("Database initialized successfully!")
    
    db.add_expense(datetime(2024, 11, 1).date(), "Test Expense", 50.00)
    db.add_income(datetime(2024, 11, 1).date(), "Test Income", 1000.00)
    
    print("\nExpenses:")
    for exp in db.get_expenses(limit=5):
        print(f"  {exp.date} - {exp.description}: ${exp.amount}")
    
    print("\nIncomes:")
    for inc in db.get_incomes(limit=5):
        print(f"  {inc.date} - {inc.description}: ${inc.amount}")
    
    print("\nDatabase ready!")
