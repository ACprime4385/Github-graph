# GitHub Developer Network Explorer

Discover developer connections, followers, and language networks on GitHub using a graph database.

## Architecture

```
Browser → Flask Backend → CognoDB (Neo4j) → GitHub API
```

- **Backend:** Python 3.11 + Flask
- **Database:** CognoDB (Managed Neo4j) — graph traversal for 1-hop and 2-hop connections
- **Frontend:** Vanilla HTML/CSS/JS — dark theme, responsive design
- **Deployment:** Render.com (auto-deploy from GitHub)

## Features

- **Developer Profile:** Search any GitHub username and view their profile
- **Direct Followers:** See who follows a developer (1-hop)
- **Second-Degree Connections:** Discover followers-of-followers (2-hop) ⭐
- **Language Network:** Find developers who share programming languages (2-hop) ⭐
- **Network Statistics:** Aggregated metrics (followers, connections, languages, repos)

## Quick Start

### Prerequisites

- Python 3.11+
- A [CognoDB](https://cognodb.cloud) account (free tier)
- A [GitHub Personal Access Token](https://github.com/settings/tokens)

### Setup

```bash
# Clone the repo
git clone https://github.com/ACprime4385/github-graph-app.git
cd github-graph-app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your credentials

# Run the app
python src/app.py
```

Open http://localhost:5000 in your browser.

### Seed Data (Optional)

Load specific users into the database:

```bash
python scripts/seed_data.py torvalds gaearon tj
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/developer/<username>` | GET | Developer profile |
| `/api/followers/<username>` | GET | Direct followers (1-hop) |
| `/api/second-degree/<username>` | GET | Followers of followers (2-hop) |
| `/api/language-network/<username>` | GET | Shared language network (2-hop) |
| `/api/network-stats/<username>` | GET | Aggregated network stats |

All endpoints support query parameter `?limit=N` for pagination.

## Deployment (Render.com)

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set environment variables in the Render Dashboard:
   - `NEO4J_URI` — Your CognoDB Bolt URL
   - `NEO4J_USER` — Database username
   - `NEO4J_PASSWORD` — Database password
   - `GITHUB_TOKEN` — GitHub personal access token
5. Deploy (auto-triggers on push to main)

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEO4J_URI` | Yes | CognoDB connection URI (bolt+s://...) |
| `NEO4J_USER` | Yes | Database username |
| `NEO4J_PASSWORD` | Yes | Database password |
| `GITHUB_TOKEN` | Yes | GitHub personal access token |
| `FLASK_ENV` | No | `development` or `production` |
| `PORT` | No | Server port (default: 5000) |

## Security

- `.env` is git-ignored — never commit credentials
- All Cypher queries use parameterized inputs (no injection)
- GitHub API rate limiting handled with exponential backoff
- Input validation on all username parameters

## License

MIT
