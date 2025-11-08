from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, DataTable, Button, Input, Label, RichLog
from textual.binding import Binding
from textual.screen import Screen
from datetime import datetime
from db import Database
import subprocess
import sys

class AddExpenseScreen(Screen):
    """Screen for adding a new expense"""
    BINDINGS = [("escape", "app.pop_screen", "Back")]
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="add-form"):
            yield Label("Add Expense", id="form-title")
            yield Label("Date (YYYY-MM-DD):")
            yield Input(placeholder="2024-01-15", id="expense-date", value=datetime.now().strftime("%Y-%m-%d"))
            yield Label("Description:")
            yield Input(placeholder="Groceries", id="expense-desc")
            yield Label("Amount:")
            yield Input(placeholder="50.00", id="expense-amount")
            yield Button("Add Expense", variant="success", id="submit-expense")
            yield Label("", id="expense-message")
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit-expense":
            try:
                date_str = self.query_one("#expense-date", Input).value
                desc = self.query_one("#expense-desc", Input).value
                amount_str = self.query_one("#expense-amount", Input).value
                
                if not date_str or not desc or not amount_str:
                    self.query_one("#expense-message", Label).update("✗ All fields are required!")
                    return
                
                amount = float(amount_str)
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                self.app.db.add_expense(date, desc, amount)
                
                self.query_one("#expense-message", Label).update("✓ Expense added successfully!")
                self.query_one("#expense-date", Input).value = datetime.now().strftime("%Y-%m-%d")
                self.query_one("#expense-desc", Input).value = ""
                self.query_one("#expense-amount", Input).value = ""
                self.app.refresh_data()
                    
            except ValueError as e:
                self.query_one("#expense-message", Label).update(f"✗ Invalid input: {str(e)}")
            except Exception as e:
                self.query_one("#expense-message", Label).update(f"✗ Error: {str(e)}")


class AddIncomeScreen(Screen):
    """Screen for adding a new income"""
    BINDINGS = [("escape", "app.pop_screen", "Back")]
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="add-form"):
            yield Label("Add Income", id="form-title")
            yield Label("Date (YYYY-MM-DD):")
            yield Input(placeholder="2024-01-15", id="income-date", value=datetime.now().strftime("%Y-%m-%d"))
            yield Label("Description:")
            yield Input(placeholder="Salary", id="income-desc")
            yield Label("Amount:")
            yield Input(placeholder="3000.00", id="income-amount")
            yield Button("Add Income", variant="success", id="submit-income")
            yield Label("", id="income-message")
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit-income":
            try:
                date_str = self.query_one("#income-date", Input).value
                desc = self.query_one("#income-desc", Input).value
                amount_str = self.query_one("#income-amount", Input).value
                
                if not date_str or not desc or not amount_str:
                    self.query_one("#income-message", Label).update("✗ All fields are required!")
                    return
                
                amount = float(amount_str)
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                self.app.db.add_income(date, desc, amount)
                
                self.query_one("#income-message", Label).update("✓ Income added successfully!")
                self.query_one("#income-date", Input).value = datetime.now().strftime("%Y-%m-%d")
                self.query_one("#income-desc", Input).value = ""
                self.query_one("#income-amount", Input).value = ""
                self.app.refresh_data()
                    
            except ValueError as e:
                self.query_one("#income-message", Label).update(f"✗ Invalid input: {str(e)}")
            except Exception as e:
                self.query_one("#income-message", Label).update(f"✗ Error: {str(e)}")


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
            # Built-in commands
            if command == "help":
                output.write("[green]Built-in commands:[/]")
                output.write("  help   - Show this help")
                output.write("  stats  - Show database statistics")
                output.write("  export - Export data to CSV")
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
                # Simple CSV export
                try:
                    expenses = self.app.db.get_expenses()
                    incomes = self.app.db.get_incomes()
                    
                    with open("expenses_export.csv", "w") as f:
                        f.write("Date,Description,Amount\n")
                        for exp in expenses:
                            f.write(f"{exp.date},{exp.description},{exp.amount}\n")
                    
                    with open("incomes_export.csv", "w") as f:
                        f.write("Date,Description,Amount\n")
                        for inc in incomes:
                            f.write(f"{inc.date},{inc.description},{inc.amount}\n")
                    
                    output.write("[green]✓ Exported to expenses_export.csv and incomes_export.csv[/]")
                except Exception as e:
                    output.write(f"[red]✗ Export error: {str(e)}[/]")
            
            else:
                # Execute as shell command
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.stdout:
                    output.write(result.stdout)
                if result.stderr:
                    output.write(f"[red]{result.stderr}[/]")
                if result.returncode != 0:
                    output.write(f"[red]Exit code: {result.returncode}[/]")
                else:
                    output.write("[green]✓ Command completed successfully[/]")
        
        except subprocess.TimeoutExpired:
            output.write("[red]✗ Command timed out (30s limit)[/]")
        except Exception as e:
            output.write(f"[red]✗ Error: {str(e)}[/]")
        
        self.query_one("#command-input", Input).value = ""


