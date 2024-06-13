import pyodbc
from faker import Faker
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Initialize Faker
fake = Faker()

# Database connection parameters
server = 'MOHIT-LAPTOP\\SQLEXPRESS'  # Double backslashes for escaping in Python strings
database = 'Ecomerce_Sales'  # Use the existing database name
username = 'MOHIT-LAPTOP\\mgmoh'  # Assuming Windows Authentication (Trusted Connection)

# Function to establish connection to SQL Server
def connect_to_database(server, database, username):
    conn = pyodbc.connect(f'DRIVER={{SQL Server Native Client 11.0}};SERVER={server};DATABASE={database};UID={username};Trusted_connection=yes')
    return conn

# Function to drop tables if they exist
def drop_tables(conn):
    cursor = conn.cursor()
    try:
        cursor.execute('''
        DROP TABLE IF EXISTS Sales;
        DROP TABLE IF EXISTS OrderItem;
        DROP TABLE IF EXISTS [Order];
        DROP TABLE IF EXISTS PriceHistory;
        DROP TABLE IF EXISTS Variant;
        DROP TABLE IF EXISTS Product;
        DROP TABLE IF EXISTS Customer;
        ''')
        conn.commit()
        print("Tables dropped successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Error dropping tables: {str(e)}")
    finally:
        cursor.close()

def generate_phone_number():
    return ''.join(random.choices('0123456789', k=10))

