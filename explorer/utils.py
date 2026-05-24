from datetime import datetime
from django.utils.dateparse import parse_datetime
def parse_github_link_header(link_header):
    # Create default pagination information
    pagination = {
        "has_next": False,
        "has_prev": False,
    }

    # If there is no Link header, return default values
    if not link_header:
        return pagination

    # Split the Link header into parts
    links = link_header.split(",")

    for link in links:
        # Check if the current link is a next page
        if 'rel="next"' in link:
            pagination["has_next"] = True

        # Check if the current link is a previous page
        if 'rel="prev"' in link:
            pagination["has_prev"] = True

    return pagination
def calculate_language_percentages(language_totals):
    # Calculate the total number of bytes for all languages
    total_bytes = sum(language_totals.values())

    # If there are no bytes, return an empty list
    if total_bytes == 0:
        return []

    percentages = []

    # Convert each language byte count into a percentage
    for language, bytes_count in language_totals.items():
        percentage = (bytes_count / total_bytes) * 100

        percentages.append({
            "language": language,
            "percentage": round(percentage, 2),
        })

    # Sort languages from highest percentage to lowest percentage
    percentages.sort(key=lambda item: item["percentage"], reverse=True)

    return percentages
def format_github_date(date_string):
    # If the date is empty, return a default message
    if not date_string:
        return "Not available"

    # Convert GitHub date string into a Python datetime object
    parsed_date = parse_datetime(date_string)

    # If Django cannot parse the date, return the original value
    if not parsed_date:
        return date_string

    # Format the date in a readable way
    return parsed_date.strftime("%b %d, %Y")