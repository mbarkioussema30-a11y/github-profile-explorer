import requests
import time
import logging
from requests.exceptions import RequestException
from django.core.cache import cache
from .utils import parse_github_link_header, calculate_language_percentages

logger = logging.getLogger(__name__)

def get_github_profile(username):
    # Build the GitHub API URL using the username
    url = f"https://api.github.com/users/{username}"

    # GitHub asks us to identify our app with a User-Agent header
    headers = {
        "User-Agent": "GitHubExplorer-InternTest/1.0",
        "Accept": "application/vnd.github+json",
    }

    try:
        # Send a GET request to GitHub API with a timeout
        response = requests.get(url, headers=headers, timeout=10)

    except RequestException as error:
        # Print the real error in the terminal for debugging
        print("REAL PROFILE ERROR:", error)

        # Log the real network error server-side
        logger.exception(
            "Network error while fetching GitHub profile for username=%s",
            username
        )

        return None, None, "network_error"

    try:
        # Convert the JSON response into a Python dictionary
        data = response.json()

    except ValueError:
        # Handle invalid JSON responses
        logger.exception(
            "Invalid JSON response while fetching GitHub profile for username=%s",
            username
        )

        return response.status_code, None, "invalid_response"

    if response.status_code == 200:
        # Extract only the useful information from the JSON data
        profile = {
            "login": data.get("login"),
            "avatar_url": data.get("avatar_url"),
            "name": data.get("name"),
            "bio": data.get("bio"),
            "location": data.get("location"),
            "followers": data.get("followers"),
            "following": data.get("following"),
            "public_repos": data.get("public_repos"),
            "created_at": data.get("created_at"),
            "html_url": data.get("html_url"),
        }

        return response.status_code, profile, None

    if response.status_code == 404:
        return response.status_code, None, "user_not_found"

    if response.status_code in [403, 429]:
        return response.status_code, None, "rate_limit"

    logger.error(
        "GitHub API error while fetching profile for username=%s, status_code=%s",
        username,
        response.status_code
    )

    return response.status_code, None, "api_error"
def get_github_repos(username, page=1):
    # Build the GitHub API URL for user repositories
    url = f"https://api.github.com/users/{username}/repos"

    # GitHub asks us to identify our app with a User-Agent header
    headers = {
        "User-Agent": "GitHubExplorer-InternTest/1.0",
        "Accept": "application/vnd.github+json",
    }

    # Query parameters for pagination and sorting
    params = {
        "page": page,
        "per_page": 30,
        "sort": "updated",
    }

    try:
        # Send a GET request to GitHub API
        response = requests.get(url, headers=headers, params=params, timeout=10)

    except RequestException as error:
        # Log the real network error server-side
        logger.exception(
            "Network error while fetching repositories for username=%s",
            username
        )

        return None, None, "network_error"

    try:
        # Convert JSON response into Python data
        data = response.json()

    except ValueError:
        # Handle invalid JSON
        logger.exception(
            "Invalid JSON response while fetching repositories for username=%s",
            username
        )

        return None, None, "invalid_response"

    if response.status_code == 200:
        repos = []

        # Clean the repositories data
        for repo in data:
            repos.append({
                "name": repo.get("name"),
                "description": repo.get("description"),
                "stars": repo.get("stargazers_count"),
                "forks": repo.get("forks_count"),
                "language": repo.get("language"),
                "html_url": repo.get("html_url"),
            })

        # Read GitHub Link header to know if next/prev pages exist
        link_header = response.headers.get("Link", "")
        pagination = parse_github_link_header(link_header)

        return repos, pagination, None

    if response.status_code in [403, 429]:
        return None, None, "rate_limit"

    logger.error(
        "GitHub API error while fetching repositories for username=%s, status_code=%s",
        username,
        response.status_code
    )

    return None, None, "api_error"
