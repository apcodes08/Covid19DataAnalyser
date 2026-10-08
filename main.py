"""COVID-19 Data Analyzer - main menu and user interaction.
Run with:  python main.py
"""

from datetime import datetime

import analyzer
import file_utils
import validators
from exceptions import InvalidCOVIDDataError

MENU = """
========================================
       COVID-19 DATA ANALYZER
========================================
1. View COVID Data
2. Add COVID Record
3. Search Data
4. Validate Data
5. Analyze Country
6. Analyze Continent
7. Generate Summary Report
8. Backup Data
9. Restore Backup
10. Copy Data File
11. Merge Data Files
0. Exit
"""


def load_records():
    try:
        return file_utils.read_records()
    except FileNotFoundError:
        print("Data file not found!")
    except InvalidCOVIDDataError as error:
        print(f"Invalid data: {error}")
    return []


def print_table(records):
    print(f"\n{'Date':<12}{'Country':<15}{'Continent':<15}{'Confirmed':>10}{'Deaths':>9}{'Recovered':>11}{'Active':>10}")
    print("-" * 88)
    for r in records:
        print(f"{r.get('Date', ''):<12}{r['Country']:<15}{r.get('Continent', 'Unknown'):<15}{r.get('Confirmed',0):>10,}{r.get('Deaths',0):>9,}"
              f"{r.get('Recovered',0):>11,}{r.get('Active',0):>10,}")
    print(f"\nRecords shown:\t{len(records)}")


def show_stats(title, stats):
    print(f"\n--- {title} ---")
    for label, value in stats.items():
        if "Rate" in label:
            print(f"{label:<20}: {value}%")
        elif isinstance(value, int):
            print(f"{label:<20}: {value:,}")
        else:
            print(f"{label:<20}: {value}")


# 1. VIEW
def view_data():
    records = load_records()
    if len(records) == 0:
        print("No records to show.")
        return
    print("Data summary:")
    print_table(records)
    print(f"Lines in file (with header): {file_utils.count_lines()}")


# 2. ADD
def add_record():
    print("\n--- Add COVID Record ---")
    try:
        date = validators.validate_date(input("Date (YYYY-MM-DD): "))
        country = validators.validate_country(input("Country: "))
        confirmed = validators.validate_number(input("Confirmed: "), "Confirmed")
        new_cases = validators.validate_number(input("New Cases: "), "New Cases")
        recovered = validators.validate_number(input("Recovered: "), "Recovered")
        deaths = validators.validate_number(input("Deaths: "), "Deaths")
        active = validators.validate_number(input("Active: "), "Active")
        record = analyzer.make_record(date=date, country=country, confirmed=confirmed, new_cases=new_cases,
                                      recovered=recovered, deaths=deaths, active=active)
        validators.validate_record(record)
    except InvalidCOVIDDataError as error:
        print(f"Invalid data: {error}")
    else:
        file_utils.append_record(record)
        print(f"Record saved! Active cases = {record['Active']:,}")
    finally:
        print("--- Add record finished ---")


# 3. SEARCH
def search_data():
    records = load_records()
    print("\n1. Country (full or partial name)\n2. Continent\n3. Regex search on country")
    choice = input("Choose search type: ").strip()
    found = []

    if choice == "1":
        term = input("Country name: ").strip().lower()
        if term == "":
            print("Nothing entered.")
            return
        for record in records:
            name = record["Country"].lower()
            if term == name:
                found.append(record)
                print(f"  {record['Country']:<15} exact match")
            elif name[:len(term)] == term:
                found.append(record)
                print(f"  {record['Country']:<15} starts with '{term}'")
            elif term in name:
                found.append(record)
                print(f"  {record['Country']:<15} contains '{term}'")
    elif choice == "2":
        term = input("Continent: ").strip().lower()
        for record in records:
            if term != "" and term in record.get("Continent", "").lower():
                found.append(record)
    elif choice == "3":
        pattern = input("Regex pattern (e.g. ^[UB], ia$, ind): ").strip()
        try:
            results = validators.regex_search_country(records, pattern)
        except InvalidCOVIDDataError as error:
            print(f"Invalid data: {error}")
            return
        for record, match in results:
            found.append(record)
            print(f"{validators.highlight(pattern, record['Country']):<15} "
                  f"match.group()='{match.group()}'  match.span()={match.span()}")
    else:
        print("Invalid search type.")
        return

    if len(found) == 0:
        print("No matching records.")
    else:
        print_table(found)


# 4. VALIDATE
def validate_data():
    records = load_records()
    print("\n--- Validate Data ---")
    valid = 0
    invalid = 0
    for record in records:
        try:
            validators.validate_record(record)
        except InvalidCOVIDDataError as error:
            print(f"Invalid: {record['Country']} ({record.get('Date')}) -> {error}")
            invalid += 1
            continue
        valid += 1
    print(f"Valid records: {valid} | Invalid records: {invalid}")

    text = input("\nType a date to test (YYYY-MM-DD): ").strip()
    if text:
        try:
            validators.validate_date(text)
            year, month, day = validators.split_date(text)
            print(f"Valid date! Year={year}, Month={month}, Day={day}")
        except InvalidCOVIDDataError as error:
            print(f"Invalid data: {error}")

    name = input("Type a country to test: ")
    try:
        print(f"Valid country -> '{validators.validate_country(name)}'")
    except InvalidCOVIDDataError as error:
        print(f"Invalid data: {error}")


