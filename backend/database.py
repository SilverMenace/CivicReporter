from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- MySQL Connection URL ---
# Format: "mysql+mysqlclient://<USER>:<PASSWORD>@<HOST>/<DB_NAME>"
# Replace 'your_password' with your actual MySQL root password.
# If you don't have a password for your local root user, leave it empty: "mysql+mysqlclient://root@127.0.0.1/civicreporter"

DB_USER = "root"
DB_PASSWORD = "password" # <-- IMPORTANT: CHANGE THIS
DB_HOST = "127.0.0.1"
DB_NAME = "civicreporter"

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()