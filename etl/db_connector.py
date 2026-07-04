import os
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session

# Default database is a local SQLite database in the root of the workspace
DEFAULT_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "decision_iq.db"))
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_DB_PATH}"

# Fetch database URL from environment variables, fallback to SQLite
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

WAREHOUSE_TABLES = [
    "customer_support",
    "shipments",
    "payments",
    "order_details",
    "orders",
    "inventory",
    "marketing_campaigns",
    "daily_business_metrics",
    "warehouses",
    "suppliers",
    "products",
    "customers",
    "employees",
    "regions",
]

def get_engine():
    """
    Creates and returns a SQLAlchemy Engine.
    For SQLite, we configure the connection to enforce foreign key constraints.
    """
    connect_args = {}
    if DATABASE_URL.startswith("sqlite"):
        connect_args["timeout"] = 30
        
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    
    # Enforce foreign keys in SQLite
    if DATABASE_URL.startswith("sqlite"):
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
            
        from sqlalchemy import event
        event.listen(engine, "connect", set_sqlite_pragma)
        
    return engine

def get_session():
    """
    Creates and returns a scoped SQLAlchemy Session.
    """
    engine = get_engine()
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    return Session()

def init_db(schema_path=None):
    """
    Initializes the database schema using the schema.sql file.
    """
    if schema_path is None:
        schema_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sql", "schema.sql"))
        
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at {schema_path}")
        
    print(f"Initializing database from schema: {schema_path}")
    print(f"Database Target: {DATABASE_URL}")
    
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    engine = get_engine()
    
    # SQLite does not support executing multiple statements via session.execute(text()) in some SQLAlchemy versions,
    # so we split the SQL script by semicolons or execute via raw connection if SQLite.
    if DATABASE_URL.startswith("sqlite"):
        # We can execute using sqlite3 directly or use SQLAlchemy raw connection
        with engine.connect() as conn:
            # SQLAlchemy connection.connection gives the DBAPI connection
            dbapi_conn = conn.connection
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=OFF")
            for table_name in WAREHOUSE_TABLES:
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            cursor.executescript(schema_sql)
            cursor.execute("PRAGMA foreign_keys=ON")
            dbapi_conn.commit()
            cursor.close()
    else:
        # Standard execution for PostgreSQL
        with engine.begin() as conn:
            for table_name in WAREHOUSE_TABLES:
                conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE'))
            # We can execute the raw SQL text directly
            # Splitting on semicolons handles simple PostgreSQL command executions
            for command in schema_sql.split(";"):
                clean_command = command.strip()
                if clean_command:
                    conn.execute(text(clean_command))
                    
    print("Database schema initialized successfully.")

if __name__ == "__main__":
    init_db()
