from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, DataTable, Button, Input, Label, RichLog
from textual.binding import Binding
from textual.screen import Screen
from datetime import datetime
from db import Database
import subprocess
import matplotlib.pyplot as plt
import seaborn as sns
import tempfile
import os

# Add after imports
EXPENSE_CATEGORIES = ["Food", "Transport", "Housing", "Entertainment", "Healthcare", "Shopping", "Other"]
INCOME_CATEGORIES = ["Salary", "Freelance", "Investment", "Gift", "Bonus", "Other"]

# ─────────────────────────────────────────────
# Add Expense Screen
# ─────────────────────────────────────────────
class AddExpenseScreen(Screen):
    """Screen for adding a new expense"""
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="add-form"):
            yield Label("Add Expense", id="form-title")
            yield Label("Date (YYYY-MM-DD):")
            yield Input(placeholder="2025-01-15", id="expense-date", value=datetime.now().strftime("%Y-%m-%d"))
            yield Label("Description:")
            yield Input(placeholder="Groceries", id="expense-desc")
            yield Label("Amount:")
            yield Input(placeholder="50.00", id="expense-amount")
            yield Label("Category:")
            yield Input(placeholder="Food", id="expense-category")
            yield Static("[dim]Common: Food, Transport, Housing, Entertainment, Healthcare, Shopping, Other[/]", id="category-hint")
            yield Button("Add Expense", variant="success", id="submit-expense")
            yield Label("", id="expense-message")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit-expense":
            try:
                date_str = self.query_one("#expense-date", Input).value
                desc = self.query_one("#expense-desc", Input).value
                amount_str = self.query_one("#expense-amount", Input).value
                category = self.query_one("#expense-category", Input).value or "Other"

                if not date_str or not desc or not amount_str:
                    self.query_one("#expense-message", Label).update("✗ All fields are required!")
                    return

                amount = float(amount_str)
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                self.app.db.add_expense(date, desc, amount, category)

                self.query_one("#expense-message", Label).update("✓ Expense added successfully!")
                self.query_one("#expense-date", Input).value = datetime.now().strftime("%Y-%m-%d")
                self.query_one("#expense-desc", Input).value = ""
                self.query_one("#expense-amount", Input).value = ""
                self.query_one("#expense-category", Input).value = ""
                self.app.refresh_data()

            except ValueError as e:
                self.query_one("#expense-message", Label).update(f"✗ Invalid input: {str(e)}")
            except Exception as e:
                self.query_one("#expense-message", Label).update(f"✗ Error: {str(e)}")


# ─────────────────────────────────────────────
# Add Income Screen
# ─────────────────────────────────────────────
class AddIncomeScreen(Screen):
    """Screen for adding a new income"""
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="add-form"):
            yield Label("Add Income", id="form-title")
            yield Label("Date (YYYY-MM-DD):")
            yield Input(placeholder="2025-01-15", id="income-date", value=datetime.now().strftime("%Y-%m-%d"))
            yield Label("Description:")
            yield Input(placeholder="Salary", id="income-desc")
            yield Label("Amount:")
            yield Input(placeholder="3000.00", id="income-amount")
            yield Label("Category:")
            yield Input(placeholder="Salary", id="income-category")
            yield Static("[dim]Common: Salary, Freelance, Investment, Gift, Bonus, Other[/]", id="category-hint")
            yield Button("Add Income", variant="success", id="submit-income")
            yield Label("", id="income-message")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit-income":
            try:
                date_str = self.query_one("#income-date", Input).value
                desc = self.query_one("#income-desc", Input).value
                amount_str = self.query_one("#income-amount", Input).value
                category = self.query_one("#income-category", Input).value or "Salary"

                if not date_str or not desc or not amount_str:
                    self.query_one("#income-message", Label).update("✗ All fields are required!")
                    return

                amount = float(amount_str)
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                self.app.db.add_income(date, desc, amount, category)

                self.query_one("#income-message", Label).update("✓ Income added successfully!")
                self.query_one("#income-date", Input).value = datetime.now().strftime("%Y-%m-%d")
                self.query_one("#income-desc", Input).value = ""
                self.query_one("#income-amount", Input).value = ""
                self.query_one("#income-category", Input).value = ""
                self.app.refresh_data()

            except ValueError as e:
                self.query_one("#income-message", Label).update(f"✗ Invalid input: {str(e)}")
            except Exception as e:
                self.query_one("#income-message", Label).update(f"✗ Error: {str(e)}")


