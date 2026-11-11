from collections.abc import Iterator
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from receipts.settings import get_settings

Conn = psycopg.Connection[dict[str, Any]]

_pool: ConnectionPool[Conn] | None = None


def get_pool() -> ConnectionPool[Conn]:
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            get_settings().database_url,
            connection_class=psycopg.Connection[dict[str, Any]],
            kwargs={"row_factory": dict_row},
            open=True,
        )
    return _pool


def get_conn() -> Iterator[Conn]:
    with get_pool().connection() as conn:
        yield conn


def connect() -> Conn:
    return psycopg.connect(get_settings().database_url, row_factory=dict_row)
