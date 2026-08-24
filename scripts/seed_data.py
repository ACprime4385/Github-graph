"""
Seed Data Script
Loads initial developer data into the graph database.
Usage: python scripts/seed_data.py <username1> [username2] [username3] ...

This script is optional for MVP. The app dynamically loads users
on first search via the API.
"""

import sys
import os
import logging

# Add src to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import db
from github_loader import GitHubLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_data(usernames):
    """Load a list of GitHub users into the database"""
    if not db.connect():
        logger.error("Failed to connect to database")
        return False

    loader = GitHubLoader()
    loader.create_indexes()

    success = 0
    failed = 0

    for username in usernames:
        logger.info(f"Loading {username}...")
        if loader.load_user(username):
            success += 1
        else:
            failed += 1

    logger.info(f"Seeding complete: {success} loaded, {failed} failed")
    db.close()
    return failed == 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/seed_data.py <username1> [username2] ...")
        print("Example: python scripts/seed_data.py torvalds gaearon tj")
        sys.exit(1)

    usernames = sys.argv[1:]
    success = seed_data(usernames)
    sys.exit(0 if success else 1)