# ─────────────────────────────────────────────
# Edit Expense / Income Screens
# ─────────────────────────────────────────────
class EditExpenseScreen(Screen):
    """Edit an existing expense by date"""
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="add-form"):
            yield Label("Edit Expense", id="form-title")
            yield Label("Enter date to list expenses (YYYY-MM-DD):")
            yield Input(id="edit-date", placeholder="2025-11-01")
            yield Button("Load Expenses", id="load-expenses", variant="primary")
            yield Label("", id="message")
            yield DataTable(id="expense-list")
            yield Label("Edit selected item:")
            yield Input(placeholder="New Description", id="new-desc")
            yield Input(placeholder="New Amount", id="new-amount")
            yield Input(placeholder="New Category", id="new-category")
            yield Button("Save Changes", variant="success", id="save-changes")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        table = self.query_one("#expense-list", DataTable)
        msg = self.query_one("#message", Label)

        if event.button.id == "load-expenses":
            try:
                date_str = self.query_one("#edit-date", Input).value
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                expenses = self.app.db.session.query(self.app.db.Expense).filter_by(date=date).all()

                table.clear(columns=True)
                table.add_columns("ID", "Description", "Amount", "Category")
                for e in expenses:
                    table.add_row(str(e.id), e.description, f"${e.amount:.2f}", e.category)

                if not expenses:
                    msg.update("No expenses found for that date.")
                else:
                    msg.update(f"Loaded {len(expenses)} expense(s).")

            except Exception as e:
                msg.update(f"✗ {str(e)}")

        elif event.button.id == "save-changes":
            if not table.cursor_row:
                msg.update("✗ No expense selected.")
                return

            try:
                row = table.cursor_row
                expense_id = int(table.get_row_at(row)[0])
                new_desc = self.query_one("#new-desc", Input).value
                new_amount_str = self.query_one("#new-amount", Input).value
                new_category = self.query_one("#new-category", Input).value

                amount = float(new_amount_str) if new_amount_str else None
                updated = self.app.db.update_expense(
                    expense_id, 
                    description=new_desc or None, 
                    amount=amount,
                    category=new_category or None
                )
                if updated:
                    msg.update("✓ Expense updated successfully.")
                    self.app.refresh_data()
                else:
                    msg.update("✗ Expense not found.")
            except Exception as e:
                msg.update(f"✗ Error: {str(e)}")


class EditIncomeScreen(Screen):
    """Edit an existing income by date"""
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="add-form"):
            yield Label("Edit Income", id="form-title")
            yield Label("Enter date to list incomes (YYYY-MM-DD):")
            yield Input(id="edit-date", placeholder="2025-11-01")
            yield Button("Load Incomes", id="load-incomes", variant="primary")
            yield Label("", id="message")
            yield DataTable(id="income-list")
            yield Label("Edit selected item:")
            yield Input(placeholder="New Description", id="new-desc")
            yield Input(placeholder="New Amount", id="new-amount")
            yield Input(placeholder="New Category", id="new-category")
            yield Button("Save Changes", variant="success", id="save-changes")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        table = self.query_one("#income-list", DataTable)
        msg = self.query_one("#message", Label)

        if event.button.id == "load-incomes":
            try:
                date_str = self.query_one("#edit-date", Input).value
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                incomes = self.app.db.session.query(self.app.db.Income).filter_by(date=date).all()

                table.clear(columns=True)
                table.add_columns("ID", "Description", "Amount", "Category")
                for i in incomes:
                    table.add_row(str(i.id), i.description, f"${i.amount:.2f}", i.category)

                if not incomes:
                    msg.update("No incomes found for that date.")
                else:
                    msg.update(f"Loaded {len(incomes)} income(s).")

            except Exception as e:
                msg.update(f"✗ {str(e)}")

        elif event.button.id == "save-changes":
            if not table.cursor_row:
                msg.update("✗ No income selected.")
                return

            try:
                row = table.cursor_row
                income_id = int(table.get_row_at(row)[0])
                new_desc = self.query_one("#new-desc", Input).value
                new_amount_str = self.query_one("#new-amount", Input).value
                new_category = self.query_one("#new-category", Input).value

                amount = float(new_amount_str) if new_amount_str else None
                updated = self.app.db.update_income(
                    income_id, 
                    description=new_desc or None, 
                    amount=amount,
                    category=new_category or None
                )
                if updated:
                    msg.update("✓ Income updated successfully.")
                    self.app.refresh_data()
                else:
                    msg.update("✗ Income not found.")
            except Exception as e:
                msg.update(f"✗ Error: {str(e)}")


