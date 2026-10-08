"""COVID calculations, statistics, recursion and lambda sorting."""

import statistics

def calculate_rate(value, total, precision=2):
    try:
        return round(value / total * 100, precision)
    except ZeroDivisionError:
        return 0.0

def make_record(date, country, confirmed, new_cases, recovered, deaths, active, continent="Unknown"):
    return {
        "Date": date,
        "Country": country,
        "Confirmed": confirmed,
        "New_Cases": new_cases,
        "Recovered": recovered,
        "Deaths": deaths,
        "Active": active,
        "Continent": continent
    }

def total_field(records, field):
    total = 0
    for record in records:
        total += record.get(field, 0)
    return total

def recursive_total(records, field, index=0):
    if index == len(records):
        return 0
    return records[index].get(field, 0) + recursive_total(records, field, index + 1)

def get_latest_records(records):
    # Groups records by country and takes the one with max Date
    latest = {}
    for r in records:
        c = r["Country"]
        if c not in latest or r["Date"] > latest[c]["Date"]:
            latest[c] = r
    return list(latest.values())

def summarize(records):
    if len(records) == 0:
        return None
    
    # summarize based on latest snapshot per country
    latest_records = get_latest_records(records)
    
    cases_list = [record["Confirmed"] for record in latest_records]
    cases = total_field(latest_records, "Confirmed")
    deaths = total_field(latest_records, "Deaths")
    recovered = total_field(latest_records, "Recovered")
    return {
        "Countries": len(latest_records),
        "Total Confirmed": cases,
        "Total Deaths": deaths,
        "Total Recovered": recovered,
        "Total Active": total_field(latest_records, "Active"),
        "Average Cases": round(statistics.mean(cases_list), 2) if cases_list else 0,
        "Highest Cases": max(cases_list) if cases_list else 0,
        "Lowest Cases": min(cases_list) if cases_list else 0,
        "Recovery Rate": calculate_rate(recovered, cases),
        "Death Rate": calculate_rate(deaths, cases),
    }

def top_countries(records, field="Confirmed", count=3):
    latest = get_latest_records(records)
    ordered = sorted(latest, key=lambda x: x.get(field, 0), reverse=True)
    return ordered[:count]

def filter_by_country(records, country):
    found = []
    for record in records:
        if record["Country"].lower() == country.lower():
            found.append(record)
    return found

def filter_by_continent(records, continent):
    found = []
    for record in records:
        if record.get("Continent", "").lower() == continent.lower():
            found.append(record)
    return found