import pytest

from app.config import normalise_database_url, normalise_origin


@pytest.mark.parametrize("given,expected", [
    ("postgres://u:p@h:5432/db", "postgresql+psycopg://u:p@h:5432/db"),
    ("postgresql://u:p@h:5432/db", "postgresql+psycopg://u:p@h:5432/db"),
    ("postgresql+psycopg://u:p@h:5432/db", "postgresql+psycopg://u:p@h:5432/db"),
    ("sqlite:///./catalog.db", "sqlite:///./catalog.db"),
])
def test_database_url_ends_up_on_the_psycopg_driver(given, expected):
    assert normalise_database_url(given) == expected


def test_a_password_containing_the_scheme_is_not_mangled():
    given = "postgres://u:postgres://x@h:5432/db"
    assert normalise_database_url(given) == "postgresql+psycopg://u:postgres://x@h:5432/db"


@pytest.mark.parametrize("given,expected", [
    ("app.onrender.com", "https://app.onrender.com"),
    ("https://app.onrender.com", "https://app.onrender.com"),
    ("https://app.onrender.com/", "https://app.onrender.com"),
    ("http://localhost:5173", "http://localhost:5173"),
    ("  app.onrender.com  ", "https://app.onrender.com"),
    ("", ""),
])
def test_bare_hosts_become_https_origins(given, expected):
    assert normalise_origin(given) == expected
