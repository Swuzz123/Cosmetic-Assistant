import sys
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load .env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env'))
load_dotenv(env_path)

# Connect to default 'postgres' database to list others
# Using standard postgres credentials
DB_URL = f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:5432/postgres"

print(f"Connecting to: {DB_URL}")

try:
    engine = create_engine(DB_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT datname FROM pg_database WHERE datistemplate = false;"))
        print("\nAvailable Databases:")
        for row in result:
            print(f"- {row[0]}")
except Exception as e:
    print(f"Error: {e}")
