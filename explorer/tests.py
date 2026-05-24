from django.test import TestCase
from unittest.mock import patch
from .models import SavedGitHubProfile

from .utils import calculate_language_percentages, parse_github_link_header


class UtilsTests(TestCase):
    def test_calculate_language_percentages(self):
        # Test if language byte counts are converted into percentages correctly
        language_totals = {
            "Python": 8000,
            "HTML": 1500,
            "CSS": 500,
        }

        result = calculate_language_percentages(language_totals)

        self.assertEqual(result[0]["language"], "Python")
        self.assertEqual(result[0]["percentage"], 80.0)

        self.assertEqual(result[1]["language"], "HTML")
        self.assertEqual(result[1]["percentage"], 15.0)

        self.assertEqual(result[2]["language"], "CSS")
        self.assertEqual(result[2]["percentage"], 5.0)

    def test_parse_github_link_header_with_next_and_prev(self):
        # Test if the GitHub Link header parser detects next and previous pages
        link_header = (
            '<https://api.github.com/users/test/repos?page=2>; rel="next", '
            '<https://api.github.com/users/test/repos?page=1>; rel="prev"'
        )

        result = parse_github_link_header(link_header)

        self.assertTrue(result["has_next"])
        self.assertTrue(result["has_prev"])


class ViewTests(TestCase):
    def test_search_page_loads(self):
        # Test if the search page loads correctly
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "GitHub Profile Search")

    def test_empty_username_shows_error(self):
        # Test if empty input shows a user-friendly error message
        response = self.client.get("/?username=")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please enter a GitHub username.")

    @patch("explorer.views.get_github_rate_limit")
    @patch("explorer.views.get_github_profile")
    def test_profile_page_with_mocked_github_api(self, mock_get_github_profile, mock_get_github_rate_limit):
        # Mock GitHub profile data so the test does not call the real GitHub API
        mock_get_github_profile.return_value = (
            200,
            {
                "login": "octocat",
                "avatar_url": "https://example.com/avatar.png",
                "name": "The Octocat",
                "bio": "GitHub mascot",
                "location": "GitHub",
                "followers": 100,
                "following": 10,
                "public_repos": 8,
                "created_at": "2011-01-25T18:44:36Z",
                "formatted_created_at": "Jan 25, 2011",
                "html_url": "https://github.com/octocat",
            },
            None,
        )

        # Mock rate limit data
        mock_get_github_rate_limit.return_value = {
            "remaining": 50,
            "limit": 60,
            "reset_minutes": 30,
        }

        response = self.client.get("/profile/octocat/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The Octocat")
        self.assertContains(response, "octocat")
        self.assertContains(response, "Repositories")
        self.assertContains(response, "Followers")
        self.assertContains(response, "Saved Profiles")
        self.assertContains(response, "Save Profile")
class DatabaseTests(TestCase):
    def test_saved_github_profile_can_be_created(self):
        # Test if a GitHub profile can be saved in the database
        profile = SavedGitHubProfile.objects.create(
            login="octocat",
            avatar_url="https://example.com/avatar.png",
            name="The Octocat",
            bio="GitHub mascot",
            location="GitHub",
            followers=100,
            following=10,
            public_repos=8,
            html_url="https://github.com/octocat",
        )

        self.assertEqual(profile.login, "octocat")
        self.assertEqual(profile.name, "The Octocat")
        self.assertEqual(profile.followers, 100)
        self.assertEqual(str(profile), "octocat")

    def test_saved_github_profile_login_is_unique(self):
        # Test that the same GitHub username cannot be saved twice
        SavedGitHubProfile.objects.create(login="octocat")

        with self.assertRaises(Exception):
            SavedGitHubProfile.objects.create(login="octocat")