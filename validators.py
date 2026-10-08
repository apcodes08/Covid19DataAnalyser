"""Input validation and regular-expression helpers."""

import re
from datetime import datetime
from exceptions import InvalidCOVIDDataError

DATE_PATTERN = r"^(\d{4})-(\d{2})-(\d{2})$"
NAME_PATTERN = r"^[A-Za-z]+( [A-Za-z]+)*$"
CONTINENT_PATTERN = r"^[A-Za-z]+([ /][A-Za-z]+)*$"

def validate_date(text):
    text = text.strip()
    match = re.match(DATE_PATTERN, text)
    if match is None:
        raise InvalidCOVIDDataError(f"Date '{text}' must look like YYYY-MM-DD")
    year, month, day = match.groups()
    try:
        datetime(int(year), int(month), int(day))
    except ValueError:
        raise InvalidCOVIDDataError(f"Date '{text}' does not exist in the calendar")
    return text

def split_date(text):
    match = re.match(DATE_PATTERN, text)
    if match:
        return match.groups()
    return None

def clean_name(text, label, pattern=NAME_PATTERN):
    cleaned = re.sub(r"\s+", " ", text.strip())
    if re.match(pattern, cleaned) is None:
        raise InvalidCOVIDDataError(f"{label} '{cleaned}' must contain letters and spaces only")
    return cleaned

def validate_country(name):
    cleaned = clean_name(name, "Country")
    if len(cleaned) <= 3:
        return cleaned.upper()
    return cleaned.title()

def validate_continent(name):
    return clean_name(name, "Continent", pattern=CONTINENT_PATTERN).title()

def validate_number(text, field_name):
    try:
        value = int(text.strip())
    except ValueError:
        raise InvalidCOVIDDataError(f"{field_name} must be a whole number, got '{text}'")
    if value < 0:
        raise InvalidCOVIDDataError(f"{field_name} cannot be negative ({value})")
    return value

def validate_record(record):
    validate_date(record["Date"])
    validate_country(record["Country"])
    if record["Recovered"] + record["Deaths"] > record["Confirmed"]:
        raise InvalidCOVIDDataError("Recovered + Deaths cannot be more than Confirmed")
    return True

def regex_search_country(records, pattern):
    results = []
    for record in records:
        try:
            match = re.search(pattern, record["Country"], re.IGNORECASE)
        except re.error:
            raise InvalidCOVIDDataError(f"'{pattern}' is not a valid regular expression")
        if match:
            results.append((record, match))
    return results

def highlight(pattern, text):
    return re.sub(pattern, lambda m: "[" + m.group() + "]", text, flags=re.IGNORECASE)