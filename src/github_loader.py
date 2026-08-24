import sys
import requests
import os

# Ensure src/ directory is on the path for sibling module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GitHubLoader:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.api_base = "https://api.github.com"

    def load_user(self, username):
        """
        Load developer and their relationships
        Args:
            username: GitHub username
        Returns:
            Boolean (success/failure)
        """
        try:
            # Fetch user info
            user_resp = self._fetch_with_retry(
                f"{self.api_base}/users/{username}"
            )

            if user_resp.status_code == 404:
                logger.warning(f"User not found: {username}")
                return False

            if user_resp.status_code != 200:
                logger.error(f"GitHub API error: {user_resp.status_code}")
                return False

            user = user_resp.json()

            # Create/update developer node
            db.execute("""
                MERGE (d:Developer {username: $username})
                SET d.name = $name,
                    d.followers = $followers,
                    d.public_repos = $repos,
                    d.profile_url = $url,
                    d.loaded_at = datetime()
            """,
                username=username,
                name=user.get("name", username),
                followers=user.get("followers", 0),
                repos=user.get("public_repos", 0),
                url=user.get("html_url"))

            # Fetch and load followers
            self._load_followers(username)

            # Fetch and load repositories + languages
            self._load_repositories(username)

            # Load followers' followers for 2nd-degree connections
            self._load_second_degree(username)

            logger.info(f"Loaded {username}")
            return True

        except requests.Timeout:
            logger.error(f"Timeout loading {username}")
            return False
        except Exception as e:
            logger.error(f"Error loading {username}: {e}")
            return False

    def _fetch_with_retry(self, url, max_retries=3):
        """Fetch URL with exponential backoff retry logic"""
        import time

        for attempt in range(max_retries):
            try:
                resp = requests.get(url, headers=self.headers, timeout=10)
                if resp.status_code == 429:  # Rate limited
                    time.sleep(2 ** attempt)
                    continue
                return resp
            except requests.Timeout:
                time.sleep(2 ** attempt)

        # Return last response even if failed
        return requests.get(url, headers=self.headers, timeout=10)

    def _load_followers(self, username):
        """Load followers (1-hop relationships)"""
        try:
            followers_resp = self._fetch_with_retry(
                f"{self.api_base}/users/{username}/followers"
                + "?per_page=30"
            )

            if followers_resp.status_code != 200:
                return

            followers = followers_resp.json()

            for follower in followers:
                db.execute("""
                    MERGE (f:Developer {username: $follower_name})
                    SET f.profile_url = $url
                    WITH f
                    MATCH (u:Developer {username: $target})
                    MERGE (f)-[:FOLLOWS]->(u)
                """,
                    follower_name=follower["login"],
                    url=follower["html_url"],
                    target=username)

            logger.info(f"Loaded {len(followers)} followers for {username}")

        except Exception as e:
            logger.error(f"Error loading followers: {e}")

    def _load_repositories(self, username):
        """Load repositories and programming languages"""
        try:
            repos_resp = self._fetch_with_retry(
                f"{self.api_base}/users/{username}/repos"
                + "?sort=stars&per_page=15"
            )

            if repos_resp.status_code != 200:
                return

            repos = repos_resp.json()

            for repo in repos:
                language = repo.get("language", "Unknown")

                # Create repository
                db.execute("""
                    MERGE (r:Repository {name: $repo_name})
                    SET r.url = $url, r.stars = $stars
                """,
                    repo_name=f"{username}/{repo['name']}",
                    url=repo["html_url"],
                    stars=repo.get("stargazers_count", 0))

                # Create ownership relationship
                db.execute("""
                    MATCH (d:Developer {username: $username})
                    MATCH (r:Repository {name: $repo_name})
                    MERGE (d)-[:OWNS]->(r)
                """,
                    username=username,
                    repo_name=f"{username}/{repo['name']}")

                # Create language node and relationships
                if language and language != "Unknown":
                    db.execute("""
                        MERGE (l:Language {name: $language})
                        WITH l
                        MATCH (r:Repository {name: $repo_name})
                        MERGE (r)-[:LANGUAGE_IS]->(l)
                        WITH l
                        MATCH (d:Developer {username: $username})
                        MERGE (d)-[:PROGRAMS_IN]->(l)
                    """,
                        language=language,
                        repo_name=f"{username}/{repo['name']}",
                        username=username)

            logger.info(f"Loaded {len(repos)} repos for {username}")

        except Exception as e:
            logger.error(f"Error loading repos: {e}")

    def _load_second_degree(self, username, max_followers=5):
        """Load followers of followers for 2nd-degree connections.
        Limits to top N followers to control API usage."""
        try:
            # Get the user's followers from DB
            followers = db.query("""
                MATCH (f:Developer)-[:FOLLOWS]->(d:Developer {username: $username})
                RETURN f.username AS username
                LIMIT $limit
            """, username=username, limit=max_followers)

            if not followers:
                return

            count = 0
            for f in followers:
                fname = f['username']
                # Skip if already loaded with followers
                existing = db.query("""
                    MATCH (f:Developer {username: $fname})<-[:FOLLOWS]-(:Developer)
                    RETURN count(*) AS cnt
                """, fname=fname)

                if existing and existing[0]['cnt'] > 0:
                    continue  # Already has follower data

                self._load_followers(fname)
                count += 1
                import time
                time.sleep(1)  # Rate limit protection

            if count > 0:
                logger.info(f"Loaded 2nd-degree data for {count} followers of {username}")

        except Exception as e:
            logger.error(f"Error loading 2nd-degree: {e}")

    def create_indexes(self):
        """Create database indexes for performance"""
        try:
            db.execute("""
                CREATE INDEX developer_username IF NOT EXISTS
                FOR (d:Developer) ON (d.username)
            """)
            db.execute("""
                CREATE INDEX language_name IF NOT EXISTS
                FOR (l:Language) ON (l.name)
            """)
            db.execute("""
                CREATE INDEX repo_name IF NOT EXISTS
                FOR (r:Repository) ON (r.name)
            """)
            logger.info("Indexes created")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)

    if not db.connect():
        print("Failed to connect to database")
        sys.exit(1)

    loader = GitHubLoader()
    loader.create_indexes()

    if len(sys.argv) > 1:
        username = sys.argv[1]
        if loader.load_user(username):
            print(f"Successfully loaded {username}")
        else:
            print(f"Failed to load {username}")
    else:
        print("Usage: python github_loader.py <username>")

    db.close()
