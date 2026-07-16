import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def init_db():
    # Connect to default database as superuser (postgres) using port 5432
    # Since we are in trust mode, no password is required
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        host="127.0.0.1",
        port=5432
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    # Create role 'user' if it does not exist
    cursor.execute("SELECT 1 FROM pg_roles WHERE rolname='user';")
    if not cursor.fetchone():
        print("Creating user role...")
        cursor.execute("CREATE ROLE \"user\" WITH LOGIN PASSWORD 'pass';")
    else:
        print("User role already exists. Updating password...")
        cursor.execute("ALTER ROLE \"user\" WITH LOGIN PASSWORD 'pass';")

    # Give 'user' CREATEDB privilege so it can manage/create databases if needed
    cursor.execute("ALTER ROLE \"user\" CREATEDB;")

    # Create database 'cyberpath' if it does not exist
    cursor.execute("SELECT 1 FROM pg_database WHERE datname='cyberpath';")
    if not cursor.fetchone():
        print("Creating cyberpath database...")
        cursor.execute("CREATE DATABASE cyberpath OWNER \"user\";")
    else:
        print("cyberpath database already exists.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    init_db()