# Function to create Customer table
def create_customer_table(conn):
    cursor = conn.cursor()
    try:
        cursor.execute('''
        CREATE TABLE Customer (
            CustomerID INT PRIMARY KEY,
            Name NVARCHAR(100),
            Email NVARCHAR(100),
            ContactNumber NVARCHAR(10),
            ShippingAddress NVARCHAR(255),
            BillingAddress NVARCHAR(255)
        );
        ''')
        conn.commit()
        print("Customer table created successfully.")

        # Insert sample data for Customers with sequential CustomerID
        for i in range(1, 11):  # Assuming we want 10 rows
            contact_number = generate_phone_number()
            cursor.execute('''
            INSERT INTO Customer (CustomerID, Name, Email, ContactNumber, ShippingAddress, BillingAddress)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (i, fake.name(), fake.email(), contact_number, fake.address(), fake.address()))
            conn.commit()
        print("Sample data inserted into Customer table.")

    except Exception as e:
        conn.rollback()
        print(f"Error creating Customer table: {str(e)}")
    finally:
        cursor.close()

product_categories = [
    'Electronics', 'Books', 'Clothing', 'Home & Kitchen', 'Sports & Outdoors', 'Beauty & Personal Care'
]

product_names = {
    'Electronics': ['Smartphone', 'Laptop', 'Headphones', 'Camera', 'Smartwatch'],
    'Books': ['Novel', 'Science Book', 'History Book', 'Children Book', 'Cookbook'],
    'Clothing': ['T-Shirt', 'Jeans', 'Dress', 'Jacket', 'Sweater'],
    'Home & Kitchen': ['Mixer', 'Toaster', 'Cookware', 'Furniture', 'Lamp'],
    'Sports & Outdoors': ['Bicycle', 'Tent', 'Backpack', 'Fitness Tracker', 'Yoga Mat'],
    'Beauty & Personal Care': ['Shampoo', 'Lotion', 'Makeup Kit', 'Perfume', 'Hair Dryer']
}

variant_names = ['Size', 'Color', 'Model', 'Edition', 'Flavor']

def create_product_table(conn):
    cursor = conn.cursor()
    try:
        cursor.execute('''
        CREATE TABLE Product (
            ProductID INT PRIMARY KEY,
            ProductCategory NVARCHAR(100),
            ProductName NVARCHAR(100)
        );
        ''')
        conn.commit()
        print("Product table created successfully.")

        # Insert sample data for Products with predefined categories and names
        product_id_counter = 1
        for category in product_categories:
            for product in product_names[category]:
                cursor.execute('''
                INSERT INTO Product (ProductID, ProductCategory, ProductName)
                VALUES (?, ?, ?)
                ''', (product_id_counter, category, product))
                conn.commit()
                product_id_counter += 1
        print("Sample data inserted into Product table.")

    except Exception as e:
        conn.rollback()
        print(f"Error creating Product table: {str(e)}")
    finally:
        cursor.close()

def create_variant_table(conn):
    cursor = conn.cursor()
    try:
        cursor.execute('''
        CREATE TABLE Variant (
            VariantID INT PRIMARY KEY,
            ProductID INT,
            VariantName NVARCHAR(100),
            LaunchDate DATE,
            DiscontinueDate DATE,
            FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
        );
        ''')
        conn.commit()
        print("Variant table created successfully.")

        # Insert sample data for Variants with predefined variant names
        cursor.execute('SELECT ProductID FROM Product')
        product_ids = [row[0] for row in cursor.fetchall()]

        variant_id_counter = 1
        for product_id in product_ids:
            for _ in range(random.randint(1, 3)):  # Each product can have 1 to 3 variants
                variant_name = random.choice(variant_names) + " " + fake.word().capitalize()
                launch_date = random_date(datetime(2020, 1, 1), datetime(2022, 1, 1))
                discontinue_date = random_date(launch_date, datetime(2023, 6, 1))
                cursor.execute('''
                INSERT INTO Variant (VariantID, ProductID, VariantName, LaunchDate, DiscontinueDate)
                VALUES (?, ?, ?, ?, ?)
                ''', (variant_id_counter, product_id, variant_name, launch_date, discontinue_date))
                conn.commit()
                variant_id_counter += 1
        print("Sample data inserted into Variant table.")

    except Exception as e:
        conn.rollback()
        print(f"Error creating Variant table: {str(e)}")
    finally:
        cursor.close()

# Function to create PriceHistory table
def create_pricehistory_table(conn):
    cursor = conn.cursor()
    try:
        cursor.execute('''
        CREATE TABLE PriceHistory (
            PriceID INT PRIMARY KEY,
            VariantID INT,
            Price DECIMAL(10, 2),
            StartDate DATE,
            EndDate DATE,
            FOREIGN KEY (VariantID) REFERENCES Variant(VariantID)
        );
        ''')
        conn.commit()
        print("PriceHistory table created successfully.")

        # Insert sample data for PriceHistory
        cursor.execute('SELECT VariantID FROM Variant')
        variant_ids = [row[0] for row in cursor.fetchall()]

        price_id_counter = 1
        for variant_id in variant_ids:
            start_date = random_date(datetime(2022, 1, 1), datetime(2022, 6, 1))
            for _ in range(3):
                end_date = random_date(start_date, datetime(2024, 6, 1))
                cursor.execute('''
                INSERT INTO PriceHistory (PriceID, VariantID, Price, StartDate, EndDate)
                VALUES (?, ?, ?, ?, ?)
                ''', (price_id_counter, variant_id, random.uniform(10, 100), start_date, end_date))
                conn.commit()
                price_id_counter += 1
                start_date = end_date
        print("Sample data inserted into PriceHistory table.")

    except Exception as e:
        conn.rollback()
        print(f"Error creating PriceHistory table: {str(e)}")
    finally:
        cursor.close()

# Helper function to generate random past dates
def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

# # Function to create Order table
def create_order_table(conn):
    cursor = conn.cursor()
    try:
        cursor.execute('''
        CREATE TABLE [Order] (
            OrderID INT PRIMARY KEY,
            CustomerID INT,
            OrderDate DATE,
            TotalAmount DECIMAL(10, 2),
            FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID)
        );
        ''')
        conn.commit()
        print("Order table created successfully.")

        # Insert sample data for Orders
        for i in range(1, 201):  # 200 orders for 2 years
            # Fetch an existing CustomerID from the Customer table
            cursor.execute('SELECT TOP 1 CustomerID FROM Customer ORDER BY NEWID()')
            customer_id = cursor.fetchone()[0]

            order_date = random_date(datetime(2022, 6, 1), datetime(2024, 6, 1))
            total_amount = random.uniform(50, 500)  # Generate a random total amount for the order

            cursor.execute('''
            INSERT INTO [Order] (OrderID, CustomerID, OrderDate, TotalAmount)
            VALUES (?, ?, ?, ?)
            ''', (i, customer_id, order_date, total_amount))
            conn.commit()
        print("Sample data inserted into Order table.")

    except Exception as e:
        conn.rollback()
        print(f"Error creating Order table: {str(e)}")
    finally:
        cursor.close()

def create_orderitem_table(conn):
    cursor = conn.cursor()
    try:
        cursor.execute('''
        CREATE TABLE OrderItem (
            OrderItemID INT PRIMARY KEY,
            OrderID INT,
            VariantID INT,
            Quantity INT,
            Price DECIMAL(10, 2),
            FOREIGN KEY (OrderID) REFERENCES [Order](OrderID),
            FOREIGN KEY (VariantID) REFERENCES Variant(VariantID)
        );
        ''')
        conn.commit()
        print("OrderItem table created successfully.")

        # Fetch all VariantIDs from Variant table
        cursor.execute('SELECT VariantID FROM Variant')
        variant_ids = [row[0] for row in cursor.fetchall()]

        # Insert sample data for OrderItems
        cursor.execute('SELECT OrderID, TotalAmount FROM [Order]')
        orders = cursor.fetchall()

        order_item_id_counter = 1
        for order in orders:
            order_id = order[0]
            total_amount = Decimal(order[1])

            remaining_amount = total_amount
            while remaining_amount > 0:
                variant_id = random.choice(variant_ids)
                quantity = random.randint(1, 3)
                price = Decimal(random.uniform(10, 100)).quantize(Decimal('0.01'))
                item_total = quantity * price

                # Ensure the last item adjusts to match the remaining amount
                if item_total > remaining_amount:
                    item_total = remaining_amount
                    price = (item_total / quantity).quantize(Decimal('0.01'))
                    remaining_amount = Decimal('0')
                else:
                    remaining_amount -= item_total

                cursor.execute('''
                INSERT INTO OrderItem (OrderItemID, OrderID, VariantID, Quantity, Price)
                VALUES (?, ?, ?, ?, ?)
                ''', (order_item_id_counter, order_id, variant_id, quantity, price))
                conn.commit()
                order_item_id_counter += 1

        print("Sample data inserted into OrderItem table.")

    except Exception as e:
        conn.rollback()
        print(f"Error creating OrderItem table: {str(e)}")
    finally:
        cursor.close()



# Function to create Sales table as a fact table in a star schema
def create_sales_table(conn):
    cursor = conn.cursor()
    try:
        cursor.execute('''
        CREATE TABLE Sales (
            SaleID INT PRIMARY KEY,
            OrderID INT,
            CustomerID INT,
            ProductID INT,
            VariantID INT,
            PriceID INT,
            Quantity INT,
            SaleDate DATE,
            FOREIGN KEY (OrderID) REFERENCES [Order](OrderID),
            FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
            FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
            FOREIGN KEY (VariantID) REFERENCES Variant(VariantID),
            FOREIGN KEY (PriceID) REFERENCES PriceHistory(PriceID)
        );
        ''')
        conn.commit()
        print("Sales table created successfully.")

        # Insert sample data for Sales
        cursor.execute('SELECT OrderID, CustomerID FROM [Order]')
        orders = cursor.fetchall()

        sale_id_counter = 1  # Initialize sale ID counter

        for order in orders:
            order_id = order[0]
            customer_id = order[1]
            cursor.execute('''
            SELECT OrderItem.VariantID FROM OrderItem
            WHERE OrderID = ?
            ''', (order_id,))
            items = cursor.fetchall()

            for item in items:
                variant_id = item[0]
                
                # Fetch ProductID from Variant table
                cursor.execute('''
                SELECT ProductID FROM Variant
                WHERE VariantID = ?
                ''', (variant_id,))
                product_id = cursor.fetchone()[0]

                # Fetch PriceID from PriceHistory table
                cursor.execute('''
                SELECT PriceID FROM PriceHistory
                WHERE VariantID = ? AND StartDate <= (SELECT [Order].OrderDate FROM [Order] WHERE [Order].OrderID = ?)
                ORDER BY StartDate DESC
                ''', (variant_id, order_id))
                price_id = cursor.fetchone()[0]

                cursor.execute('''
                INSERT INTO Sales (SaleID, OrderID, CustomerID, ProductID, VariantID, PriceID, Quantity, SaleDate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (sale_id_counter, order_id, customer_id, product_id, variant_id, price_id,
                      random.randint(1, 3), random_date(datetime(2022, 6, 1), datetime(2024, 6, 1))))
                sale_id_counter += 1  # Increment sale ID counter
                conn.commit()
        print("Sample data inserted into Sales table.")

    except Exception as e:
        conn.rollback()
        print(f"Error creating Sales table: {str(e)}")
    finally:
        cursor.close()

# Function to generate a random date between two dates
def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

# Main function to create database and tables
def create_database():
    conn = connect_to_database(server, database, username)
    
    # Drop tables if they exist
    drop_tables(conn)
    
    # Create tables
    create_customer_table(conn)
    create_product_table(conn)
    create_variant_table(conn)
    create_pricehistory_table(conn)
    create_order_table(conn)
    create_orderitem_table(conn)
    create_sales_table(conn)

    # Close connection
    conn.close()

# Execute the script
if __name__ == "__main__":
    create_database()

