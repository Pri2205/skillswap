"""
db.py  -  Turso database helper (HTTP wala, koi extra install nahi chahiye)

Turso ka "pipeline" API use karta hai, isliye Windows, Linux aur Render
teeno par bina kisi dikkat ke chalta hai (sirf `requests` chahiye).
"""
import os
import requests

_session = requests.Session()


class DBError(Exception):
    """Database se kuch galat aaya."""


class UniqueError(DBError):
    """UNIQUE rule toota (jaise same email dobara)."""
    def __init__(self, message, column):
        super().__init__(message)
        self.column = column


def _endpoint():
    url = os.environ.get("TURSO_DATABASE_URL", "").strip()
    if not url:
        raise DBError("TURSO_DATABASE_URL set nahi hai (.env file check karo)")
    url = url.replace("libsql://", "https://").rstrip("/")
    return url + "/v2/pipeline"


def _arg(value):
    if value is None:
        return {"type": "null"}
    if isinstance(value, bool):
        return {"type": "integer", "value": str(int(value))}
    if isinstance(value, int):
        return {"type": "integer", "value": str(value)}
    if isinstance(value, float):
        return {"type": "float", "value": value}
    return {"type": "text", "value": str(value)}


def _cell(cell):
    kind = cell.get("type")
    if kind == "null":
        return None
    if kind == "integer":
        return int(cell["value"])
    if kind == "float":
        return float(cell["value"])
    return cell.get("value")


def execute(sql, args=()):
    """
    Ek SQL chalata hai.
    Return: {"rows": [ {column: value, ...}, ... ], "last_id": int|None, "changed": int}
    """
    token = os.environ.get("TURSO_AUTH_TOKEN", "").strip()
    body = {
        "requests": [
            {"type": "execute",
             "stmt": {"sql": sql, "args": [_arg(a) for a in args]}},
            {"type": "close"},
        ]
    }
    try:
        resp = _session.post(
            _endpoint(),
            json=body,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
    except requests.RequestException as exc:
        raise DBError(f"Database tak pahunch nahi paye: {exc}") from exc

    if resp.status_code == 401:
        raise DBError("Turso token galat hai (TURSO_AUTH_TOKEN check karo)")
    if resp.status_code != 200:
        raise DBError(f"Turso error {resp.status_code}: {resp.text[:200]}")

    first = resp.json()["results"][0]
    if first["type"] == "error":
        message = first["error"].get("message", "database error")
        if "UNIQUE constraint failed" in message:
            column = message.rsplit(".", 1)[-1].strip()
            raise UniqueError(message, column)
        raise DBError(message)

    result = first["response"]["result"]
    names = [c["name"] for c in result.get("cols", [])]
    rows = [dict(zip(names, (_cell(c) for c in row))) for row in result.get("rows", [])]
    last_id = result.get("last_insert_rowid")
    return {
        "rows": rows,
        "last_id": int(last_id) if last_id is not None else None,
        "changed": result.get("affected_row_count", 0),
    }


def one(sql, args=()):
    rows = execute(sql, args)["rows"]
    return rows[0] if rows else None


SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        name          TEXT    NOT NULL,
        email         TEXT    NOT NULL UNIQUE,
        phone         TEXT    NOT NULL UNIQUE,
        password_hash TEXT    NOT NULL,
        skillpoints   INTEGER NOT NULL DEFAULT 500,
        referral_code TEXT    NOT NULL UNIQUE,
        referred_by   INTEGER,
        created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
    )
    """,
]


def init_db():
    """Tables nahi bani to bana deta hai (baar baar chalane se kuch nahi bigadta)."""
    for statement in SCHEMA:
        execute(statement)