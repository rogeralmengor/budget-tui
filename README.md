# 💰 Personal Budget Tracker TUI

A powerful, terminal-based budget tracking application built with Python and Textual. Track your income and expenses with an intuitive text user interface (TUI) featuring visual charts, category management, and comprehensive reporting.

![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### Core Functionality
- **📊 Visual Dashboard**: Real-time overview of monthly income, expenses, and balance
- **📅 Month Navigation**: Browse through different months with ease
- **💵 Income Tracking**: Log all income sources with categories
- **💸 Expense Tracking**: Track expenses with detailed categorization
- **📈 Visual Bars**: Interactive bar charts showing financial summary
- **🔄 CRUD Operations**: Full create, read, update, and delete functionality

### Advanced Features
- **🎯 Category Management**: Predefined categories for both income and expenses
- **🔍 View All Transactions**: Browse complete transaction history with scrolling
- **📊 Pie Charts**: Generate visual category breakdowns (matplotlib integration)
- **💾 Data Export**: Export transactions to CSV format
- **⚡ Command Terminal**: Built-in command interface for advanced operations
- **🗄️ SQLite Database**: Reliable local data storage

### Supported Categories
**Expenses**: Food, Transport, Housing, Entertainment, Healthcare, Shopping, Other  
**Income**: Salary, Freelance, Investment, Gift, Bonus, Other

## 🚀 Installation

### Prerequisites
- Python 3.11 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/budget-tracker-tui.git
   cd budget-tracker-tui
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## 📦 Dependencies

```
textual>=0.40.0
sqlalchemy>=2.0.0
matplotlib>=3.5.0
seaborn>=0.12.0
```

## 🎮 Usage

### Launching the Application

```bash
python main.py
```

Or make it executable:
```bash
chmod +x main.py
./main.py
```

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `e` | Add new expense |
| `i` | Add new income |
| `E` | Edit existing expense |
| `I` | Edit existing income |
| `d` | Delete expense |
| `D` | Delete income |
| `v` | View all transactions |
| `c` | Open command terminal |
| `r` | Refresh dashboard |
| `←` | Previous month |
| `→` | Next month |
| `t` | Return to current month |
| `q` | Quit application |
| `ESC` | Go back / Cancel |

### Adding Transactions

1. Press `e` for expenses or `i` for income
2. Fill in the required fields:
   - Date (YYYY-MM-DD format)
   - Description
   - Amount
   - Category
3. Press Enter or click "Add" button
4. Transaction is automatically saved to database

### Editing Transactions

1. Press `E` for expenses or `I` for income
2. Enter the date to load transactions
3. Select the transaction using arrow keys
4. Enter new values (leave blank to keep current)
5. Save changes

### Command Terminal

Press `c` to access the command terminal with built-in commands:

- `help` - Show all available commands
- `stats` - Display database statistics
- `export` - Export data to CSV files
- `plot` - Generate category pie charts
- `clear` - Clear terminal output

You can also run custom shell commands and Python scripts directly!

## 📁 Project Structure

```
budget-tracker-tui/
├── main.py              # Application entry point
├── tui.py               # Main TUI interface and screens
├── db.py                # Database models and operations
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── budget.db           # SQLite database (created on first run)
```

## 🗄️ Database Schema

The application uses SQLite with two main tables:

**Expenses Table**
- id (Primary Key)
- date (Date)
- description (String)
- amount (Float)
- category (String)

**Income Table**
- id (Primary Key)
- date (Date)
- description (String)
- amount (Float)
- category (String)

## 🎨 Screenshots

### Main Dashboard
- Monthly expense/income summary
- Visual bar charts
- Scrollable transaction lists sorted by date

### Add Transaction Screen
- Simple form interface
- Date validation
- Category suggestions

### Command Terminal
- Execute custom commands
- Built-in utilities
- Real-time output display

## 🔧 Configuration

The application creates a `budget.db` SQLite database in the current directory on first run. To reset your data, simply delete this file.

### Customizing Categories

Edit the category lists in `tui.py`:

```python
EXPENSE_CATEGORIES = ["Food", "Transport", "Housing", "Entertainment", "Healthcare", "Shopping", "Other"]
INCOME_CATEGORIES = ["Salary", "Freelance", "Investment", "Gift", "Bonus", "Other"]
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Known Issues

- Pie chart generation requires matplotlib and seaborn
- Date format is fixed to YYYY-MM-DD (ISO format)
- Database is local only (no cloud sync)

## 🔮 Future Enhancements

- Pie chart generation within the TUI
- Pie charts for annual expenses
- Savings
- Investment

## 💡 Tips

- Use consistent category names for better reporting
- Review your transactions regularly using the "View All" screen
- Export data monthly for external backups
- Use the command terminal for bulk operations

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Built with ❤️ using [Textual](https://textual.textualize.io/)**