# 5. COUNTRY ANALYSIS
def analyze_country():
    records = load_records()
    try:
        country = validators.validate_country(input("\nEnter country: "))
    except InvalidCOVIDDataError as error:
        print(f"Invalid data: {error}")
        return
    subset = analyzer.filter_by_country(records, country)
    if len(subset) == 0:
        print(f"No records found for {country}.")
        return
    latest = analyzer.get_latest_records(subset)
    if not latest:
        return
    r = latest[0]
    
    latest_all = analyzer.get_latest_records(records)
    world_cases = analyzer.total_field(latest_all, "Confirmed")
    
    print(f"\n--- Country: {r['Country']} ({r['Country'][:3].upper()}) [Latest: {r['Date']}] ---")
    print(f"Continent           : {r.get('Continent', 'Unknown')}")
    print(f"Total Confirmed     : {r['Confirmed']:,}")
    print(f"Total Deaths        : {r['Deaths']:,}")
    print(f"Total Recovered     : {r['Recovered']:,}")
    print(f"Total Active        : {r['Active']:,}")
    print(f"Recovery Rate       : {analyzer.calculate_rate(r['Recovered'], r['Confirmed'])}%")
    print(f"Death Rate          : {analyzer.calculate_rate(r['Deaths'], r['Confirmed'])}%")
    print(f"Share of All Cases  : {analyzer.calculate_rate(r['Confirmed'], world_cases)}%")


# 6. CONTINENT ANALYSIS
def analyze_continent():
    records = load_records()
    try:
        continent = validators.validate_continent(input("\nEnter continent: "))
    except InvalidCOVIDDataError as error:
        print(f"Invalid data: {error}")
        return
    subset = analyzer.filter_by_continent(records, continent)
    if len(subset) == 0:
        print(f"No records found for {continent}.")
        return
    show_stats(f"Continent: {continent}", analyzer.summarize(subset))
    print("\nTop 3 countries by total confirmed:")
    print_table(analyzer.top_countries(subset, "Confirmed", 3))


# 7. SUMMARY REPORT
def summary_report():
    records = load_records()
    stats = analyzer.summarize(records)
    if stats is None:
        print("No data to summarize.")
        return
    print(f"\nReport generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    show_stats("OVERALL SUMMARY (all countries - latest snapshots)", stats)

    print(f"\n{'Continent':<15}{'Countries':>10}{'Confirmed':>12}{'Deaths':>10}{'Recovery%':>11}{'Death%':>8}")
    continents = sorted({record.get("Continent", "Unknown") for record in records})
    for continent in continents:
        sub = analyzer.filter_by_continent(records, continent)
        s = analyzer.summarize(sub)
        print(f"{continent:<15}{s['Countries']:>10}{s['Total Confirmed']:>12,}{s['Total Deaths']:>10,}"
              f"{s['Recovery Rate']:>11}{s['Death Rate']:>8}")

    print("\nTop 3 countries by total confirmed (sorted with lambda):")
    print_table(analyzer.top_countries(records, "Confirmed", 3))
    print("Top 3 countries by deaths:")
    print_table(analyzer.top_countries(records, "Deaths", 3))


# 8-11. FILE OPERATIONS
def backup():
    records = load_records()
    file_utils.backup_data(records)
    print(f"Backup created: {len(records)} records saved to data/backup.dat")


def restore():
    try:
        records = file_utils.restore_backup()
    except FileNotFoundError:
        print("No backup found. Use option 8 first.")
    else:
        file_utils.save_all(records)
        print(f"Restored {len(records)} records into covid_data.csv")


def copy_data():
    try:
        size = file_utils.copy_file()
    except FileNotFoundError:
        print("Source file not found!")
    else:
        print(f"Copied covid_data.csv -> copy.csv ({size} bytes)")


def merge_data():
    first = input("\nFirst file [covid_data.csv]: ").strip() or "covid_data.csv"
    second = input("Second file [extra_data.csv]: ").strip() or "extra_data.csv"
    try:
        count = file_utils.merge_files(file_utils.DATA_DIR / first, file_utils.DATA_DIR / second)
    except FileNotFoundError as error:
        print(error)
    else:
        print(f"Merged {count} unique records into data/merged.csv (one header)")


def main():
    file_utils.ensure_sample_data()
    while True:
        print(MENU)
        choice = input("Enter your choice: ").strip()
        if choice == "0":
            print(".....EXITED.....")
            break
        elif choice == "1":
            view_data()
        elif choice == "2":
            add_record()
        elif choice == "3":
            search_data()
        elif choice == "4":
            validate_data()
        elif choice == "5":
            analyze_country()
        elif choice == "6":
            analyze_continent()
        elif choice == "7":
            summary_report()
        elif choice == "8":
            backup()
        elif choice == "9":
            restore()
        elif choice == "10":
            copy_data()
        elif choice == "11":
            merge_data()
        else:
            print("Invalid choice! Please enter a number from 0 to 11.")
            continue
        # Pause omitted for script testing if ran without a tty, but keeping input for actual interactive use
        try:
            input("\nPress Enter to continue...")
        except EOFError:
            break


if __name__ == "__main__":
    main()