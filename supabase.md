Connect to your project
Get the connection strings and environment variables for your app

Connection String
App Frameworks
Mobile Frameworks
ORMs
Type

Python
Source

Primary database
1
Install the following
pip install python-dotenv psycopg2

2
Add file to project
main.py
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Connect to the database
try:
    connection = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )
    print("Connection successful!")
    
    # Create a cursor to execute SQL queries
    cursor = connection.cursor()
    
    # Example query
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print("Current Time:", result)

    # Close the cursor and connection
    cursor.close()
    connection.close()
    print("Connection closed.")

except Exception as e:
    print(f"Failed to connect: {e}")

3
Choose type of connection
Direct connection
Ideal for applications with persistent, long-lived connections, such as those running on virtual machines or long-standing containers.

.env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.csqozoduvzvmdortjosh.supabase.co:5432/postgres


View parameters
Suitable for long-lived, persistent connections
Each client has a dedicated connection to Postgres
Not IPv4 compatible
Use Session Pooler if on a IPv4 network or purchase IPv4 add-on
IPv4 add-on

Some platforms are IPv4-only:
Transaction pooler
Supavisor
Ideal for stateless applications like serverless functions where each interaction with Postgres is brief and isolated.

.env
user=postgres.csqozoduvzvmdortjosh 
password=[YOUR-PASSWORD] 
host=aws-0-eu-central-1.pooler.supabase.com
port=6543
dbname=postgres

Does not support PREPARE statements


View parameters
Suitable for a large number of connected clients
Pre-warmed connection pool to Postgres
IPv4 compatible
Transaction pooler connections are IPv4 proxied for free.
Session pooler
Supavisor
Only recommended as an alternative to Direct Connection, when connecting via an IPv4 network.

.env
user=postgres.csqozoduvzvmdortjosh 
password=[YOUR-PASSWORD] 
host=aws-0-eu-central-1.pooler.supabase.com
port=5432
dbname=postgres


View parameters
IPv4 compatible
Session pooler connections are IPv4 proxied for free
Only use on a IPv4 network
Use Direct Connection if connecting via an IPv6 network

Connecting to SQL Alchemy