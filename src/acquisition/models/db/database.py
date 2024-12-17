from peewee import SqliteDatabase

# Default to a placeholder database
db = SqliteDatabase(None)  # Uninitialized database

def initialize_db(db_name=None):
    """Initialize the database connection conditionally."""
    global db
    if db_name:
        db.init(f'src/acquisition/models/db/{db_name}')
    else:
        db.init(':memory:')  # Default to in-memory DB if not specified
    db.connect()
    print(f"Database initialized: {db_name or 'in-memory'}")
