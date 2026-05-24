from django.shortcuts import render, redirect
from .services import (
    get_github_profile,
    get_github_repos,
    get_github_followers,
    get_language_breakdown_for_repos,
    get_github_rate_limit,
)
from django.contrib import messages
from django.utils.dateparse import parse_datetime

from .models import SavedGitHubProfile

def search_view(request):
    # Get the username from the search form
    username = request.GET.get("username", "").strip()

    error_message = None

    # If the form was submitted but username is empty
    if "username" in request.GET and not username:
        error_message = "Please enter a GitHub username."

    # If username exists, redirect to the profile page
    if username:
        return redirect("profile", username=username)

    context = {
        "error_message": error_message,
    }

    # Render the search page
    return render(request, "explorer/search.html", context)


def profile_view(request, username):
    # Call GitHub API to get the user profile
    status_code, profile, error_type = get_github_profile(username)

    error_message = None
    profile_stats = []
    is_saved = False

    if error_type == "user_not_found":
        error_message = "GitHub user not found. Please check the username."

    elif error_type == "network_error":
        error_message = "Network error. Please check your internet connection."

    elif error_type == "invalid_response":
        error_message = "GitHub returned an invalid response. Please try again."

    elif error_type == "rate_limit":
        error_message = "GitHub API rate limit reached. Please try again later."

    elif error_type == "api_error":
        error_message = "GitHub API error. Please try again later."

    if profile:
        profile_stats = [
            {"label": "Followers", "value": profile["followers"]},
            {"label": "Following", "value": profile["following"]},
            {"label": "Public repositories", "value": profile["public_repos"]},
        ]

        # Check if this GitHub profile already exists in our database
        is_saved = SavedGitHubProfile.objects.filter(login=profile["login"]).exists()

    rate_limit = get_github_rate_limit()

    if rate_limit and rate_limit["remaining"] == 0:
        error_message = f"GitHub API rate limit reached. Please try again in about {rate_limit['reset_minutes']} minutes."

    context = {
        "section": "profile",
        "username": username,
        "profile": profile,
        "profile_stats": profile_stats,
        "error_message": error_message,
        "rate_limit": rate_limit,
        "is_saved": is_saved,
    }

    return render(request, "explorer/profile.html", context)
def repos_view(request, username):
    # Get the page number from the URL
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1

    # Page number should never be less than 1
    if page < 1:
        page = 1

    # Call GitHub API to get user repositories
    repos, pagination, error_type = get_github_repos(username, page)
    
    language_breakdown = []
    if repos:
        language_breakdown = get_language_breakdown_for_repos(username, repos)

    error_message = None

    if error_type == "network_error":
        error_message = "Network error. Please check your internet connection."

    elif error_type == "invalid_response":
        error_message = "GitHub returned an invalid response. Please try again."

    elif error_type == "rate_limit":
        error_message = "GitHub API rate limit reached. Please try again later."

    elif error_type == "api_error":
        error_message = "GitHub API error. Please try again later."
    rate_limit = get_github_rate_limit()

    context = {
    "section": "repos",
    "username": username,
    "repos": repos,
    "pagination": pagination,
    "error_message": error_message,
    "page": page,
    "previous_page": page - 1,
    "next_page": page + 1,
    "language_breakdown": language_breakdown,
    "rate_limit": rate_limit,
    }

    return render(request, "explorer/profile.html", context)
def followers_view(request, username):
    # Get the page number from the URL
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1

    # Page number should never be less than 1
    if page < 1:
        page = 1

    # Call GitHub API to get user followers
    followers, pagination, error_type = get_github_followers(username, page)

    error_message = None

    if error_type == "network_error":
        error_message = "Network error. Please check your internet connection."

    elif error_type == "invalid_response":
        error_message = "GitHub returned an invalid response. Please try again."

    elif error_type == "rate_limit":
        error_message = "GitHub API rate limit reached. Please try again later."

    elif error_type == "api_error":
        error_message = "GitHub API error. Please try again later."
    
    rate_limit = get_github_rate_limit()
    context = {
    "section": "followers",
    "username": username,
    "followers": followers,
    "pagination": pagination,
    "error_message": error_message,
    "page": page,
    "previous_page": page - 1,
    "next_page": page + 1,
    "rate_limit": rate_limit,
    }

    return render(request, "explorer/profile.html", context)
def save_profile_view(request, username):
    # Only POST requests can save data
    if request.method != "POST":
        return redirect("profile", username=username)

    # Get the profile from GitHub API again before saving
    status_code, profile, error_type = get_github_profile(username)

    if error_type or not profile:
        messages.error(request, "Could not save this profile. Please try again.")
        return redirect("profile", username=username)

    # Convert GitHub created_at string to Python datetime
    github_created_at = None

    if profile.get("created_at"):
        github_created_at = parse_datetime(profile.get("created_at"))

    # Create the profile if it does not exist, update it if it exists
    saved_profile, created = SavedGitHubProfile.objects.update_or_create(
    login=profile.get("login"),
    defaults={
        "avatar_url": profile.get("avatar_url"),
        "name": profile.get("name"),
        "bio": profile.get("bio"),
        "location": profile.get("location"),
        "followers": profile.get("followers") or 0,
        "following": profile.get("following") or 0,
        "public_repos": profile.get("public_repos") or 0,
        "github_created_at": github_created_at,
        "html_url": profile.get("html_url"),
        }
    )

    if created:
        messages.success(request, f"{profile.get('login')} was saved in the database.")
    else:
        messages.success(request, f"{profile.get('login')} was updated in the database.")

    return redirect("profile", username=profile.get("login"))
def saved_profiles_view(request):
    # Get all saved GitHub profiles from the database
    saved_profiles = SavedGitHubProfile.objects.all().order_by("-saved_at")

    # Count how many profiles are saved
    saved_profiles_count = saved_profiles.count()

    context = {
        "saved_profiles": saved_profiles,
        "saved_profiles_count": saved_profiles_count,
    }

    return render(request, "explorer/saved_profiles.html", context)

    return render(request, "explorer/saved_profiles.html", context)
def delete_saved_profile_view(request, username):
    # Only POST requests can delete data
    if request.method != "POST":
        return redirect("saved_profiles")

    try:
        # Find the saved profile by GitHub username
        saved_profile = SavedGitHubProfile.objects.get(login=username)

        # Delete the saved profile from the database
        saved_profile.delete()

        messages.success(request, f"{username} was deleted from the database.")

    except SavedGitHubProfile.DoesNotExist:
        # If the profile does not exist, show an error message
        messages.error(request, "Saved profile not found.")

    return redirect("saved_profiles")