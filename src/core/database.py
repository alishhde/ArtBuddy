import sqlite3
import logging
from datetime import datetime
from src.core.logging_config import setup_logging

# Get logger for this module
logger = logging.getLogger(__name__)

class DatabaseCore:
    def __init__(self, verbose: bool, 
                       database_type: str, 
                       database_path: str):
        self.db = None
        
        self.verbose = verbose
        setup_logging(verbose=verbose)
        
        self.database_type = database_type
        self.database_path = database_path

        self.db = self.connect()
        if self.db is None:
            logger.error("Error connecting to the database")
            raise Exception("Error connecting to the database")


    def connect(self):
        """Connect to the database

        Returns:
            sqlite3.Connection: The connection to the database
        """
        try:
            if self.database_type == "sqlite":
                db = sqlite3.connect(self.database_path)
            logger.info(f"Connected to {self.database_type} database")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            return False
        return db


    def conversation_retriever(self, data_table: str="conversations", date: str=None, exclude_image: bool=False, exclude_text: bool=False, role: str=None):
        """Return the data from the database in chronological order (oldest to newest)

        Args:
            data_table (str): The table of the data to retrieve
            date (str): Retrieve all data since the date
            exclude_image (bool): Whether to exclude image data from the results
            exclude_text (bool): Whether to exclude text data from the results
            role (str): Filter by specific role ('user', 'system', 'agent')

        Returns:
            list: List of lists containing [role, text, image] for each entry, ordered from oldest to newest
                  If exclude_text or exclude_image is True, the corresponding element will be None
                  If data is missing in the database, the corresponding element will be None
        """
        try:
            cursor = self.db.cursor()
            
            if data_table is None:
                logger.error("No data table provided")
                return False

            # Validate role if provided
            if role is not None and role not in ['user', 'system', 'agent']:
                logger.error(f"Invalid role: {role}. Must be 'user', 'system', or 'agent'")
                return False

            # Build the query based on parameters
            columns = ["role"]  # Always include role
            if not exclude_text:
                columns.append("text")
            if not exclude_image:
                columns.append("image")
            
            columns_str = ", ".join(columns)
            
            # Build WHERE clause
            where_clauses = []
            params = []
            
            if date is not None:
                where_clauses.append("date >= ?")
                params.append(date)
            
            if role is not None:
                where_clauses.append("role = ?")
                params.append(role)
            
            where_str = " AND ".join(where_clauses) if where_clauses else ""
            query = f"SELECT {columns_str} FROM {data_table}"
            if where_str:
                query += f" WHERE {where_str}"
            query += " ORDER BY date ASC"

            cursor.execute(query, tuple(params))

            # Fetch all results
            results = cursor.fetchall()
            
            # Convert to list of lists format with None for excluded columns
            formatted_results = []
            for row in results:
                entry = [row[0]]  # role is always first
                if not exclude_text:
                    # Handle case where text might be NULL in database
                    text = row[1] if row[1] is not None else None
                    entry.append(text)
                if not exclude_image:
                    # Handle case where image might be NULL in database
                    image_idx = 2 if not exclude_text else 1
                    image = row[image_idx] if row[image_idx] is not None else None
                    entry.append(image)
                formatted_results.append(entry)
                
                # Log if any data is missing
                if not exclude_text and not exclude_image:
                    if row[1] is None and row[2] is None:
                        logger.warning(f"Found row with both text and image missing for role {row[0]}")
                    elif row[1] is None:
                        logger.warning(f"Found row with text missing for role {row[0]}")
                    elif row[2] is None:
                        logger.warning(f"Found row with image missing for role {row[0]}")
            
            return formatted_results

        except sqlite3.Error as e:
            logger.error(f"Error retrieving data: {e}")
            return False


    def conversation_saver(self, data: dict, data_table: str="conversations"):
        """Save the data to the database

        Args:
            data (dict): The data to save, which can contain text, base64 encoded image, or both
            data_table (str): The table of the data to save
        """
        # Get the current date
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            cursor = self.db.cursor()
            
            # Create table if it doesn't exist with our columns
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {data_table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    role TEXT NOT NULL,
                    text TEXT,
                    image TEXT
                )
            """)
            
            # Extract data from the dictionary
            text_data = data.get('text', None)
            image_data = data.get('image', None)
            role = data.get('role', 'user')  # Default to 'user' if not specified
            
            # Validate role
            if role not in ['user', 'system', 'agent']:
                logger.error(f"Invalid role: {role}. Must be 'user', 'system', or 'agent'")
                return False
            
            # Build the query based on available data
            if text_data is not None and image_data is not None:
                cursor.execute(
                    f"INSERT INTO {data_table} (date, role, text, image) VALUES (?, ?, ?, ?)",
                    (date, role, str(text_data), image_data)
                )
            elif text_data is not None:
                cursor.execute(
                    f"INSERT INTO {data_table} (date, role, text) VALUES (?, ?, ?)",
                    (date, role, str(text_data))
                )
            elif image_data is not None:
                cursor.execute(
                    f"INSERT INTO {data_table} (date, role, image) VALUES (?, ?, ?)",
                    (date, role, image_data)
                )
            else:
                logger.error("No data provided to save")
                return False
                
            self.db.commit()
            logger.info(f"Data saved to {data_table} table")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error saving data: {e}")
            raise e


    def idea_retriever(self, date: str=None, data_table: str="ideas", since_date: bool=False, at_date: bool=False):
        """Retrieve ideas from the database

        Args:
            date (str): The date to retrieve ideas from
            data_table (str): The table of the data to retrieve
            since_date (bool): Whether to retrieve ideas since the date
            at_date (bool): Whether to retrieve ideas at the date

        Returns:
            list: List of tuples containing (id, date, idea) for each entry
        """
        try:
            cursor = self.db.cursor()
            
            # Build the query based on parameters
            query = f"SELECT id, date, idea FROM {data_table}"
            params = []
            
            if date is not None:
                if since_date:
                    query += " WHERE date >= ?"
                    params.append(date)
                elif at_date:
                    query += " WHERE date LIKE ?"
                    params.append(f"{date}%")  # Match any time on that date
                else:
                    query += " WHERE date = ?"
                    params.append(date)
            
            query += " ORDER BY date DESC"  # Most recent first
            
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()
            
            # Convert results to list of tuples
            ideas = []
            for row in results:
                # Split the idea text back into a list if it contains newlines
                idea_text = row[2]
                if "\n" in idea_text:
                    ideas_list = idea_text.split("\n")
                else:
                    ideas_list = [idea_text]
                
                ideas.append({
                    'id': row[0],
                    'date': row[1],
                    'ideas': ideas_list
                })
            
            return ideas

        except sqlite3.Error as e:
            logger.error(f"Error retrieving ideas: {e}")
            return []


    def idea_saver(self, data: list, data_table: str="ideas"):
        """Save an idea to the database

        Args:
            data (list): List of prompts or texts that are ideas
            data_table (str): The table of the data to save

        Returns:
            bool: True if successful, False otherwise
        """
        # Get the current date
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            cursor = self.db.cursor()
            
            # Create table if it doesn't exist
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {data_table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    idea TEXT NOT NULL
                )
            """)
            
            # Convert list of ideas to a single string if needed
            if isinstance(data, list):
                idea_text = "\n".join(str(item) for item in data)
            else:
                idea_text = str(data)
            
            # Save the idea to the database
            cursor.execute(
                f"INSERT INTO {data_table} (date, idea) VALUES (?, ?)",
                (date, idea_text)
            )
            self.db.commit()
            logger.info(f"Idea saved to {data_table} table")
            return True
        except sqlite3.Error as e:
            logger.error(f"Error saving idea: {e}")
            return False
