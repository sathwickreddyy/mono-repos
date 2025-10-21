import psycopg2
from pymongo import MongoClient
import os
from urllib.parse import quote_plus
from contextlib import contextmanager
from typing import Optional, Tuple

# Global configuration variables
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME", "sathwick")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "Sathwick@18")
MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
MONGODB_PORT = os.getenv("MONGODB_PORT", "27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "test_db")

POSTGRESQL_USERNAME = os.getenv("POSTGRESQL_USERNAME", "sathwick")
POSTGRESQL_PASSWORD = os.getenv("POSTGRESQL_PASSWORD", "Sathwick@18")
POSTGRESQL_HOST = os.getenv("POSTGRESQL_HOST", "localhost")
POSTGRESQL_DATABASE = os.getenv("POSTGRESQL_DATABASE", "mydatabase")


class DatabaseManager:
    """Manages database connections for MongoDB and PostgreSQL."""

    def __init__(self):
        self._mongo_client = None
        self._postgres_connection = None

    def get_mongodb_connection_string(self) -> str:
        """Generate MongoDB connection string with properly encoded credentials."""
        encoded_username = quote_plus(MONGODB_USERNAME)
        encoded_password = quote_plus(MONGODB_PASSWORD)
        return f"mongodb://{encoded_username}:{encoded_password}@{MONGODB_HOST}:{MONGODB_PORT}/"

    def get_postgresql_connection_string(self) -> str:
        """Generate PostgreSQL connection string."""
        return f"dbname={POSTGRESQL_DATABASE} user={POSTGRESQL_USERNAME} password={POSTGRESQL_PASSWORD} host={POSTGRESQL_HOST}"

    def get_mongo_client(self) -> Optional[MongoClient]:
        """Get or create MongoDB client. Returns None if connection fails."""
        if self._mongo_client is None:
            try:
                connection_string = self.get_mongodb_connection_string()
                self._mongo_client = MongoClient(connection_string)
                # Test the connection
                self._mongo_client.admin.command("ping")
            except Exception as e:
                print(f"MongoDB connection failed: {e}")
                return None
        return self._mongo_client

    def get_postgres_connection(self) -> Optional[psycopg2.extensions.connection]:
        """Get or create PostgreSQL connection. Returns None if connection fails."""
        if self._postgres_connection is None or self._postgres_connection.closed:
            try:
                connection_string = self.get_postgresql_connection_string()
                self._postgres_connection = psycopg2.connect(connection_string)
            except Exception as e:
                print(f"PostgreSQL connection failed: {e}")
                return None
        return self._postgres_connection

    @contextmanager
    def mongo_database(self, database_name: str = None):
        """Context manager for MongoDB database operations."""
        client = self.get_mongo_client()
        if client is None:
            raise Exception("Failed to connect to MongoDB")

        db_name = database_name or MONGODB_DATABASE
        db = client[db_name]
        try:
            yield db
        finally:
            # MongoDB client handles connection pooling, no need to close here
            pass

    @contextmanager
    def postgres_cursor(self):
        """Context manager for PostgreSQL cursor operations."""
        conn = self.get_postgres_connection()
        if conn is None:
            raise Exception("Failed to connect to PostgreSQL")

        cur = conn.cursor()
        try:
            yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cur.close()

    def close_connections(self):
        """Close all database connections."""
        if self._mongo_client:
            self._mongo_client.close()
            self._mongo_client = None

        if self._postgres_connection and not self._postgres_connection.closed:
            self._postgres_connection.close()
            self._postgres_connection = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatically close connections."""
        self.close_connections()


def test_mongodb_connection(db_manager: DatabaseManager) -> bool:
    """Test MongoDB connection and list collections."""
    try:
        with db_manager.mongo_database() as db:
            collections = db.list_collection_names()
            print(f"MongoDB collections: {collections}")
            return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return False


def test_postgresql_connection(db_manager: DatabaseManager) -> bool:
    """Test PostgreSQL connection and version."""
    try:
        with db_manager.postgres_cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()
            print(
                f"PostgreSQL version: {version[0][:50]}..."
            )  # Truncate for readability
            return True
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")
        return False


def main():
    """Test all database connections using the DatabaseManager."""
    print("Testing database connections...")

    # Using context manager for automatic connection cleanup
    with DatabaseManager() as db_manager:
        mongodb_status = test_mongodb_connection(db_manager)
        postgresql_status = test_postgresql_connection(db_manager)

        print(f"\nConnection status:")
        print(f"MongoDB: {'✓' if mongodb_status else '✗'}")
        print(f"PostgreSQL: {'✓' if postgresql_status else '✗'}")

        # Demonstrate reusable connections
        if mongodb_status:
            print(
                f"\nMongoDB connection string: {db_manager.get_mongodb_connection_string()}"
            )
        if postgresql_status:
            print(
                f"PostgreSQL connection string: {db_manager.get_postgresql_connection_string()}"
            )


# Example usage in another class
class DataService:
    """Example service class that uses the DatabaseManager."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def get_user_data_from_mongo(self, user_id: str):
        """Example method using MongoDB."""
        try:
            with self.db_manager.mongo_database() as db:
                users_collection = db.users
                return users_collection.find_one({"_id": user_id})
        except Exception as e:
            print(f"Error fetching user data: {e}")
            return None

    def get_user_data_from_postgres(self, user_id: int):
        """Example method using PostgreSQL."""
        try:
            with self.db_manager.postgres_cursor() as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                return cur.fetchone()
        except Exception as e:
            print(f"Error fetching user data: {e}")
            return None


if __name__ == "__main__":
    main()
