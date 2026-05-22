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

---

## What I Would Improve With More Time

- Add GitHub Personal Access Token support to increase the API rate limit.
- Improve the visual design with a separate CSS file instead of inline CSS in `base.html`.
- Add more tests for repositories, followers, pagination, and API error cases.
- Add better date formatting for the GitHub join date.
- Cache more API responses, such as profile data and repository lists.
- Add a dark mode toggle.
- Add a comparison page to compare two GitHub users.
- Improve performance when calculating language breakdown for users with many repositories.

---

## Issues I Ran Into

- I reached the GitHub unauthenticated API rate limit during testing.
- I had a `TemplateDoesNotExist` error because a template file was not created in the correct folder.
- I had an indentation issue in Python after an `except` block.
- I accidentally placed a `return None, None, "network_error"` outside the `except` block, which caused the app to always show a network error.
- I learned that Python indentation is very important because it controls which code belongs to each block.

---

## How To Run The Project

1. Clone or download the project.

2. Open the project folder in VS Code.

### Create a virtual environment.

In terminal of vscode type :

py -m venv venv

### Activate the virtual environment.

venv\Scripts\activate

### Install the project dependencies.

py -m pip install -r requirements.txt

### Run the Django development server.

py manage.py runserver

### Open the application in the browser.

http://127.0.0.1:8000/

### To stop the server, press:

CTRL + C