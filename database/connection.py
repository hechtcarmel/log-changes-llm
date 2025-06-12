import pymysql
from pymysql import Error
from typing import Optional, Dict, Any
import logging
from campaign_analyzer.constants import DATABASE_CONFIG

class DatabaseConnection:
    """Handles MySQL database connections with runtime credentials."""
    
    def __init__(self):
        self.connection = None
        self.host = DATABASE_CONFIG["host"]
        self.port = DATABASE_CONFIG["port"]
        self.database = DATABASE_CONFIG["database"]
    
    def connect(self, username: str, password: str) -> bool:
        """
        Establish database connection with provided credentials.
        
        Args:
            username: MySQL username
            password: MySQL password
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=username,
                password=password,
                autocommit=True,
                connect_timeout=DATABASE_CONFIG["connect_timeout"],
                charset=DATABASE_CONFIG["charset"]
            )
            
            if self.connection.open:
                logging.info(f"Successfully connected to MySQL database: {self.database}")
                return True
            else:
                return False
                
        except Error as e:
            logging.error(f"Error connecting to MySQL database: {e}")
            return False
    
    def disconnect(self):
        """Close the database connection."""
        if self.connection and self.connection.open:
            self.connection.close()
            logging.info("MySQL database connection closed")
    
    def is_connected(self) -> bool:
        """Check if database connection is active."""
        return self.connection and self.connection.open
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> Optional[list]:
        """
        Execute a SELECT query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            List of dictionaries representing query results, or None if error
        """
        if not self.is_connected():
            logging.error("No active database connection")
            return None
            
        try:
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            cursor.close()
            return results
            
        except Error as e:
            logging.error(f"Error executing query: {e}")
            return None
    
    def test_connection(self, username: str, password: str) -> Dict[str, Any]:
        """
        Test database connection and return status information.
        
        Args:
            username: MySQL username
            password: MySQL password
            
        Returns:
            Dictionary with connection status and details
        """
        result = {
            "success": False,
            "message": "",
            "host": self.host,
            "port": self.port,
            "database": self.database
        }
        
        try:
            if self.connect(username, password):
                result["success"] = True
                result["message"] = "Connection successful"
                self.disconnect()
            else:
                result["message"] = "Connection failed - unknown error"
                
        except Error as e:
            result["message"] = f"Connection failed: {str(e)}"
            
        return result 