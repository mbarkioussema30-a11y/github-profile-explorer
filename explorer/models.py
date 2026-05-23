from django.db import models


class SavedGitHubProfile(models.Model):
    # GitHub username, unique to avoid duplicates
    login = models.CharField(max_length=100, unique=True)

    # GitHub profile information
    avatar_url = models.URLField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    # GitHub statistics
    followers = models.PositiveIntegerField(default=0)
    following = models.PositiveIntegerField(default=0)
    public_repos = models.PositiveIntegerField(default=0)

    # GitHub date and profile link
    github_created_at = models.DateTimeField(blank=True, null=True)
    html_url = models.URLField(blank=True, null=True)

    # Local save/update date
    saved_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Display object by username
        return self.login