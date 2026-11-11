from collections.abc import Iterator

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from receipts.settings import get_settings

_pool: ConnectionPool | None = None


def get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            get_settings().database_url,
            kwargs={"row_factory": dict_row},
            open=True,
        )
    return _pool


def get_conn() -> Iterator[psycopg.Connection]:
    with get_pool().connection() as conn:
        yield conn
