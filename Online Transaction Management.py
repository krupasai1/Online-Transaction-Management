import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import sqlite3

class SQLFrontend:
    def __init__(self, root):
        self.root = root
        self.root.title("SQL Frontend")

        # Connect to SQLite database
        db_path = r'C:\Users\Krupa\Desktop\DBMS SQL\Transactions.db'
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        # Create Transactions table if not exists
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Transactions (
                                id INTEGER PRIMARY KEY,                            
                                Customer_Name TEXT NOT NULL,
                                Product_Name TEXT NOT NULL,
                                Cost REAL NOT NULL,
                                Card_Number TEXT NOT NULL,
                                OTP TEXT NOT NULL
                            )''')

        self.conn.commit()

        # List of CSV table names
        self.csv_tables = ['Address', 'Bill', 'Customer Fix', 'Customer', 'Employee new', 'Employee', 
                           'Order Product', 'Order', 'Orders', 'Payment', 'Product Details', 'Product group', 
                           'Product', 'Reviews', 'Supplier', 'Voucher', 'Zipcode']

        # List of DB table names
        self.db_tables = ['Transactions']

        # Create a frame to hold the table selection
        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(pady=10)
        
        self.selected_table = tk.StringVar()
        
        # Create a label and dropdown for selecting a table
        self.table_label = tk.Label(self.table_frame, text="Select a table:")
        self.table_label.grid(row=0, column=0)
        
        self.table_dropdown = tk.OptionMenu(self.table_frame, self.selected_table, *self.csv_tables, *self.db_tables, command=self.show_buy_button)
        self.table_dropdown.grid(row=0, column=1)
        
        # Create a button to display the selected table
        self.show_table_button = tk.Button(self.table_frame, text="Show Table", command=self.show_table)
        self.show_table_button.grid(row=0, column=2)
        
        # Create a Buy button (initially disabled)
        self.buy_button = tk.Button(self.table_frame, text="Buy", command=self.show_product_page)
        self.buy_button.grid(row=0, column=3)
        self.buy_button.config(state="disabled")
        
        # Create a Search button
        self.search_button = tk.Button(self.table_frame, text="Search", command=self.show_search_window)
        self.search_button.grid(row=0, column=4)
        
        # Create a text widget to display the table data
        self.table_data_text = tk.Text(self.root, height=100, width=130, state="disabled")
        self.table_data_text.pack(pady=10)
        
        # List to store selected products as tuples (name, cost)
        self.selected_products = []

    def show_buy_button(self, selected_table):
        if selected_table == "Product":
            self.buy_button.config(state="normal")
        else:
            self.buy_button.config(state="disabled")
    
    def show_table(self):
        # Clear the text widget
        self.table_data_text.delete('1.0', tk.END)
        
        # Get the selected table name
        table_name = self.selected_table.get()
        
        # Check if the selected table is a CSV table
        if table_name in self.csv_tables:
            # Construct the full path to the CSV file
            csv_file = r'C:\Users\Krupa\Desktop\DBMS SQL\{}.csv'.format(table_name)
        
            try:
                df = pd.read_csv(csv_file)
                # Display the data in the text widget
                self.table_data_text.config(state="normal")
                self.table_data_text.delete('1.0', tk.END)
                self.table_data_text.insert(tk.END, df.to_string(index=False))
                self.table_data_text.config(state="disabled")
                    
            except FileNotFoundError:
                self.table_data_text.config(state="normal")
                self.table_data_text.insert(tk.END, f"CSV file '{csv_file}' not found.")
                self.table_data_text.config(state="disabled")
        elif table_name in self.db_tables:
            try:
                # Fetch data from the Transactions table
                self.cursor.execute("SELECT * FROM Transactions")
                data = self.cursor.fetchall()

                # Display the data in the text widget
                self.table_data_text.config(state="normal")
                self.table_data_text.delete('1.0', tk.END)
                for row in data:
                    self.table_data_text.insert(tk.END, row)
                    self.table_data_text.insert(tk.END, "\n")
                self.table_data_text.config(state="disabled")
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error fetching data from Transactions table: {e}")

    def show_product_page(self):
        # Create a new window for selecting products
        product_window = tk.Toplevel(self.root)
        product_window.title("Select Products")

        # Get the selected table name
        table_name = self.selected_table.get()

        # Construct the full path to the CSV file (only if the selected table is a CSV table)
        if table_name in self.csv_tables:
            csv_file = r'C:\Users\Krupa\Desktop\DBMS SQL\{}.csv'.format(table_name)

            try:
                df = pd.read_csv(csv_file)
                products = df[['Product_Name', 'Cost']].values.tolist()

                # Calculate the number of rows and columns needed
                num_rows = (len(products) + 3) // 4  # Ensure at least 4 products are displayed in each row
                num_columns = 4

                # Create Checkbuttons for each product in a grid layout
                for i, (product, cost) in enumerate(products):
                    row = i // num_columns
                    column = i % num_columns

                    var = tk.BooleanVar()
                    tk.Checkbutton(product_window, text=f"{product} - ₹{cost}", variable=var).grid(row=row, column=column, sticky="w")

                    # Add product to selected products list when selected
                    var.trace('w', lambda *args, product=product, cost=cost, var=var: self.update_selected_products(product, cost, var))

                # Create Pay button
                pay_button = tk.Button(product_window, text="Pay", command=lambda: self.make_payment(product_window))
                pay_button.grid(row=num_rows, columnspan=num_columns, pady=10)

            except FileNotFoundError:
                messagebox.showerror("Error", f"CSV file '{csv_file}' not found.")
                product_window.destroy()
        else:
            messagebox.showerror("Error", "Cannot buy from a database table.")

    def update_selected_products(self, product, cost, var):
        if var.get():
            self.selected_products.append((product, cost))
        else:
            self.selected_products = [(p, c) for p, c in self.selected_products if p != product]

    def make_payment(self, product_window):
        if not self.selected_products:
            messagebox.showerror("Error", "Please select at least one product.")
            return

        # Create a new window for payment details
        payment_window = tk.Toplevel(self.root)
        payment_window.title("Payment Details")

        # Display selected products and total cost
        tk.Label(payment_window, text="Selected Products:", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=20, pady=10)
        for product, cost in self.selected_products:
            tk.Label(payment_window, text=f"{product}: ₹{cost}", font=("Helvetica", 10)).pack(anchor="w", padx=40)

        total_cost = sum([product[1] for product in self.selected_products])
        tk.Label(payment_window, text=f"Total Cost: ₹{total_cost}", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=20, pady=10)

        # Dummy debit card transaction form
        tk.Label(payment_window, text="Card Number:", font=("Helvetica", 10)).pack(anchor="w", padx=20, pady=5)
        self.card_number_entry = tk.Entry(payment_window)
        self.card_number_entry.pack(anchor="w", padx=20)

        tk.Label(payment_window, text="CVV:", font=("Helvetica", 10)).pack(anchor="w", padx=20, pady=5)
        cvv_entry = tk.Entry(payment_window)
        cvv_entry.pack(anchor="w", padx=20)

        tk.Label(payment_window, text="Card Name:", font=("Helvetica", 10)).pack(anchor="w", padx=20, pady=5)
        self.card_name_entry = tk.Entry(payment_window)
        self.card_name_entry.pack(anchor="w", padx=20)

        tk.Label(payment_window, text="OTP:", font=("Helvetica", 10)).pack(anchor="w", padx=20, pady=5)
        self.otp_entry = tk.Entry(payment_window)
        self.otp_entry.pack(anchor="w", padx=20)

        # Proceed button for the dummy transaction
        proceed_button = tk.Button(payment_window, text="Proceed", font=("Helvetica", 12, "bold"), bg="green", fg="white", command=lambda: self.complete_transaction(payment_window))
        proceed_button.pack(anchor="center", pady=20)

        # Destroy product window
        product_window.destroy()

    def complete_transaction(self, payment_window):
        card_number = self.card_number_entry.get()
        card_name = self.card_name_entry.get()
        otp = self.otp_entry.get()

        if not card_number or not card_name or not otp:
            messagebox.showerror("Error", "Please enter card details and OTP.")
            return

        try:
            # Store transaction in the database
            for product, cost in self.selected_products:
                self.cursor.execute("INSERT INTO Transactions (Customer_Name, Product_Name, Cost, Card_Number, OTP) VALUES (?, ?, ?, ?, ?)",
                                    (card_name, product, cost, card_number, otp))

            self.conn.commit()

            messagebox.showinfo("Payment Successful", "Payment successful!")

            # Clear selected products and close payment window
            self.selected_products.clear()
            payment_window.destroy()

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error completing transaction: {e}")

    def show_search_window(self):
        # Create a new window for search functionality
        search_window = tk.Toplevel(self.root)
        search_window.title("Search")

        # Create labels and entry fields for search criteria
        tk.Label(search_window, text="Search by ID, Customer Name, Product Name, Cost, Card Number, or OTP:").pack(pady=10)
        search_entry = tk.Entry(search_window, width=50)
        search_entry.pack(pady=5)

        # Create search button
        search_button = tk.Button(search_window, text="Search", command=lambda: self.search_transaction(search_entry.get()))
        search_button.pack(pady=10)

    def search_transaction(self, search_criteria):
        try:
            # Search for transactions based on the provided criteria
            query = f"SELECT * FROM Transactions WHERE id LIKE ? OR Customer_Name LIKE ? OR Product_Name LIKE ? OR Cost LIKE ? OR Card_Number LIKE ? OR OTP LIKE ?"
            self.cursor.execute(query, ('%' + search_criteria + '%', '%' + search_criteria + '%', '%' + search_criteria + '%', '%' + search_criteria + '%', '%' + search_criteria + '%', '%' + search_criteria + '%'))
            results = self.cursor.fetchall()

            if results:
                # Display search results in a new window
                search_results_window = tk.Toplevel(self.root)
                search_results_window.title("Search Results")

                # Display search results in a treeview widget
                tree = ttk.Treeview(search_results_window)
                tree["columns"] = ("ID", "Customer Name", "Product Name", "Cost", "Card Number", "OTP")
                tree.heading("ID", text="ID")
                tree.heading("Customer Name", text="Customer Name")
                tree.heading("Product Name", text="Product Name")
                tree.heading("Cost", text="Cost")
                tree.heading("Card Number", text="Card Number")
                tree.heading("OTP", text="OTP")

                for result in results:
                    tree.insert("", "end", values=result)

                tree.pack()

            else:
                messagebox.showinfo("Search Results", "No matching transactions found.")

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error searching transactions: {e}")

# Create the Tkinter root window
root = tk.Tk()

# Create an instance of the SQLFrontend class
app = SQLFrontend(root)

# Run the Tkinter event loop
root.mainloop()
