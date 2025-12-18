import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load database credentials from .env file for security
load_dotenv()

class DataIngestor:
    """
    Handles the professional ingestion of TfL CSV files into PostgreSQL.
    Follows the 'As-Is' Multi-Table strategy.
    """
    
    def __init__(self):
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.host = os.getenv("DB_HOST")
        self.port = os.getenv("DB_PORT")
        self.db_name = os.getenv("DB_NAME")
        
        # Initialize SQLAlchemy connection
        self.engine = create_engine(
            f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
        )

    def load_usage_data(self, file_path: str, year: int):
        """
        Loads a specific year's station usage CSV into its own table.
        
        Args:
            file_path (str): The local path to the raw CSV.
            year (int): The year associated with the data.
        """
        try:
            print(f"--- Processing Usage Data for Year: {year} ---")
            
            # Professional Check: Historical CSVs often have 3-4 rows of junk above headers
            # Based on our audit, 2011.csv has 3 rows above the header
            df = pd.read_csv(file_path, skiprows=3)
            
            # Clean column names: Replace spaces with underscores and make lowercase
            df.columns = [c.strip().lower().replace(" ", "_").replace("+", "plus") for c in df.columns]
            
            # Load into PostgreSQL 'as-is'
            table_name = f"usage_{year}"
            df.to_sql(table_name, self.engine, if_exists='replace', index=False)
            
            print(f"SUCCESS: Table '{table_name}' created with {len(df)} rows.")
            
        except Exception as e:
            print(f"FAILURE: Could not load year {year}. Error: {e}")

if __name__ == "__main__":
    ingestor = DataIngestor()
    
    # Task for the Freshers: Loop through our 'Gold Mine' files
    usage_files = {
        2011: "data/raw/2011.csv",
        2012: "data/raw/2012.csv",
        2013: "data/raw/2013.csv"
    }
    
    for year, path in usage_files.items():
        if os.path.exists(path):
            ingestor.load_usage_data(path, year)
        else:
            print(f"WARNING: File not found at {path}")