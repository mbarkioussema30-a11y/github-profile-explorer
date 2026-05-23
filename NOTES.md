# GitHub Profile Explorer - Notes

## Decisions Made

### 1. Django project structure

I created a Django project with one main app called `explorer`.

The app contains:
- `views.py` for handling user requests and rendering pages
- `services.py` for all GitHub API calls
- `utils.py` for helper functions such as pagination parsing and language percentage calculation
- `templates/explorer/` for HTML templates

This separation makes the project easier to understand, test, and maintain.

### 2. Separate pages

I used separate pages for:
- the search page
- the profile page
- the repositories page
- the followers page
- the error page

This makes the application cleaner and easier to extend.

### 3. GitHub API usage

The app uses the GitHub public API to fetch:
- user profile information
- public repositories
- followers
- repository languages
- rate limit information

Each request includes a `User-Agent` header as required by the assessment.

### 4. Error handling

The app handles:
- empty username input
- user not found
- network errors
- invalid API responses
- GitHub API rate limit errors

Instead of showing raw Django errors to the user, the app displays friendly messages.

### 5. Pagination

Repositories and followers are paginated using GitHub API pagination.

The app reads the GitHub `Link` response header to detect if a next or previous page exists.

### 6. Language breakdown

The language breakdown is calculated by calling the GitHub languages endpoint for repositories on the current page.

The byte counts are aggregated and converted into percentages.

### 7. Caching

Repository language responses are cached for 5 minutes.

This avoids calling the GitHub languages endpoint again and again when the same page is loaded multiple times.

### 8. Database saving feature

I added a database saving feature using Django models and migrations.

The app can save a searched GitHub profile into the local SQLite database using a `Save in DB` button. I used `update_or_create()` to prevent duplicate saved profiles and to update existing records when the same profile is saved again.

---

## What I Would Improve With More Time

- Add GitHub Personal Access Token support to increase the API rate limit.
- Improve the visual design further with more responsive components and better UI details.
- Add more tests for repositories, followers, pagination, and API error cases.
- Add better date formatting for the GitHub join date.
- Cache more API responses, such as profile data and repository lists.
- Add a dark mode toggle.
- Add a comparison page to compare two GitHub users.
- Improve performance when calculating language breakdown for users with many repositories.
- Add a page to list all saved GitHub profiles from the database.
- Add a delete button to remove saved profiles from the database.
- Add a detail page for saved profiles.
- Replace SQLite with PostgreSQL for production deployment.

---

## Issues I Ran Into

- I reached the GitHub unauthenticated API rate limit during testing.
- I had a `TemplateDoesNotExist` error because a template file was not created in the correct folder.
- I had an indentation issue in Python after an `except` block.
- I accidentally placed a `return None, None, "network_error"` outside the `except` block, which caused the app to always show a network error.
- I learned that Python indentation is very important because it controls which code belongs to each block.
- I learned how Django models and migrations work.
- I learned that `db.sqlite3` should not be pushed to GitHub because it is a local development database.
- I added migrations instead, so the database structure can be recreated by running `py manage.py migrate`.
---

## Database Feature

I added a database feature to save searched GitHub profiles locally.

I created a Django model called `SavedGitHubProfile` in `explorer/models.py`. This model stores the main GitHub profile information, such as:

- GitHub username
- avatar URL
- name
- bio
- location
- followers count
- following count
- public repositories count
- GitHub profile URL
- GitHub account creation date
- local save/update date

After creating the model, I generated and applied migrations using:

```bash
py manage.py makemigrations explorer
py manage.py migrate
```

This created the database table for saved GitHub profiles.

I also added a `Save in DB` button on the profile page. When the user clicks this button, the app sends a POST request protected with a CSRF token. The view then calls the GitHub API again, retrieves the latest profile data, and saves it into the database.

I used `update_or_create()` to avoid duplicate profiles. If the profile already exists in the database, it is updated. If it does not exist, it is created.

I also added Django messages to show a success or error message after the save action.

The local database file `db.sqlite3` is not pushed to GitHub because it contains local development data. Instead, the migrations are included so another user can recreate the database by running:

```bash
py manage.py migrate
```

---

## How To Run The Project

1. Clone or download the project.

2. Open the project folder in VS Code.

3. Create a virtual environment.

```bash
py -m venv venv
```

4. Activate the virtual environment.

```bash
venv\Scripts\activate
```

5. Install the project dependencies.

```bash
py -m pip install -r requirements.txt
```

6. Apply database migrations.

```bash
py manage.py migrate
```

7. Run the Django development server.

```bash
py manage.py runserver
```

8. Open the application in the browser.

```text
http://127.0.0.1:8000/
```

9. To stop the server, press:

```text
CTRL + C
```

---

## Test Command

To run the tests for the `explorer` app, use:

```bash
py manage.py test explorer
```

This command runs the unit tests defined in `explorer/tests.py`, including utility tests, view tests, and database model tests.