def get_github_followers(username, page=1):
    # Build the GitHub API URL for user followers
    url = f"https://api.github.com/users/{username}/followers"

    # GitHub asks us to identify our app with a User-Agent header
    headers = {
        "User-Agent": "GitHubExplorer-InternTest/1.0",
        "Accept": "application/vnd.github+json",
    }

    # Query parameters for pagination
    params = {
        "page": page,
        "per_page": 30,
    }

    try:
        # Send a GET request to GitHub API
        response = requests.get(url, headers=headers, params=params, timeout=10)

    except RequestException as error:
        # Log the real network error server-side
        logger.exception("Network error while fetching followers for username=%s", username)

        return None, None, "network_error"

    try:
        # Convert JSON response into Python data
        data = response.json()

    except ValueError:
        # Handle invalid JSON
        return None, None, "invalid_response"

    if response.status_code == 200:
        followers = []

        # Clean the followers data
        for follower in data:
            followers.append({
                "login": follower.get("login"),
                "avatar_url": follower.get("avatar_url"),
                "html_url": follower.get("html_url"),
            })

        # Read GitHub Link header to know if next/prev pages exist
        link_header = response.headers.get("Link", "")
        pagination = parse_github_link_header(link_header)

        return followers, pagination, None

    if response.status_code in [403, 429]:
        return None, None, "rate_limit"

    return None, None, "api_error"
def get_repo_languages(username, repo_name):
    # Create a cache key for this repository languages
    cache_key = f"languages_{username}_{repo_name}"

    # Try to get languages from cache first
    cached_languages = cache.get(cache_key)

    if cached_languages is not None:
        return cached_languages

    # Build the GitHub API URL for repo languages
    url = f"https://api.github.com/repos/{username}/{repo_name}/languages"

    headers = {
        "User-Agent": "GitHubExplorer-InternTest/1.0",
        "Accept": "application/vnd.github+json",
    }

    try:
        # Send a GET request to GitHub API
        response = requests.get(url, headers=headers, timeout=10)

    except RequestException as error:
        # Log the error, but do not crash the page
        logger.exception(
            "Network error while fetching languages for username=%s repo=%s",
            username,
            repo_name
        )

        return {}

    try:
        # Convert JSON response into Python dictionary
        data = response.json()

    except ValueError:
        # If the response is not valid JSON, return empty data
        return {}

    if response.status_code == 200:
        # Save languages in cache for 5 minutes
        cache.set(cache_key, data, 300)

        return data

    # If GitHub returns an error for this repo, ignore it
    return {}
def get_language_breakdown_for_repos(username, repos):
    # This dictionary will store total bytes for each language
    language_totals = {}

    # If there are no repositories, return an empty list
    if not repos:
        return []

    # Loop through the repositories displayed on the current page
    for repo in repos:
        repo_name = repo.get("name")

        if not repo_name:
            continue

        # Get languages for this repository
        repo_languages = get_repo_languages(username, repo_name)

        # Add each language bytes to the global total
        for language, bytes_count in repo_languages.items():
            language_totals[language] = language_totals.get(language, 0) + bytes_count

    # Convert total bytes into percentages
    return calculate_language_percentages(language_totals)
def get_github_rate_limit():
    # Build the GitHub API URL for rate limit information
    url = "https://api.github.com/rate_limit"

    headers = {
        "User-Agent": "GitHubExplorer-InternTest/1.0",
        "Accept": "application/vnd.github+json",
    }

    try:
        # Send a GET request to GitHub API
        response = requests.get(url, headers=headers, timeout=10)

    except RequestException:
        # If the rate limit request fails, return None
        return None

    try:
        # Convert JSON response into Python dictionary
        data = response.json()

    except ValueError:
        # If the response is not valid JSON, return None
        return None

    if response.status_code != 200:
        return None

    core = data.get("resources", {}).get("core", {})

    remaining = core.get("remaining")
    limit = core.get("limit")
    reset_timestamp = core.get("reset")

    reset_minutes = None

    if reset_timestamp:
        # Calculate how many minutes remain until the limit resets
        seconds_until_reset = reset_timestamp - int(time.time())
        reset_minutes = max(0, round(seconds_until_reset / 60))

    rate_limit = {
        "remaining": remaining,
        "limit": limit,
        "reset_minutes": reset_minutes,
    }

    return rate_limit