import sys
import os

# Ensure src/ directory is on the path for sibling module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request
from database import db
from github_loader import GitHubLoader
from dotenv import load_dotenv
import logging
import re

load_dotenv()

# Flask needs templates/ and static/ at the project root
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__,
            template_folder=os.path.join(_project_root, 'templates'),
            static_folder=os.path.join(_project_root, 'static'))

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# GitHub username validation regex
GITHUB_USERNAME_REGEX = r'^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}$'


def validate_username(username):
    """Validate GitHub username format"""
    if not username or len(username) > 39:
        return False
    return re.match(GITHUB_USERNAME_REGEX, username.lower()) is not None


def make_error_response(message, status_code):
    """Create standardized error response"""
    from datetime import datetime, timezone
    return jsonify({
        "error": message,
        "status_code": status_code,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }), status_code


# Helper: ensure DB is connected (called per-route after input validation)
def ensure_db():
    """Return error response if DB unavailable, or None if OK"""
    if not db.driver:
        if not db.connect():
            return make_error_response("Database unavailable", 503)
    return None


# Middleware: Error handler
@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"Unhandled error: {error}")
    return jsonify({
        "error": "Internal server error",
        "status": "error"
    }), 500


# ============= ROUTES =============

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    err = ensure_db()
    if err:
        return err
    try:
        with db.driver.session() as session:
            session.run("RETURN 1")
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503


@app.route('/api/developer/<username>', methods=['GET'])
def get_developer(username):
    """Get developer profile"""
    username = username.strip().lower()
    if not validate_username(username):
        return make_error_response("Invalid username format", 400)

    err = ensure_db()
    if err:
        return err

    # Try to get from DB first
    result = db.query("""
        MATCH (d:Developer {username: $username})
        RETURN d.username AS username,
               d.name AS name,
               d.followers AS followers,
               d.public_repos AS public_repos,
               d.profile_url AS profile_url
    """, username=username)

    if result and result[0]:
        return jsonify(result[0]), 200

    # If not in DB, fetch from GitHub
    try:
        loader = GitHubLoader()
        if not loader.load_user(username):
            return make_error_response("Developer not found", 404)
    except Exception:
        return make_error_response("GitHub API temporarily unavailable", 503)

    # Now get from DB
    result = db.query("""
        MATCH (d:Developer {username: $username})
        RETURN d.username AS username,
               d.name AS name,
               d.followers AS followers,
               d.public_repos AS public_repos,
               d.profile_url AS profile_url
    """, username=username)

    if result:
        return jsonify(result[0]), 200

    return make_error_response("Database error", 500)


@app.route('/api/followers/<username>', methods=['GET'])
def get_followers(username):
    """Get direct followers (1-hop)"""
    username = username.strip().lower()
    if not validate_username(username):
        return make_error_response("Invalid username format", 400)

    err = ensure_db()
    if err:
        return err

    limit = request.args.get('limit', default=20, type=int)
    if limit < 1 or limit > 100:
        limit = 20

    results = db.query("""
        MATCH (follower:Developer)-[:FOLLOWS]->(d:Developer {username: $username})
        RETURN follower {
            username: follower.username,
            followers: follower.followers,
            profile_url: follower.profile_url
        } AS follower
        ORDER BY follower.followers DESC
        LIMIT $limit
    """, username=username, limit=limit)

    if results is None:
        return make_error_response("Database error", 500)

    return jsonify([r["follower"] for r in results]), 200


@app.route('/api/second-degree/<username>', methods=['GET'])
def get_second_degree(username):
    """Get followers of followers (2-hop)"""
    username = username.strip().lower()
    if not validate_username(username):
        return make_error_response("Invalid username format", 400)

    err = ensure_db()
    if err:
        return err

    limit = request.args.get('limit', default=10, type=int)
    if limit < 1 or limit > 50:
        limit = 10

    results = db.query("""
        MATCH (me:Developer {username: $username})
              <-[:FOLLOWS]-(follower:Developer)
              <-[:FOLLOWS]-(friend:Developer)
        WHERE me.username <> friend.username
        RETURN DISTINCT friend.username AS username,
               COUNT(DISTINCT follower) AS mutual_connections
        ORDER BY mutual_connections DESC
        LIMIT $limit
    """, username=username, limit=limit)

    if results is None:
        return make_error_response("Database error", 500)

    return jsonify(results), 200


@app.route('/api/language-network/<username>', methods=['GET'])
def get_language_network(username):
    """Get developers with shared languages (2-hop)"""
    username = username.strip().lower()
    if not validate_username(username):
        return make_error_response("Invalid username format", 400)

    err = ensure_db()
    if err:
        return err

    limit = request.args.get('limit', default=15, type=int)
    if limit < 1 or limit > 50:
        limit = 15

    results = db.query("""
        MATCH (me:Developer {username: $username})
              -[:PROGRAMS_IN]->(lang:Language)
              <-[:PROGRAMS_IN]-(other:Developer)
        WHERE me.username <> other.username
        RETURN other.username AS username,
               COUNT(DISTINCT lang) AS shared_languages,
               COLLECT(DISTINCT lang.name) AS languages
        ORDER BY shared_languages DESC
        LIMIT $limit
    """, username=username, limit=limit)

    if results is None:
        return make_error_response("Database error", 500)

    return jsonify(results), 200


@app.route('/api/network-stats/<username>', methods=['GET'])
def get_network_stats(username):
    """Get network statistics"""
    username = username.strip().lower()
    if not validate_username(username):
        return make_error_response("Invalid username format", 400)

    err = ensure_db()
    if err:
        return err

    stats = {}

    # Direct followers
    followers_result = db.query("""
        MATCH (f:Developer)-[:FOLLOWS]->(d:Developer {username: $username})
        RETURN COUNT(f) AS count
    """, username=username)
    stats["direct_followers"] = followers_result[0]["count"] if followers_result else 0

    # Second degree
    second_result = db.query("""
        MATCH (me:Developer {username: $username})
              <-[:FOLLOWS]-(:Developer)
              <-[:FOLLOWS]-(friend:Developer)
        WHERE me.username <> friend.username
        RETURN COUNT(DISTINCT friend) AS count
    """, username=username)
    stats["second_degree"] = second_result[0]["count"] if second_result else 0

    # Languages
    langs_result = db.query("""
        MATCH (d:Developer {username: $username})
              -[:PROGRAMS_IN]->(lang:Language)
        RETURN COUNT(lang) AS count
    """, username=username)
    stats["languages"] = langs_result[0]["count"] if langs_result else 0

    # Repos
    repos_result = db.query("""
        MATCH (d:Developer {username: $username})
              -[:OWNS]->(r:Repository)
        RETURN COUNT(r) AS count
    """, username=username)
    stats["repositories"] = repos_result[0]["count"] if repos_result else 0

    return jsonify(stats), 200


@app.route('/', methods=['GET'])
def index():
    """Serve the frontend"""
    from flask import render_template
    return render_template('index.html')


# ============= APP STARTUP =============

if __name__ == '__main__':
    try:
        if not db.connect():
            logger.warning("Database not available on startup - API routes will attempt reconnection")

        app.run(
            host='0.0.0.0',
            port=int(os.getenv("PORT", 5000)),
            debug=os.getenv("FLASK_ENV") == "development"
        )
    finally:
        db.close()
