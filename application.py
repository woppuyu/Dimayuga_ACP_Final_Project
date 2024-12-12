import customtkinter as ctk
from customtkinter import CTkFont
from CTkMessagebox import CTkMessagebox
from tkinter import ttk
import mysql.connector
from mysql.connector import Error
import re

# Admin authentication credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class DatabaseConnection:
    # Database connection manager with automatic cleanup
    def __init__(self):
        self.connection = None
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="schoolsuppliesdonationdb"
            )
            if self.connection.is_connected():
                print("Successfully connected to the database")
        except Error as e:
            print(f"Error connecting to database: {e}")
            raise Exception(f"Database connection failed: {e}")
            
    def __del__(self):
        if hasattr(self, 'connection') and self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

    def update_supply_quantity(self, supply_name, quantity):
        try:
            cursor = self.connection.cursor()
            check_query = "SELECT quantity FROM supplies WHERE supply_name = %s"
            cursor.execute(check_query, (supply_name,))
            result = cursor.fetchone()
            
            if result:
                update_query = """
                    UPDATE supplies 
                    SET quantity = quantity + %s 
                    WHERE supply_name = %s
                """
                cursor.execute(update_query, (quantity, supply_name))
            else:
                insert_query = """
                    INSERT INTO supplies (supply_name, quantity) 
                    VALUES (%s, %s)
                """
                cursor.execute(insert_query, (supply_name, quantity))
            
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error: {e}")
            return False
        finally:
            cursor.close()

    def get_all_supplies(self):
        try:
            cursor = self.connection.cursor()
            query = "SELECT supply_name, quantity FROM supplies ORDER BY supply_name"
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
            return []
        finally:
            cursor.close()

    def get_supply_id(self, supply_name):
        try:
            cursor = self.connection.cursor()
            query = "SELECT id FROM supplies WHERE supply_name = %s"
            cursor.execute(query, (supply_name,))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            cursor.close()

    def add_donation(self, donor_name, contact_info, barangay, city, province, supply_name, quantity):
        try:
            cursor = self.connection.cursor()
            supply_id = self.get_supply_id(supply_name)
            if not supply_id:
                cursor.execute("""
                    INSERT INTO supplies (supply_name, quantity) 
                    VALUES (%s, 0)
                """, (supply_name,))
                self.connection.commit()
                supply_id = cursor.lastrowid

            cursor.execute("""
                UPDATE supplies 
                SET quantity = quantity + %s 
                WHERE id = %s
            """, (quantity, supply_id))

            full_address = f"{barangay}, {city}, {province}" if barangay else f"{city}, {province}"

            cursor.execute("""
                INSERT INTO donations 
                (donor_name, contact_info, address, supply_id, quantity) 
                VALUES (%s, %s, %s, %s, %s)
            """, (donor_name, contact_info, full_address, supply_id, quantity))
            
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error: {e}")
            return False
        finally:
            cursor.close()

    def get_all_donations(self):
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT d.donor_name, d.contact_info, d.address, s.supply_name, d.quantity 
                FROM donations d
                JOIN supplies s ON d.supply_id = s.id
                ORDER BY d.donor_name
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
            return []
        finally:
            cursor.close()

    def withdraw_supply(self, supply_name, quantity):
        try:
            cursor = self.connection.cursor()
            check_query = "SELECT quantity FROM supplies WHERE supply_name = %s"
            cursor.execute(check_query, (supply_name,))
            result = cursor.fetchone()
            
            if not result:
                return False, "Supply not found"
            
            current_quantity = result[0]
            if current_quantity < quantity:
                return False, "Not enough supply available"
            
            update_query = """
                UPDATE supplies 
                SET quantity = quantity - %s 
                WHERE supply_name = %s
            """
            cursor.execute(update_query, (quantity, supply_name))
            self.connection.commit()
            return True, "Withdrawal successful"
        except Error as e:
            print(f"Error: {e}")
            return False, str(e)
        finally:
            cursor.close()

    def record_withdrawal(self, supply_id, quantity):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO withdrawals (supply_id, quantity)
                VALUES (%s, %s)
            """, (supply_id, quantity))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Error: {e}")
            return False
        finally:
            cursor.close()

    def get_all_withdrawals(self):
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT s.supply_name, w.quantity, w.withdrawal_date 
                FROM withdrawals w
                JOIN supplies s ON w.supply_id = s.id
                ORDER BY w.withdrawal_date DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
            return []
        finally:
            cursor.close()

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Classroom Connect")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Configure dark mode appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize database and UI framework
        try:
            self.db = DatabaseConnection()
        except Exception as e:
            error_label = ctk.CTkLabel(root, text=f"Error connecting to database: {e}")
            error_label.pack(pady=20)
            return
        
        # Initialize frame management system
        self.container = ctk.CTkFrame(root)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Register all application pages
        self.frames = {}
        
        for F in (MainMenu, DonationPage, SuppliesPage, LoginPage, AdminPage, DonationsViewPage, WithdrawalPage, WithdrawalRecordsPage):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(MainMenu)
        
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        # Add on_show method call if it exists
        if hasattr(frame, 'on_show'):
            frame.on_show()

    def quit_app(self):
        # Close database connection
        if hasattr(self, 'db'):
            self.db.connection.close()
            print("Database connection closed")
        # Destroy the root window
        self.root.quit()

class MainMenu(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        
        # Create a container frame to hold content
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="x", padx=20, pady=(50,0))
        
        label = ctk.CTkLabel(content_frame, 
            text="Welcome to Classroom Connect",
            font=CTkFont(family="Helvetica", size=24, weight="bold"),  # Changed size from 14 to 24
        )
        label.pack(pady=(0,20))
        
        button1 = ctk.CTkButton(content_frame, 
            text="Add Donation",
            command=lambda: controller.show_frame(DonationPage),
            width=200,
            fg_color="#2f9e44",
            hover_color="#2b8a3e"
        )
        button1.pack(pady=10)
        
        button2 = ctk.CTkButton(self, 
            text="View Supplies",
            command=lambda: controller.show_frame(SuppliesPage),
            width=200,
            fg_color="#1971c2",
            hover_color="#1864ab"
        )
        button2.pack(pady=10)
        
        button3 = ctk.CTkButton(self, 
            text="Admin View",
            command=lambda: controller.show_frame(LoginPage),
            width=200,
            fg_color="#e8590c",
            hover_color="#d9480f"
        )
        button3.pack(pady=10)
        
        exit_button = ctk.CTkButton(self, 
            text="Exit",
            command=lambda: controller.quit_app(),
            width=200,
            fg_color="#e03131",
            hover_color="#c92a2a"
        )
        exit_button.pack(pady=10)

class DonationPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.entries = {}
        
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="x", padx=20, pady=(50,0))
        
        headline = ctk.CTkLabel(main_container,
            text="Add Your Donation",
            font=CTkFont(family="Helvetica", size=14, weight="bold")
        )
        headline.pack(pady=20)
        
        form_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        form_frame.pack(padx=40, pady=10)
        
        # Basic fields
        labels = ['Donor Name:', 'Contact Info:']
        row = 0
        for label_text in labels:
            label = ctk.CTkLabel(form_frame,
                text=label_text,
                font=CTkFont(family="Helvetica", size=10)
            )
            label.grid(row=row, column=0, pady=10, sticky="e", padx=5)
            entry = ctk.CTkEntry(form_frame, width=400)
            entry.grid(row=row, column=1, pady=10, padx=5, columnspan=3)
            self.entries[label_text] = entry
            row += 1

        # Address fields
        address_label = ctk.CTkLabel(form_frame,
            text="Address:",
            font=CTkFont(family="Helvetica", size=10)
        )
        address_label.grid(row=row, column=0, pady=10, sticky="e", padx=5)

        # Address entries with placeholders
        for field, col in [('Barangay:', 1), ('City:', 2), ('Province:', 3)]:
            self.entries[field] = ctk.CTkEntry(form_frame, width=130, placeholder_text=field.replace(':', ''))
            self.entries[field].grid(row=row, column=col, pady=10, padx=2)
        
        row += 1

        # Supply fields
        supply_items = [
            'Pencil', 'Eraser', 'Paper', 'Pen', 'Folder', 'Ruler',
            'Coloring Material', 'Glue', 'Scissors', 'Sharpener',
            'Notebook', 'Books', 'Others'
        ]

        supply_label = ctk.CTkLabel(form_frame,
            text="Supply Name:",
            font=CTkFont(family="Helvetica", size=10)
        )
        supply_label.grid(row=row, column=0, pady=10, sticky="e", padx=5)
        
        supply_combo = ctk.CTkOptionMenu(form_frame, width=400, values=supply_items)
        supply_combo.set("Select an item")
        supply_combo.grid(row=row, column=1, pady=10, padx=5, columnspan=3)
        self.entries['Supply Name:'] = supply_combo
        
        row += 1

        quantity_label = ctk.CTkLabel(form_frame,
            text="Quantity:",
            font=CTkFont(family="Helvetica", size=10)
        )
        quantity_label.grid(row=row, column=0, pady=10, sticky="e", padx=5)
        
        quantity_entry = ctk.CTkEntry(form_frame, width=400)
        quantity_entry.grid(row=row, column=1, pady=10, padx=5, columnspan=3)
        self.entries['Quantity:'] = quantity_entry

        # Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.grid(row=row+1, column=0, columnspan=4, pady=20)
        
        add_button = ctk.CTkButton(button_frame,
            text="Add Donation",
            command=self.add_donation,
            fg_color="#2f9e44",
            hover_color="#2b8a3e"
        )
        add_button.pack(side="left", padx=10)
        
        back_button = ctk.CTkButton(button_frame,
            text="Back to Menu",
            command=lambda: controller.show_frame(MainMenu),
            fg_color="#e03131",
            hover_color="#c92a2a"
        )
        back_button.pack(side="left", padx=10)

    # Keep existing methods, but update clear_fields
    def clear_fields(self):
        for key, entry in self.entries.items():
            if isinstance(entry, ctk.CTkOptionMenu):
                entry.set("Select an item")
            else:
                entry.delete(0, "end")

    def validate_fields(self):
        for label, entry in self.entries.items():
            value = entry.get() if not isinstance(entry, ctk.CTkOptionMenu) else entry.get()
            
            # Skip optional Barangay field
            if label == 'Barangay:' and not value.strip():
                continue
                
            # Validate contact information format
            if label == 'Contact Info:':
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                phone_pattern = r'^(09|\+63)[0-9]{9}$'
                
                if not (re.match(email_pattern, value) or re.match(phone_pattern, value)):
                    self.show_warning("Contact info must be a valid email address or Philippine phone number (09XXXXXXXXX or +63XXXXXXXXX)")
                    return False
                continue
            
            # Validate required fields
            if not value or value.strip() == "" or value == "Select an item":
                self.show_warning(f"Please fill in the {label.replace(':', '')} field")
                return False
                
            # Validate quantity constraints
            if label == 'Quantity:':
                try:
                    qty = int(value)
                    if qty <= 0:
                        self.show_warning("Quantity must be greater than 0")
                        return False
                    if qty > 2147483647:
                        self.show_warning("Quantity cannot exceed 2,147,483,647")
                        return False
                except ValueError:
                    self.show_warning("Quantity must be a valid number")
                    return False
        return True

    def show_warning(self, message):
        CTkMessagebox(title="Invalid Input", message=message, icon="warning")

    def add_donation(self):
        if self.validate_fields():
            try:
                donor_name = self.entries['Donor Name:'].get()
                contact_info = self.entries['Contact Info:'].get()
                barangay = self.entries['Barangay:'].get().strip()
                city = self.entries['City:'].get().strip()
                province = self.entries['Province:'].get().strip()
                supply_name = self.entries['Supply Name:'].get()
                quantity = int(self.entries['Quantity:'].get())
                
                if self.controller.db.add_donation(donor_name, contact_info, barangay, city, province, supply_name, quantity):
                    CTkMessagebox(title="Success", message="Your donation has been recorded.", icon="check")
                    self.clear_fields()
                    self.controller.show_frame(MainMenu)
                else:
                    CTkMessagebox(title="Error", message="Failed to record donation.", icon="cancel")
            except Exception as e:
                CTkMessagebox(title="Error", message=f"An error occurred: {str(e)}", icon="cancel")

class SuppliesPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        label = ctk.CTkLabel(self,
            text="View Supplies",
            font=CTkFont(family="Helvetica", size=14, weight="bold")
        )
        label.pack(pady=20)

        # Create Treeview Frame with fixed width
        tree_frame = ctk.CTkFrame(self, width=400)
        tree_frame.pack(pady=10, padx=200, fill="y")
        tree_frame.pack_propagate(False)

        # Create a frame for the treeview and scrollbar
        tree_scroll_frame = ctk.CTkFrame(tree_frame, fg_color="transparent")
        tree_scroll_frame.pack(fill="both", expand=True)

        # Create Treeview with scrollbar
        self.tree = ttk.Treeview(tree_scroll_frame, 
                                columns=("Supply Name", "Quantity"), 
                                show='headings',
                                height=10)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_scroll_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        
        # Configure the treeview to use scrollbar
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Format columns with adjusted widths
        self.tree.heading("Supply Name", text="Supply Name")
        self.tree.heading("Quantity", text="Quantity")
        
        self.tree.column("Supply Name", width=200)
        self.tree.column("Quantity", width=150)
        
        self.tree.pack(side="left", fill="both", expand=True)

        # Buttons frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=10)

        # Refresh button
        refresh_button = ctk.CTkButton(button_frame,
            text="Refresh",
            command=self.refresh_data,
            fg_color="#2f9e44",
            hover_color="#2b8a3e"
        )
        refresh_button.pack(side="left", padx=10)
        
        back_button = ctk.CTkButton(button_frame,
            text="Back to Menu",
            command=lambda: controller.show_frame(MainMenu),
            fg_color="#e03131",
            hover_color="#c92a2a"
        )
        back_button.pack(side="left", padx=10)

    def on_show(self):
        """Called when the frame becomes visible"""
        self.refresh_data()
        
    def refresh_data(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Fetch and insert new data
        supplies = self.controller.db.get_all_supplies()
        for supply in supplies:
            self.tree.insert("", "end", values=supply)

class AdminPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        label = ctk.CTkLabel(self,
            text="Admin Dashboard",
            font=CTkFont(family="Helvetica", size=14, weight="bold")
        )
        label.pack(pady=20)

        # Add Supply Summary Table
        summary_label = ctk.CTkLabel(self,
            text="Available Supplies",
            font=CTkFont(family="Helvetica", size=12, weight="bold")
        )
        summary_label.pack(pady=10)

        # Create centered container for the table
        outer_frame = ctk.CTkFrame(self, fg_color="transparent")
        outer_frame.pack(pady=10, expand=True)

        # Create fixed-width frame for the table
        self.supplies_frame = ctk.CTkFrame(outer_frame, width=400, height=300)
        self.supplies_frame.pack(expand=True)
        self.supplies_frame.pack_propagate(False)  # Keep fixed size

        # Create Treeview (removed scrollbar)
        self.supplies_tree = ttk.Treeview(self.supplies_frame, 
            columns=("Supply Name", "Quantity"),
            show='headings',
            height=10
        )

        # Configure columns
        self.supplies_tree.heading("Supply Name", text="Supply Name")
        self.supplies_tree.heading("Quantity", text="Quantity")
        
        self.supplies_tree.column("Supply Name", width=200)
        self.supplies_tree.column("Quantity", width=150)
        
        self.supplies_tree.pack(expand=True, fill="both", padx=5, pady=5)

        # Button container
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)
        
        # Create a frame for the side-by-side buttons
        top_buttons_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        top_buttons_frame.pack(pady=10)
        
        view_records_btn = ctk.CTkButton(top_buttons_frame,
            text="View Donation Records",
            command=lambda: controller.show_frame(DonationsViewPage),
            width=200,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        view_records_btn.pack(side="left", padx=5)
        
        withdraw_btn = ctk.CTkButton(top_buttons_frame,
            text="Withdraw Supplies",
            command=lambda: controller.show_frame(WithdrawalPage),
            width=200,
            fg_color="#FF9800",
            hover_color="#F57C00"
        )
        withdraw_btn.pack(side="left", padx=5)

        # Add withdrawal records button
        withdrawal_records_btn = ctk.CTkButton(top_buttons_frame,
            text="View Withdrawals",
            command=lambda: controller.show_frame(WithdrawalRecordsPage),
            width=200,
            fg_color="#9C27B0",
            hover_color="#7B1FA2"
        )
        withdrawal_records_btn.pack(side="left", padx=5)
        
        # Back button
        back_button = ctk.CTkButton(button_frame,
            text="Back to Menu",
            command=lambda: controller.show_frame(MainMenu),
            width=200,
            fg_color="#e03131",
            hover_color="#c92a2a"
        )
        back_button.pack(pady=10)

    def on_show(self):
        """Called when the frame becomes visible"""
        self.refresh_supplies()
        
    def refresh_supplies(self):
        for item in self.supplies_tree.get_children():
            self.supplies_tree.delete(item)
            
        supplies = self.controller.db.get_all_supplies()
        for supply in supplies:
            self.supplies_tree.insert("", "end", values=supply)

class DonationsViewPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        label = ctk.CTkLabel(self,
            text="Donation Records",
            font=CTkFont(family="Helvetica", size=14, weight="bold")
        )
        label.pack(pady=20)

        # Create Treeview Frame with transparent background
        self.tree_frame = ctk.CTkFrame(self, width=600, fg_color="transparent")
        self.tree_frame.pack(pady=10, padx=100, fill="y")
        self.tree_frame.pack_propagate(False)

        # Create a frame for the treeview and scrollbar
        tree_scroll_frame = ctk.CTkFrame(self.tree_frame, fg_color="transparent")
        tree_scroll_frame.pack(fill="both", expand=True)

        # Create Treeview with scrollbar
        self.tree = ttk.Treeview(tree_scroll_frame, 
            columns=("Donor Name", "Contact", "Address", "Supply Name", "Quantity"),
            show='headings',
            height=10)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_scroll_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        
        # Configure the treeview to use scrollbar
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Format columns with balanced widths
        columns = {
            "Donor Name": 150,
            "Contact": 120,
            "Address": 170,
            "Supply Name": 100,
            "Quantity": 60
        }
        
        for col, width in columns.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        self.tree.pack(side="left", fill="both", expand=True)

        # Buttons Frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=10)

        refresh_button = ctk.CTkButton(button_frame,
            text="Refresh",
            command=self.refresh_data,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        refresh_button.pack(side="left", padx=5)
        
        back_button = ctk.CTkButton(button_frame,
            text="Back to Admin",
            command=lambda: controller.show_frame(AdminPage),
            fg_color="#f44336",
            hover_color="#d32f2f"
        )
        back_button.pack(side="left", padx=5)

    def on_show(self):
        self.refresh_data()
        
    def refresh_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        donations = self.controller.db.get_all_donations()
        for donation in donations:
            self.tree.insert("", "end", values=donation)

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="x", padx=20, pady=(50,0))
        
        # Login form
        login_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        login_frame.pack(pady=10)
        
        # Title
        title = ctk.CTkLabel(login_frame,
            text="Admin Login",
            font=CTkFont(family="Helvetica", size=14, weight="bold")
        )
        title.pack(pady=20)
        
        # Username
        self.username = ctk.CTkEntry(login_frame, 
            width=300,
            placeholder_text="Username"
        )
        self.username.pack(pady=10)
        
        # Password
        self.password = ctk.CTkEntry(login_frame, 
            width=300,
            placeholder_text="Password",
            show="*"
        )
        self.password.pack(pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(login_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        
        login_button = ctk.CTkButton(button_frame,
            text="Login",
            command=self.verify_login,
            fg_color="#4CAF50",
            hover_color="#45a049",
            width=140
        )
        login_button.pack(side="left", padx=10)
        
        cancel_button = ctk.CTkButton(button_frame,
            text="Cancel",
            command=lambda: controller.show_frame(MainMenu),
            fg_color="#f44336",
            hover_color="#d32f2f",
            width=140
        )
        cancel_button.pack(side="left", padx=10)

    def verify_login(self):
        username = self.username.get()
        password = self.password.get()
        
        if not username or not password:
            CTkMessagebox(title="Error", message="Please enter username and password", icon="cancel")
            return
            
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            self.username.delete(0, "end")
            self.password.delete(0, "end")
            self.controller.show_frame(AdminPage)
        else:
            CTkMessagebox(title="Error", message="Invalid username or password", icon="cancel")

class WithdrawalPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = ctk.CTkLabel(self,
            text="Withdraw Supplies",
            font=CTkFont(family="Helvetica", size=14, weight="bold")
        )
        label.pack(pady=20)
        
        # Create form frame
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(pady=20)
        
        # Get supply items
        supply_items = [
            'Pencil', 'Eraser', 'Paper', 'Pen', 'Folder', 'Ruler',
            'Coloring Material', 'Glue', 'Scissors', 'Sharpener',
            'Notebook', 'Books', 'Others'
        ]
        
        # Supply selection
        supply_label = ctk.CTkLabel(form_frame,
            text="Select Supply:",
            font=CTkFont(family="Helvetica", size=10)
        )
        supply_label.pack()
        
        self.supply_combo = ctk.CTkOptionMenu(form_frame, 
            values=supply_items,
            width=300
        )
        self.supply_combo.set("Select an item")
        self.supply_combo.pack(pady=5)
        
        # Quantity entry
        quantity_label = ctk.CTkLabel(form_frame,
            text="Quantity:",
            font=CTkFont(family="Helvetica", size=10)
        )
        quantity_label.pack()
        
        self.quantity_entry = ctk.CTkEntry(form_frame, width=300)
        self.quantity_entry.pack(pady=5)
        
        # Buttons frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)
        
        withdraw_button = ctk.CTkButton(button_frame,
            text="Withdraw",
            command=self.withdraw_supply,
            fg_color="#4CAF50",
            hover_color="#45a049",
            width=140
        )
        withdraw_button.pack(side="left", padx=5)
        
        back_button = ctk.CTkButton(button_frame,
            text="Back to Admin",
            command=lambda: controller.show_frame(AdminPage),
            fg_color="#f44336",
            hover_color="#d32f2f",
            width=140
        )
        back_button.pack(side="left", padx=5)
        
    def withdraw_supply(self):
        supply_name = self.supply_combo.get()
        if supply_name == "Select an item":
            CTkMessagebox(title="Error", message="Please select a supply item", icon="warning")
            return
            
        try:
            quantity = int(self.quantity_entry.get())
            if quantity <= 0:
                CTkMessagebox(title="Error", message="Quantity must be greater than 0", icon="warning")
                return
        except ValueError:
            CTkMessagebox(title="Error", message="Please enter a valid number for quantity", icon="warning")
            return
            
        success, message = self.controller.db.withdraw_supply(supply_name, quantity)
        if success:
            # Get supply_id and record withdrawal
            supply_id = self.controller.db.get_supply_id(supply_name)
            if supply_id:
                self.controller.db.record_withdrawal(supply_id, quantity)
            
            CTkMessagebox(title="Success", message=message, icon="check")
            self.supply_combo.set("Select an item")
            self.quantity_entry.delete(0, "end")
            self.controller.show_frame(AdminPage)
        else:
            CTkMessagebox(title="Error", message=message, icon="cancel")

class WithdrawalRecordsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        label = ctk.CTkLabel(self,
            text="Withdrawal Records",
            font=CTkFont(family="Helvetica", size=14, weight="bold")
        )
        label.pack(pady=20)

        # Create Treeview Frame
        self.tree_frame = ctk.CTkFrame(self, width=600, fg_color="transparent")
        self.tree_frame.pack(pady=10, padx=100, fill="y")
        self.tree_frame.pack_propagate(False)

        # Create a frame for the treeview and scrollbar
        tree_scroll_frame = ctk.CTkFrame(self.tree_frame, fg_color="transparent")
        tree_scroll_frame.pack(fill="both", expand=True)

        # Create Treeview with scrollbar
        self.tree = ttk.Treeview(tree_scroll_frame, 
            columns=("Supply Name", "Quantity", "Date"),
            show='headings',
            height=10)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_scroll_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Format columns
        columns = {
            "Supply Name": 200,
            "Quantity": 100,
            "Date": 200
        }
        
        for col, width in columns.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width)
        
        self.tree.pack(side="left", fill="both", expand=True)

        # Buttons Frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=10)

        refresh_button = ctk.CTkButton(button_frame,
            text="Refresh",
            command=self.refresh_data,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        refresh_button.pack(side="left", padx=5)
        
        back_button = ctk.CTkButton(button_frame,
            text="Back to Admin",
            command=lambda: controller.show_frame(AdminPage),
            fg_color="#f44336",
            hover_color="#d32f2f"
        )
        back_button.pack(side="left", padx=5)

    def on_show(self):
        self.refresh_data()
        
    def refresh_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        withdrawals = self.controller.db.get_all_withdrawals()
        for withdrawal in withdrawals:
            self.tree.insert("", "end", values=withdrawal)

if __name__ == "__main__":
    root = ctk.CTk()
    app = MainApp(root)
    root.mainloop()