"""All file handling: text (CSV), binary (pickle), copy and merge."""

import csv
import os
import pickle
from pathlib import Path

import analyzer
from exceptions import InvalidCOVIDDataError

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CSV_FILE = DATA_DIR / "covid_data.csv"
EXTRA_FILE = DATA_DIR / "extra_data.csv"
COPY_FILE = DATA_DIR / "copy.csv"
MERGED_FILE = DATA_DIR / "merged.csv"
BACKUP_FILE = DATA_DIR / "backup.dat"

DATA_DATE = "2020-05-17"

FIELDS = ["Date", "Country", "Confirmed", "New Cases", "Recovered", "Deaths", "Active"]
HEADER = ",".join(FIELDS)
REQUIRED_COLUMNS = ["Date", "Country", "Confirmed", "Recovered", "Deaths"]

# Simple map for assigning continent
CONTINENT_MAP = {
    "India": "Asia",
    "USA": "North America",
    "UK": "Europe",
    "Brazil": "South America",
    "Italy": "Europe",
    "Peru": "South America",
    "Mexico": "North America",
    "Turkey": "Asia",
}

def record_to_line(record):
    values = [
        str(record.get("Date", "")),
        str(record.get("Country", "")),
        str(record.get("Confirmed", 0)),
        str(record.get("New_Cases", 0)),
        str(record.get("Recovered", 0)),
        str(record.get("Deaths", 0)),
        str(record.get("Active", 0))
    ]
    return ",".join(values)

def to_int(text):
    text = (text or "").replace(",", "").strip()
    if text == "" or text.upper() == "N/A":
        return 0
    return int(float(text))

def read_records(path=CSV_FILE):
    records = []
    with open(path, "r", encoding="utf-8-sig") as file:
        header = file.readline().strip().split(",")
        for name in REQUIRED_COLUMNS:
            if name not in header:
                raise InvalidCOVIDDataError(f"Column '{name}' not found in {os.path.basename(path)}")
        reader = csv.DictReader(file, fieldnames=header)
        line_number = 1
        for row in reader:
            line_number += 1
            country = (row.get("Country") or "").strip()
            if country == "":
                continue
            try:
                date = (row.get("Date") or "").strip()
                continent = CONTINENT_MAP.get(country, "Unknown")
                record = analyzer.make_record(
                    date=date,
                    country=country,
                    confirmed=to_int(row.get("Confirmed")),
                    new_cases=to_int(row.get("New Cases")),
                    recovered=to_int(row.get("Recovered")),
                    deaths=to_int(row.get("Deaths")),
                    active=to_int(row.get("Active")),
                    continent=continent
                )
            except ValueError:
                print(f"  (skipped bad line {line_number})")
                continue
            records.append(record)
    return records

def count_lines(path=CSV_FILE):
    with open(path, "r") as file:
        text = file.read()
    return len(text.splitlines())

def append_record(record, path=CSV_FILE):
    if not os.path.exists(path):
        with open(path, "w") as file:
            file.write(HEADER + "\n")
    with open(path, "a") as file:
        file.write(record_to_line(record) + "\n")

def save_all(records, path=CSV_FILE):
    with open(path, "w") as file:
        file.write(HEADER + "\n")
        for record in records:
            file.write(record_to_line(record) + "\n")

def backup_data(records, path=BACKUP_FILE):
    with open(path, "wb") as file:
        pickle.dump(records, file)

def restore_backup(path=BACKUP_FILE):
    with open(path, "rb") as file:
        return pickle.load(file)

def copy_file(source=CSV_FILE, destination=COPY_FILE):
    with open(source, "rb") as src:
        data = src.read()
    with open(destination, "wb") as dst:
        dst.write(data)
    return len(data)

def merge_files(first, second, output=MERGED_FILE):
    for path in (first, second):
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
    seen = set()
    written = 0
    with open(output, "w") as out:
        out.write(HEADER + "\n")
        for path in (first, second):
            with open(path, "r") as file:
                file.readline()
                for line in file:
                    line = line.strip()
                    if line == "" or line in seen:
                        continue
                    seen.add(line)
                    out.write(line + "\n")
                    written += 1
    return written

def ensure_sample_data():
    pass