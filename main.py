#!/usr/bin/env python3
"""
Personal Budget Tracker TUI
Entry point for the application
"""

from tui import BudgetApp

def main():
    """Launch the Budget Tracker TUI"""
    app = BudgetApp()
    app.run()

if __name__ == "__main__":
    main()
