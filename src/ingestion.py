import pandas as pd
import os
import glob
import logging
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from dotenv import load_dotenv

# 1. FIX ENCODING: Tell logging to ignore characters it can't handle
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

class TfLProfessionalIngestor:
    def __init__(self):
        load_dotenv()
        self.engine = self._get_connection()
        self.header_keywords = ['nlc', 'station', 'day', 'financial year']

    def _get_connection(self):
        """Builds a professional URL object to avoid 'None' and '@' parsing errors."""
        try:
            # PROFESSIONAL DEBUG: Let's see what is being loaded
            user = os.getenv('DB_USER')
            host = os.getenv('DB_HOST')
            port = os.getenv('DB_PORT', '5432')
            db_name = os.getenv('DB_NAME')
            password = os.getenv('DB_PASSWORD')

            print(f"DEBUG: Connecting to {host}:{port} as user {user}...")

            # Use the URL builder to handle special characters in passwords safely
            connection_url = URL.create(
                drivername="postgresql+psycopg2",
                username=user,
                password=password,
                host=host,
                port=int(port),
                database=db_name
            )
            return create_engine(connection_url)
        except Exception as e:
            logging.error(f"CRITICAL: Failed to build connection URL. Error: {e}")
            raise

    def _clean_column_names(self, df):
        df.columns = [
            str(c).strip().lower().replace(" ", "_").replace("/", "_").replace("+", "plus")
            for c in df.columns
        ]
        return df

    def _find_header_row(self, file_path):
        """Scans file for keywords to find the data start point."""
        try:
            preview = pd.read_csv(file_path, nrows=10, header=None)
            for i, row in preview.iterrows():
                if any(key in str(cell).lower() for cell in row for key in self.header_keywords):
                    return i
            return 0
        except:
            return 0

    def process_directory(self, pattern="data_raw/*.csv"):
        files = glob.glob(pattern)
        if not files:
            logging.warning(f"No files found in: {pattern}")
            return

        for file_path in files:
            file_name = os.path.basename(file_path)
            # Create table name: remove extension and replace dashes
            clean_name = file_name.replace(".csv", "").replace(" ", "_").replace("-", "_").lower()
            
            # Professional renaming: tables shouldn't start with numbers
            table_name = f"usage_{clean_name}" if clean_name[0].isdigit() else f"tfl_{clean_name}"
            
            self.ingest_file(file_path, table_name)

    def ingest_file(self, file_path, table_name):
        try:
            skip = self._find_header_row(file_path)
            logging.info(f"START: Ingesting {file_path} (Table: {table_name})")
            
            df = pd.read_csv(file_path, skiprows=skip)
            df = self._clean_column_names(df)
            df = df.dropna(axis=1, how='all')

            df.to_sql(table_name, self.engine, if_exists='replace', index=False)
            logging.info(f"SUCCESS: {table_name} loaded.")
            
        except Exception as e:
            logging.error(f"ERROR on {table_name}: {e}")

if __name__ == "__main__":
    ingestor = TfLProfessionalIngestor()
    # Point exactly to your folder
    ingestor.process_directory("data_raw/*.csv")
    logging.info("DONE: All files processed.")