import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestAPI(unittest.TestCase):
    """Basic API tests (requires running database for full tests)"""

    def setUp(self):
        from src.app import app
        self.app = app
        self.client = app.test_client()

    def test_index_loads(self):
        """Test that the index page loads"""
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_health_endpoint(self):
        """Test health endpoint returns valid JSON"""
        resp = self.client.get('/api/health')
        self.assertIn(resp.status_code, [200, 503])
        data = resp.get_json()
        self.assertIn('status', data)

    def test_invalid_username_400(self):
        """Test invalid username returns 400"""
        resp = self.client.get('/api/developer/invalid@username!')
        self.assertEqual(resp.status_code, 400)

    def test_long_username_400(self):
        """Test username > 39 chars returns 400"""
        resp = self.client.get('/api/developer/' + 'a' * 40)
        self.assertEqual(resp.status_code, 400)

    def test_followers_invalid_username(self):
        """Test followers with invalid username returns 400"""
        resp = self.client.get('/api/followers/invalid@user')
        self.assertEqual(resp.status_code, 400)

    def test_second_degree_invalid_username(self):
        """Test second-degree with invalid username returns 400"""
        resp = self.client.get('/api/second-degree/invalid@user')
        self.assertEqual(resp.status_code, 400)

    def test_language_network_invalid_username(self):
        """Test language-network with invalid username returns 400"""
        resp = self.client.get('/api/language-network/invalid@user')
        self.assertEqual(resp.status_code, 400)

    def test_network_stats_invalid_username(self):
        """Test network-stats with invalid username returns 400"""
        resp = self.client.get('/api/network-stats/invalid@user')
        self.assertEqual(resp.status_code, 400)


if __name__ == '__main__':
    unittest.main()
