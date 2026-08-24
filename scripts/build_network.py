"""
Build a 2-level network for demo purposes.
Loads several developers AND their followers so 2nd-degree queries return results.

Usage: python scripts/build_network.py
"""

import sys
import os
import time
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
os.chdir(os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv()

from database import db
from github_loader import GitHubLoader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Developers to seed (popular devs whose followers likely overlap)
SEED_USERS = [
    "torvalds",       # Linux creator
    "gaearon",        # React core team
    "tj",             # Node.js ecosystem
    "sindresorhus",   # npm packages
    "mrdoob",         # Three.js creator
]


def build_network():
    if not db.connect():
        logger.error("Failed to connect to database")
        return False

    loader = GitHubLoader()
    loader.create_indexes()

    # Level 1: Load main developers (this fetches their followers too)
    logger.info("=== Level 1: Loading main developers ===")
    for username in SEED_USERS:
        logger.info(f"Loading {username}...")
        loader.load_user(username)
        time.sleep(2)  # Respect rate limits

    # Level 2: Load some of their followers to create 2-hop paths
    logger.info("")
    logger.info("=== Level 2: Loading select followers for 2nd-degree paths ===")

    for username in SEED_USERS[:3]:  # Top 3 developers
        # Get their followers from DB
        followers = db.query("""
            MATCH (f:Developer)-[:FOLLOWS]->(d:Developer {username: $username})
            RETURN f.username AS username
            LIMIT 10
        """, username=username)

        if followers:
            # Load the top 5 followers of each developer
            for f in followers[:5]:
                f_name = f['username']
                logger.info(f"  Loading follower: {f_name} (for 2nd-degree from {username})...")
                loader.load_user(f_name)
                time.sleep(2)  # Respect rate limits

    logger.info("")
    logger.info("=== Network build complete! ===")
    logger.info("")
    logger.info("Try these queries:")
    logger.info("  2nd-degree:  GET /api/second-degree/torvalds?limit=5")
    logger.info("  Followers:   GET /api/followers/torvalds?limit=5")
    logger.info("  Lang network: GET /api/language-network/torvalds?limit=5")
    logger.info("  Stats:       GET /api/network-stats/torvalds")

    db.close()
    return True


if __name__ == "__main__":
    build_network()
