import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# -------- DATABASE CONFIG --------
DB_USER = "root"
DB_PASS = quote_plus("oppoa12@bharath")   # encode @
DB_HOST = "localhost"
DB_NAME = "NutritionDB"

# SQLAlchemy engine
engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}",
    pool_pre_ping=True
)

# -------- SIMPLE QUERY EXECUTOR --------
def run_query(query, params=None):
    """Execute INSERT/UPDATE/DELETE safely."""
    with engine.begin() as conn:
        conn.execute(text(query), params or {})

# -------- LOAD TABLE AS DATAFRAME --------
def load_data(table):
    """Load an entire table as a pandas DataFrame."""
    return pd.read_sql(text(f"SELECT * FROM {table}"), engine)

# -------- RUN SELECT QUERY --------
def fetch(query, params=None):
    """Fetch read-only SQL results as DataFrame."""
    return pd.read_sql(text(query), engine, params=params or {})
