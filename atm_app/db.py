import os
import mysql.connector
from mysql.connector import pooling, Error
from dotenv import load_dotenv

# Load environment variables from current directory or relative path
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "atm_db")

# Global pool reference
db_pool = None

def init_pool():
    """Initializes the MySQL connection pool on demand."""
    global db_pool
    if db_pool is None:
        try:
            db_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="atm_pool",
                pool_size=10,
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
        except Error as e:
            if e.errno == 1049:  # Unknown database
                raise RuntimeError(
                    f"Database '{DB_NAME}' does not exist. Please create it and run schema.sql first."
                )
            else:
                raise RuntimeError(
                    f"Failed to connect to MySQL server at {DB_HOST}:{DB_PORT} (User: {DB_USER}). Error: {e}"
                )

def get_db_connection():
    """Gets a connection from the pool, initializing the pool if needed."""
    init_pool()
    return db_pool.get_connection()

def execute_query(query, params=None):
    """Executes a single write query (INSERT, UPDATE, DELETE)."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.rowcount
    except Error as e:
        raise RuntimeError(f"Database query execution failed: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def fetch_one(query, params=None, dictionary=True):
    """Fetches a single row matching the query."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=dictionary)
        cursor.execute(query, params or ())
        return cursor.fetchone()
    except Error as e:
        raise RuntimeError(f"Database fetch_one failed: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def fetch_all(query, params=None, dictionary=True):
    """Fetches all rows matching the query."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=dictionary)
        cursor.execute(query, params or ())
        return cursor.fetchall()
    except Error as e:
        raise RuntimeError(f"Database fetch_all failed: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def execute_transaction(queries_with_params):
    """
    Executes a list of queries sequentially within a single transaction.
    Rolls back automatically on any failure.
    queries_with_params: list of tuples like (query_string, parameters_tuple)
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        conn.start_transaction()
        cursor = conn.cursor()
        for query, params in queries_with_params:
            cursor.execute(query, params or ())
        conn.commit()
        return True
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except Error:
                pass
        raise RuntimeError(f"Transaction failed and was rolled back: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
