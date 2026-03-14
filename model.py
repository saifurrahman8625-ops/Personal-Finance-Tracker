import sys
import mysql.connector
from datetime import datetime

from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QTableWidgetItem,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
    QWidget, QTabWidget, QLineEdit,  QComboBox, QFormLayout, QGroupBox, QTextEdit, QTableWidget,
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Personal Finance Tracker")
        self.setMinimumSize(800, 700)

        self.mydb = None
        self.create_connection()
        self.create_table()

        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #1e1e1e;")

        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        self.create_header(main_layout)
        self.create_content_area(main_layout)

    def create_header(self,parent_layout):

        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 10, 10, 10)
        title_layout = QHBoxLayout()

        self.balance_label = QLabel("Balance: 0.00")
        self.balance_label.setStyleSheet("""
                    font-size: 24px;
                    font-weight: bold;
                    color: white;
                    margin-left: 10px;
                """)

        title_layout.addWidget(self.balance_label)
        title_layout.addStretch()
        header_layout.addLayout(title_layout)
        parent_layout.addWidget(header_widget)

        self.update_balance()

    def update_balance(self):
        """Calculate and update the current balance"""
        try:
            cursor = self.mydb.cursor()
            cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM addmoney_table")
            total_income = cursor.fetchone()[0]

            cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM expense_table")
            total_expense = cursor.fetchone()[0]

            balance = total_income - total_expense
            self.balance_label.setText(f"Balance: {balance:.2f}")

        except Exception as e:
            print(f"Error updating balance: {e}")

    def create_content_area(self,parent_layout):
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        tab_bar = self.tab_widget.tabBar()
        tab_bar.setExpanding(True)

        self.tab_widget.setStyleSheet("""
            QTabBar::tab {
                min-height: 20px;
                font-size: 15px;
                background: lightgray;
                border: 8px solid #ddd;
                color: black;
                padding: 5px;
            }
            
            QTabBar::tab:selected {
            background: #07F078;   
            color: white;
    }

        """)
        self.setStyleSheet("""
             QDialog{
                background-color:white;
            }
                QLineEdit{ 
                    border: 1px solid gray;
                    border-radius: 18px;
                    padding-left: 15px;
                    height: 35px;
                }
                 QTextEdit{
                    border: 1px solid gray;
                    border-radius: 18px;
                    padding-left: 15px;
                    height: 35px;
                }
                QComboBox{
            border: 1px solid gray;
            border-radius: 18px;
            background-color: black;
            color: black;
            padding: 15px;
            }
                 """)

        self.tab_widget.addTab(self.AddMoney(), "💰 Add Money")
        self.tab_widget.addTab(self.Expenses(), "💸 Expense")
        self.tab_widget.addTab(self.Transaction(), "📝 All Transaction")
        parent_layout.addWidget(self.tab_widget)

    def AddMoney(self):

            tab = QWidget()
            tab.setStyleSheet("background-color: white;")
            layout = QVBoxLayout(tab)

            form_group = QGroupBox("AddMoney")
            form_layout = QFormLayout(form_group)

            font = QFont("Arial", 15, QFont.Bold)
            self.amount_add = QLineEdit()
            self.amount_add.setPlaceholderText("Enter Amount")
            label1 = QLabel("Amount:")
            label1.setFont(font)
            form_layout.addRow(label1, self.amount_add)

            form_layout.setSpacing(80)

            label2 = QLabel("Category:")
            label2.setFont(font)
            self.category_add = QComboBox()
            self.category_add.addItems(["Salary","Parent money","Gift", "Others"])
            form_layout.addRow(label2, self.category_add)

            label3 = QLabel("Note:")
            label3.setFont(font)
            self.note_add = QTextEdit()
            self.note_add.setPlaceholderText("Provide short note of the money...")
            self.note_add.setMaximumHeight(40)
            form_layout.addRow(label3, self.note_add)

            layout.addWidget(form_group)
            layout.addStretch()

            submit_btn = QPushButton("Cash In")
            submit_btn.setMinimumHeight(40)

            submit_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #4CAF50;
                            color: white;
                            font-size: 16px;
                             border-radius: 20px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #2196F3;
                        }
                    """)

            submit_btn.enterEvent = lambda event: submit_btn.setText("Cash In 😊")
            submit_btn.leaveEvent = lambda event: submit_btn.setText("Cash In")
            submit_btn.clicked.connect(self.add_money_to_db)

            layout.addWidget(submit_btn)
            return tab

    def add_money_to_db(self):
        
        try:
              amount = self.amount_add.text()
              category = self.category_add.currentText()
              note = self.note_add.toPlainText()
              current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

              cursor = self.mydb.cursor()
              query = "Insert INTO addmoney_table (amount, category, note, date) VALUES (%s, %s, %s, %s)"
              
              values = (amount,category,note,current_time)

              cursor.execute(query, values)
              self.mydb.commit()

              self.amount_add.clear()
              self.note_add.clear()

              self.update_balance()

              self.load_addmoney_records()
              self.load_expense_records()

              QMessageBox.information(self, "Success", "Money added successfully!")

        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter a valid amount")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Database error: {str(e)}")

    def Expenses(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(tab)

        form_group = QGroupBox("Expenses")
        form_layout = QFormLayout(form_group)

        font = QFont("Arial", 15, QFont.Bold)
        self.amount_expense = QLineEdit()
        self.amount_expense.setPlaceholderText("Enter Amount")
        label1 = QLabel("Amount:")
        label1.setFont(font)
        form_layout.addRow(label1, self.amount_expense)

        form_layout.setSpacing(80)

        label2 = QLabel("Category:")
        label2.setFont(font)
        self.category_expense = QComboBox()
        self.category_expense.addItems(["Food", "Entertainment","Clothing","Internet bill/Phone recharge","University fee","Transport","Gadgets","Phone", "Others"])
        form_layout.addRow(label2, self.category_expense)

        label3 = QLabel("Note:")
        label3.setFont(font)
        self.note_expense = QTextEdit()
        self.note_expense .setPlaceholderText("Provide description of the money...")
        self.note_expense .setMaximumHeight(40)
        form_layout.addRow(label3, self.note_expense )

        layout.addWidget(form_group)
        layout.addStretch()

        submit_btn = QPushButton("Expense")
        submit_btn.setMinimumHeight(40)

        submit_btn.setStyleSheet("""
                                QPushButton {
                                    background-color: #4CAF50;
                                    color: white;
                                    font-size: 16px;
                                     border-radius: 20px;
                                    font-weight: bold;
                                }
                                QPushButton:hover {
                                    background-color: #EC1313;
                                }
                            """)

        submit_btn.enterEvent = lambda event: submit_btn.setText("Expense 😔")
        submit_btn.leaveEvent = lambda event: submit_btn.setText("Expense")
        submit_btn.clicked.connect(self.add_expense_to_db)

        layout.addWidget(submit_btn)

        return tab

    def get_current_balance(self):
        try:
            cursor = self.mydb.cursor()
            cursor.execute("""
                           SELECT COALESCE((SELECT SUM(amount) FROM addmoney_table), 0) -
                                  COALESCE((SELECT SUM(amount) FROM expense_table), 0) as balance
                           """)
            return cursor.fetchone()[0]
        except Exception as e:
            print(f"Error getting balance: {e}")
            return 0

    def add_expense_to_db(self):
        try:
            amount = float(self.amount_expense.text())
            current_balance = self.get_current_balance()

            if current_balance - amount < 0:
                QMessageBox.warning(
                    self,
                    "Insufficient Balance",
                    f"Cannot add expense of ${amount:.2f}!\n"
                    f"Current balance: ${current_balance:.2f}\n"
                    f"Balance would become: ${current_balance - amount:.2f}"
                )
                return

            category = self.category_expense.currentText()
            note = self.note_expense.toPlainText()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor = self.mydb.cursor()
            query = "INSERT INTO expense_table (amount, category, note, date) VALUES (%s, %s, %s, %s)"
            values = (amount, category, note, current_time)

            cursor.execute(query, values)
            self.mydb.commit()

            self.amount_expense.clear()
            self.note_expense.clear()

            self.update_balance()
            self.load_addmoney_records()
            self.load_expense_records()

            QMessageBox.information(self, "Success", "Expense added successfully!")

        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter a valid amount")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Database error: {str(e)}")

    def Transaction(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: white; border-radius: 8px;")
        layout = QVBoxLayout(tab)

        inner_tab_widget = QTabWidget()
        inner_tab_widget.setDocumentMode(True)
        inner_tab_widget.tabBar().setExpanding(True)

        inner_tab_widget.setStyleSheet("""
           QTabBar::tab {
               min-height: 20px;
               font-size: 14px;
               background: lightgray;
               border: 8px solid #ddd;
               color: black;
               padding: 5px;
           }
    
           QTabBar::tab:selected {
               background: #2196F3;
               color: white;
           }
           """)

        inner_tab_widget.addTab(self.Money(), "💵 Add Money Record")
        inner_tab_widget.addTab(self.Expense(), "🏦 Expense Record")

        layout.addWidget(inner_tab_widget)
        return tab

    def Money(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(tab)

        self.money_table = QTableWidget()
        self.money_table.setColumnCount(5)
        self.money_table.setHorizontalHeaderLabels(
            ["ID", "Amount", "Category", "Note", "Date and time"])
        self.money_table.horizontalHeader().setStretchLastSection(True)
        self.money_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.money_table.setAlternatingRowColors(True)
        self.money_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.money_table.verticalHeader().setVisible(False)

        layout.addWidget(self.money_table)
        self.load_addmoney_records()

        return tab

    def Expense(self):
        tab = QWidget()
        tab.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(tab)

        self.expense_table = QTableWidget()
        self.expense_table.setColumnCount(5)
        self.expense_table.setHorizontalHeaderLabels(
            ["ID", "Amount", "Category", "Note", "Date and time"])
        self.expense_table.horizontalHeader().setStretchLastSection(True)
        self.money_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.expense_table.setAlternatingRowColors(True)
        self.expense_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.expense_table.verticalHeader().setVisible(False)

        layout.addWidget(self.expense_table)
        self.load_expense_records()

        return tab

    def load_addmoney_records(self):

        try:
            cursor = self.mydb.cursor()
            cursor.execute("SELECT * FROM addmoney_table ORDER BY income_id DESC")

            records = cursor.fetchall()

            self.money_table.setRowCount(len(records))

            for row, record in enumerate(records):
                 for col, value in enumerate(record):
                      self.money_table.setItem(row, col, QTableWidgetItem(str(value)))


        except Exception as e:
            print(f"Error loading add money records: {e}")

    def load_expense_records(self):
        try:
            cursor = self.mydb.cursor()
            cursor.execute("SELECT * FROM expense_table ORDER BY expense_id DESC")
            records = cursor.fetchall()

            self.expense_table.setRowCount(len(records))
            
            for row, record in enumerate(records):
                for col, value in enumerate(record):
                    self.expense_table.setItem(row, col, QTableWidgetItem(str(value)))

        except Exception as e:
            print(f"Error loading expense records: {e}")

    def create_connection(self):
        host_name = "localhost"
        user_name = "root"
        mypassword = ""
        database_name = ("personal")

        self.mydb=mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=mypassword,
        )

        cursor = self.mydb.cursor()
        cursor.execute(f'Create database if not exists {database_name};')

        self.mydb.close()

        self.mydb = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=mypassword,
            database=database_name
        )

        return self.mydb

    def create_table(self):
         cursor = self.create_connection().cursor()

         create_addmoney_table_query = """
             CREATE TABLE IF NOT EXISTS addmoney_table(
                income_id INT AUTO_INCREMENT PRIMARY KEY,
                amount float NOT NULL,
                category VARCHAR(50),
                note VARCHAR(300),
                date VARCHAR(50)
            )"""

         create_expense_table_query = """
            CREATE TABLE IF NOT EXISTS expense_table(
                expense_id INT AUTO_INCREMENT PRIMARY KEY,
                amount float NOT NULL,
                category VARCHAR(50),
                note VARCHAR(300),
                date VARCHAR(50)
            )"""

         cursor.execute(create_addmoney_table_query)
         cursor.execute(create_expense_table_query)

         self.mydb.commit()

    def closeEvent(self, event):
        if self.mydb and self.mydb.is_connected():
            self.mydb.close()
        event.accept()

if __name__ == "__main__":
       app = QApplication(sys.argv)
       window = MainWindow()
       window.show()
       app.exec()




