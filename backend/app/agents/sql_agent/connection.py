from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from app.core.config import settings

# Create Synchronous Engine for Agent Tools
# pool_pre_ping=True helps verify connections before using them, preventing stale connection errors
engine = create_engine(settings.SYNC_DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_sync_db_context():
    """
    Context manager for synchronous database sessions.
    Usage:
        with get_sync_db_context() as item_session:
             result = item_session.execute(text("SELECT * FROM ..."))
    """
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def execute_read_only_query(query: str, params: dict = None):
    """
    Executes a raw SQL query and returns the results as a list of dictionaries.
    Enforces READ-ONLY safety by checking for forbidden keywords.
    """
    # Basic Safety Check (SQL Injection is still possible if params aren't used, 
    # but the Agent is the one generating SQL, not the user directly. 
    # We still want to prevent the Agent from hallucinating DROP TABLE commands.)
    normalized_query = query.strip().lower()
    forbidden_keywords = ['insert', 'update', 'delete', 'drop', 'alter', 'truncate', 'create', 'grant', 'revoke']
    
    if any(keyword in normalized_query.split() for keyword in forbidden_keywords):
         return {"error": "Safety Alert: Only SELECT statements are allowed."}

    with get_sync_db_context() as session:
        try:
            result = session.execute(text(query), params or {})
            # Convert keys to strings and rows to dicts
            keys = result.keys()
            return [dict(zip(keys, row)) for row in result.fetchall()]
        except Exception as e:
            return {"error": f"Database Error: {str(e)}"}