class BudgetApp(App):
    """Main Budget Tracker Application"""
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    #dashboard {
        height: 100%;
        padding: 1;
    }
    
    .panel {
        border: solid $primary;
        height: auto;
        margin: 1;
        padding: 1;
    }
    
    #month-nav {
        height: 5;
        margin: 1;
        padding: 1;
        border: solid $accent;
        background: $boost;
    }
    
    #month-display {
        text-style: bold;
        text-align: center;
        color: $accent;
        margin: 0 2;
    }
    
    #summary-container {
        height: 12;
    }
    
    #recent-container {
        height: 1fr;
    }
    
    .summary-box {
        width: 1fr;
        border: solid $accent;
        padding: 1;
        margin: 1;
    }
    
    #add-form {
        width: 60;
        height: auto;
        margin: 2 4;
        padding: 2;
        border: solid $primary;
    }
    
    #form-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
        content-align: center middle;
    }
    
    Input {
        margin-bottom: 1;
    }
    
    Button {
        margin-top: 1;
        width: 100%;
    }
    
    DataTable {
        height: 100%;
    }
    
    #expense-message, #income-message {
        margin-top: 1;
        text-align: center;
    }
    
    .nav-button {
        margin: 0 1;
        min-width: 15;
    }
    
    #command-container {
        width: 80;
        height: auto;
        margin: 2;
        padding: 2;
        border: solid $primary;
    }
    
    #command-title {
        margin-bottom: 1;
        text-align: center;
    }
    
    #command-output {
        height: 20;
        border: solid $primary;
        margin-top: 1;
        padding: 1;
    }
    
    #output-label {
        margin-top: 1;
        text-style: bold;
    }
    """
    
    BINDINGS = [
        Binding("e", "add_expense", "Add Expense"),
        Binding("i", "add_income", "Add Income"),
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
            # Month navigation bar
            with Container(id="month-nav"):
                with Horizontal():
                    yield Button("◀ Prev", variant="primary", classes="nav-button", id="btn-prev")
                    yield Static("", id="month-display")
                    yield Button("Next ▶", variant="primary", classes="nav-button", id="btn-next")
                    yield Button("Today", variant="success", classes="nav-button", id="btn-today")
            
            # Summary section
            with Container(id="summary-container", classes="panel"):
                with Horizontal():
                    yield Static("Loading...", id="expense-summary", classes="summary-box")
                    yield Static("Loading...", id="income-summary", classes="summary-box")
                    yield Static("Loading...", id="balance-summary", classes="summary-box")
            
            # Recent transactions
            with Container(id="recent-container"):
                with Horizontal():
                    with Vertical(classes="panel"):
                        yield Label("Expenses This Month")
                        yield DataTable(id="expense-table")
                    with Vertical(classes="panel"):
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
    
    def action_open_command(self) -> None:
        """Open command terminal"""
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
        try:
            month_name = datetime(self.current_year, self.current_month, 1).strftime("%B %Y")
            self.query_one("#month-display", Static).update(f"[bold]{month_name}[/]")
            
            monthly_expenses = self.db.get_monthly_expenses(self.current_year, self.current_month)
            monthly_incomes = self.db.get_monthly_incomes(self.current_year, self.current_month)
            
            total_expenses = sum(e.amount for e in monthly_expenses)
            total_incomes = sum(i.amount for i in monthly_incomes)
            balance = total_incomes - total_expenses
            
            self.query_one("#expense-summary", Static).update(
                f"[bold red]Expenses[/]\n[yellow]${total_expenses:,.2f}[/]\n({len(monthly_expenses)} transactions)"
            )
            self.query_one("#income-summary", Static).update(
                f"[bold green]Income[/]\n[yellow]${total_incomes:,.2f}[/]\n({len(monthly_incomes)} transactions)"
            )
            
            balance_color = "green" if balance >= 0 else "red"
            balance_symbol = "+" if balance >= 0 else ""
            self.query_one("#balance-summary", Static).update(
                f"[bold]Balance[/]\n[{balance_color}]{balance_symbol}${balance:,.2f}[/]"
            )
            
            expense_table = self.query_one("#expense-table", DataTable)
            expense_table.clear(columns=True)
            expense_table.add_columns("ID", "Date", "Description", "Amount")
            
            sorted_expenses = sorted(monthly_expenses, key=lambda x: x.date, reverse=True)
            for exp in sorted_expenses:
                expense_table.add_row(
                    str(exp.id),
                    str(exp.date),
                    exp.description[:25] + "..." if len(exp.description) > 25 else exp.description,
                    f"${exp.amount:,.2f}"
                )
            
            income_table = self.query_one("#income-table", DataTable)
            income_table.clear(columns=True)
            income_table.add_columns("ID", "Date", "Description", "Amount")
            
            sorted_incomes = sorted(monthly_incomes, key=lambda x: x.date, reverse=True)
            for inc in sorted_incomes:
                income_table.add_row(
                    str(inc.id),
                    str(inc.date),
                    inc.description[:25] + "..." if len(inc.description) > 25 else inc.description,
                    f"${inc.amount:,.2f}"
                )
                
        except Exception as e:
            self.notify(f"Error refreshing data: {str(e)}", severity="error")


if __name__ == "__main__":
    app = BudgetApp()
    app.run()
