import os
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.driver = None

    def connect(self):
        """Initialize database connection with error handling"""
        try:
            uri = os.getenv("NEO4J_URI")
            user = os.getenv("NEO4J_USER")
            password = os.getenv("NEO4J_PASSWORD")

            if not all([uri, user, password]):
                raise ValueError("Missing database credentials")

            # bolt+s and neo4j+s URIs already handle encryption
            # Don't pass encrypted parameter for +s or +ssc schemes
            driver_kwargs = {
                'auth': (user, password)
            }
            if '+s' not in uri and '+ssc' not in uri:
                driver_kwargs['encrypted'] = True

            self.driver = GraphDatabase.driver(uri, **driver_kwargs)

            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")

            logger.info("Connected to CognoDB")
            return True

        except AuthError as e:
            logger.error(f"Auth error: {e}")
            return False
        except ServiceUnavailable as e:
            logger.error(f"Service unavailable: {e}")
            return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

    def close(self):
        """Close database driver"""
        if self.driver:
            self.driver.close()

    def query(self, cypher, **parameters):
        """
        Execute read query
        Args:
            cypher: Cypher query string with $parameters
            **parameters: Query parameters (safe from injection)
        Returns:
            List of result dictionaries
        """
        if not self.driver:
            raise RuntimeError("Database not connected")

        try:
            with self.driver.session() as session:
                result = session.run(cypher, **parameters)
                return result.data()
        except ServiceUnavailable:
            logger.error("Database unavailable during query")
            return None
        except Exception as e:
            logger.error(f"Query error: {e}")
            return None

    def execute(self, cypher, **parameters):
        """
        Execute write query
        Args:
            cypher: Cypher query string
            **parameters: Query parameters
        Returns:
            Query result summary
        """
        if not self.driver:
            raise RuntimeError("Database not connected")

        try:
            with self.driver.session() as session:
                result = session.run(cypher, **parameters)
                return result.consume()
        except ServiceUnavailable:
            logger.error("Database unavailable during execute")
            return None
        except Exception as e:
            logger.error(f"Execute error: {e}")
            return None


# Singleton instance
db = Database()