# ─────────────────────────────────────────────
# Command Screen
# ─────────────────────────────────────────────
class CommandScreen(Screen):
    """Screen for running commands and scripts"""
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="command-container"):
            yield Label("[bold cyan]Command Terminal[/]", id="command-title")
            yield Label("Enter command or script path to execute:")
            yield Input(placeholder="python my_script.py or ls", id="command-input")
            yield Button("Execute", variant="success", id="btn-execute")
            yield Label("\nOutput:", id="output-label")
            yield RichLog(id="command-output", highlight=True, markup=True)
        yield Footer()

    def on_mount(self) -> None:
        output = self.query_one("#command-output", RichLog)
        output.write("[dim]Available built-in commands:[/]")
        output.write("  • help - Show available commands")
        output.write("  • stats - Show database statistics")
        output.write("  • export - Export data to CSV")
        output.write("  • clear - Clear this output")
        output.write("\n[dim]Or run any Python script or shell command[/]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-execute":
            self.execute_command()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "command-input":
            self.execute_command()

    def execute_command(self) -> None:
        command = self.query_one("#command-input", Input).value.strip()
        output = self.query_one("#command-output", RichLog)

        if not command:
            return

        output.write(f"\n[bold cyan]$ {command}[/]")

        try:
            if command == "help":
                output.write("[green]Built-in commands:[/]")
                output.write("  help   - Show this help")
                output.write("  stats  - Show database statistics")
                output.write("  export - Export data to CSV")
                output.write("  plot   - Generate category pie charts")
                output.write("  clear  - Clear output")

            elif command == "clear":
                output.clear()
                output.write("[dim]Output cleared[/]")

            elif command == "stats":
                total_expenses = len(self.app.db.get_expenses())
                total_incomes = len(self.app.db.get_incomes())
                output.write(f"[green]Total Expenses: {total_expenses}[/]")
                output.write(f"[green]Total Incomes: {total_incomes}[/]")

                now = datetime.now()
                monthly_exp = self.app.db.get_monthly_expenses(now.year, now.month)
                monthly_inc = self.app.db.get_monthly_incomes(now.year, now.month)
                output.write(f"[yellow]This month - Expenses: {len(monthly_exp)}, Incomes: {len(monthly_inc)}[/]")

            elif command == "export":
                expenses = self.app.db.get_expenses()
                incomes = self.app.db.get_incomes()
                with open("expenses_export.csv", "w") as f:
                    f.write("Date,Description,Amount,Category\n")  # Added Category
                    for exp in expenses:
                        f.write(f"{exp.date},{exp.description},{exp.amount},{exp.category}\n")
                with open("incomes_export.csv", "w") as f:
                    f.write("Date,Description,Amount,Category\n")  # Added Category
                    for inc in incomes:
                        f.write(f"{inc.date},{inc.description},{inc.amount},{inc.category}\n")
                output.write("[green]✓ Exported to expenses_export.csv and incomes_export.csv[/]")

            elif command == "plot":
                self.generate_pie_charts(output)

            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
                if result.stdout:
                    output.write(result.stdout)
                if result.stderr:
                    output.write(f"[red]{result.stderr}[/]")
                output.write("[green]✓ Command completed successfully[/]" if result.returncode == 0 else f"[red]Exit code: {result.returncode}[/]")

        except subprocess.TimeoutExpired:
            output.write("[red]✗ Command timed out (30s limit)[/]")
        except Exception as e:
            output.write(f"[red]✗ Error: {str(e)}[/]")

        self.query_one("#command-input", Input).value = ""

def generate_pie_charts(self, output):
    """Generate pie charts for expenses and incomes by category"""
    try:
        # Get current month data
        now = datetime.now()
        expense_categories = self.app.db.get_expenses_by_category(now.year, now.month)
        income_categories = self.app.db.get_incomes_by_category(now.year, now.month)

        if not expense_categories and not income_categories:
            output.write("[yellow]No data available for current month[/]")
            return

        # Create subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))

        # Colors for pie charts
        colors = sns.color_palette("pastel", max(len(expense_categories), len(income_categories)))

        # Expense pie chart (percentage)
        if expense_categories:
            exp_labels = list(expense_categories.keys())
            exp_values = list(expense_categories.values())
            exp_total = sum(exp_values)
            
            ax1.pie(exp_values, labels=exp_labels, autopct='%1.1f%%', colors=colors[:len(exp_labels)])
            ax1.set_title(f'Expenses by Category\n(Total: ${exp_total:.2f})')

        else:
            ax1.text(0.5, 0.5, 'No Expense Data', ha='center', va='center', transform=ax1.transAxes)
            ax1.set_title('Expenses by Category')

        # Income pie chart (percentage)
        if income_categories:
            inc_labels = list(income_categories.keys())
            inc_values = list(income_categories.values())
            inc_total = sum(inc_values)
            
            ax2.pie(inc_values, labels=inc_labels, autopct='%1.1f%%', colors=colors[:len(inc_labels)])
            ax2.set_title(f'Incomes by Category\n(Total: ${inc_total:.2f})')

        else:
            ax2.text(0.5, 0.5, 'No Income Data', ha='center', va='center', transform=ax2.transAxes)
            ax2.set_title('Incomes by Category')

        plt.tight_layout()
        
        # Save to temporary file and open
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            plt.savefig(tmp.name, dpi=150, bbox_inches='tight')
            tmp_path = tmp.name

        # Try to open the image
        try:
            if os.name == 'nt':  # Windows
                os.startfile(tmp_path)
            elif os.name == 'posix':  # macOS, Linux
                subprocess.run(['open', tmp_path] if sys.platform == 'darwin' else ['xdg-open', tmp_path])
            output.write("[green]✓ Pie charts generated and opened[/]")
        except:
            output.write(f"[green]✓ Pie charts saved to: {tmp_path}[/]")
            output.write("[yellow]Could not auto-open image viewer[/]")

        plt.close()

    except ImportError:
        output.write("[red]✗ matplotlib or seaborn not installed[/]")
        output.write("[yellow]Run: pip install matplotlib seaborn[/]")
    except Exception as e:
        output.write(f"[red]✗ Error generating charts: {str(e)}[/]")


# ─────────────────────────────────────────────
# Main BudgetApp
# ─────────────────────────────────────────────
class BudgetApp(App):
    """Main Budget Tracker Application"""

    BINDINGS = [
        Binding("e", "add_expense", "Add Expense"),
        Binding("i", "add_income", "Add Income"),
        Binding("E", "edit_expense", "Edit Expense"),
        Binding("I", "edit_income", "Edit Income"),
        Binding("c", "open_command", "Command"),
        Binding("r", "refresh", "Refresh"),
        Binding("left", "prev_month", "Prev Month"),
        Binding("right", "next_month", "Next Month"),
        Binding("t", "current_month", "Today"),
        Binding("q", "quit", "Quit"),
    ]

    TITLE = "Budget Tracker TUI"

    def __init__(self):
        super().__init__()
        self.db = Database()
        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="dashboard"):
            with Container(id="month-nav"):
                with Horizontal():
                    yield Button("◀ Prev", variant="primary", id="btn-prev")
                    yield Static("", id="month-display")
                    yield Button("Next ▶", variant="primary", id="btn-next")
                    yield Button("Today", variant="success", id="btn-today")

            with Container(id="summary-container"):
                with Horizontal():
                    yield Static("Loading...", id="expense-summary")
                    yield Static("Loading...", id="income-summary")
                    yield Static("Loading...", id="balance-summary")

            with Container(id="recent-container"):
                with Horizontal():
                    with Vertical():
                        yield Label("Expenses This Month")
                        yield DataTable(id="expense-table")
                    with Vertical():
                        yield Label("Incomes This Month")
                        yield DataTable(id="income-table")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_data()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-prev":
            self.action_prev_month()
        elif event.button.id == "btn-next":
            self.action_next_month()
        elif event.button.id == "btn-today":
            self.action_current_month()

    def action_add_expense(self) -> None:
        self.push_screen(AddExpenseScreen())

    def action_add_income(self) -> None:
        self.push_screen(AddIncomeScreen())

    def action_edit_expense(self) -> None:
        self.push_screen(EditExpenseScreen())

    def action_edit_income(self) -> None:
        self.push_screen(EditIncomeScreen())

    def action_open_command(self) -> None:
        self.push_screen(CommandScreen())

    def action_refresh(self) -> None:
        self.refresh_data()
        self.notify("Data refreshed!")

    def action_prev_month(self) -> None:
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.refresh_data()

    def action_next_month(self) -> None:
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.refresh_data()

    def action_current_month(self) -> None:
        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month
        self.refresh_data()
        self.notify("Showing current month")

    def refresh_data(self) -> None:
        """Refresh dashboard data and update tables"""
        try:
            month_name = datetime(self.current_year, self.current_month, 1).strftime("%B %Y")
            self.query_one("#month-display", Static).update(f"[bold]{month_name}[/]")

            monthly_expenses = self.db.get_monthly_expenses(self.current_year, self.current_month)
            monthly_incomes = self.db.get_monthly_incomes(self.current_year, self.current_month)

            # ... rest of the method remains the same until table setup ...

            exp_table = self.query_one("#expense-table", DataTable)
            inc_table = self.query_one("#income-table", DataTable)

            exp_table.clear(columns=True)
            inc_table.clear(columns=True)

            exp_table.add_columns("Date", "Description", "Amount", "Category")  # Added Category
            inc_table.add_columns("Date", "Description", "Amount", "Category")  # Added Category

            for e in monthly_expenses:
                exp_table.add_row(str(e.date), e.description, f"${e.amount:.2f}", e.category)
            for i in monthly_incomes:
                inc_table.add_row(str(i.date), i.description, f"${i.amount:.2f}", i.category)

        except Exception as e:
            self.notify(f"✗ Error refreshing data: {e}", severity="error")


# ─────────────────────────────────────────────
# Run App
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = BudgetApp()
    app.run()
