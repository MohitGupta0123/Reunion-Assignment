import json
import requests
import pyodbc

# Step 1: Load JSON data from file
file_path = 'json.txt'  # Update with your actual file path
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
print(data)
# Initialize lists to store normalized data
orchestras = []
concerts = []
works = []
artists = []

# Extract and transform data
for orchestra in data['orchestras']:
    orchestras.append((
        orchestra['orchestra_id'],
        orchestra['name'],
        orchestra['city'],
        orchestra['country']
    ))

for concert in data['concerts']:
    concerts.append((
        concert['concert_id'],
        concert['orchestra_id'],
        concert['date'],
        concert['location']
    ))

for work in data['works']:
    works.append((
        work['work_id'],
        work['title'],
        work['composer'],
        work['year']
    ))

for artist in data['artists']:
    artists.append((
        artist['artist_id'],
        artist['name'],
        artist['birth_year'],
        artist['death_year'] if 'death_year' in artist else None
    ))

# Step 2: Connect to SQL Server using pyodbc
server = 'MOHIT-LAPTOP\\SQLEXPRESS'  # Double backslashes for escaping in Python strings
database = 'Ecomerce_Sales'  # Use the existing database name
username = 'MOHIT-LAPTOP\\mgmoh'  # Assuming Windows Authentication (Trusted Connection)
conn_str = pyodbc.connect(f'DRIVER={{SQL Server Native Client 11.0}};SERVER={server};DATABASE={database};UID={username};Trusted_connection=yes')
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Step 3: Create tables if they do not exist
cursor.execute('''
    IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Orchestras')
    CREATE TABLE Orchestras (
        orchestra_id INT PRIMARY KEY,
        name NVARCHAR(255),
        city NVARCHAR(255),
        country NVARCHAR(255)
    )
''')

cursor.execute('''
    IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Concerts')
    CREATE TABLE Concerts (
        concert_id INT PRIMARY KEY,
        orchestra_id INT,
        date DATE,
        location NVARCHAR(255),
        FOREIGN KEY (orchestra_id) REFERENCES Orchestras (orchestra_id)
    )
''')

cursor.execute('''
    IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Works')
    CREATE TABLE Works (
        work_id INT PRIMARY KEY,
        title NVARCHAR(255),
        composer NVARCHAR(255),
        year INT
    )
''')

cursor.execute('''
    IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = 'Artists')
    CREATE TABLE Artists (
        artist_id INT PRIMARY KEY,
        name NVARCHAR(255),
        birth_year INT,
        death_year INT
    )
''')

# Step 4: Insert data into tables
cursor.executemany('''
    INSERT INTO Orchestras (orchestra_id, name, city, country)
    VALUES (?, ?, ?, ?)
''', orchestras)

cursor.executemany('''
    INSERT INTO Concerts (concert_id, orchestra_id, date, location)
    VALUES (?, ?, ?, ?)
''', concerts)

cursor.executemany('''
    INSERT INTO Works (work_id, title, composer, year)
    VALUES (?, ?, ?, ?)
''', works)

cursor.executemany('''
    INSERT INTO Artists (artist_id, name, birth_year, death_year)
    VALUES (?, ?, ?, ?)
''', artists)

# Step 5: Commit changes and close connection
conn.commit()
conn.close()

print("Data successfully loaded into SQL Server database.")
