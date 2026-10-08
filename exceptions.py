"""Custom exceptions for the COVID-19 Data Analyzer."""


class InvalidCOVIDDataError(Exception):
    """Raised when COVID data (date, country, numbers) is invalid."""
    pass
