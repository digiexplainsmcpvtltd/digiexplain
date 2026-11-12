from __future__ import annotations

import json
import os
import secrets
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import keyring
from cryptography.fernet import Fernet, InvalidToken
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field

SERVICE_NAME = "DigiAI-Local-Agent"
KEY_NAME = "memory-encryption-key"
APP_NAME = "DigiAI"
DATA_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / APP_NAME
DB_PATH = DATA_DIR / "memory.sqlite3"
TOKEN_PATH = DATA_DIR / "owner.token"
HOST = "127.0.0.1"
PORT = int(os.environ.get("DIGI_AI_LOCAL_PORT", "8765"))

app = FastAPI(title="Digi AI Local Companion", version="0.1.0", docs_url=None, redoc_url=None)


def secure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        username = os.environ.get("USERNAME")
        if username:
            subprocess.run(
                ["icacls", str(DATA_DIR), "/inheritance:r", "/grant:r",
                 f"{username}:(OI)(CI)F", "SYSTEM:(OI)(CI)F"],
                capture_output=True, check=False,
            )
    else:
        DATA_DIR.chmod(0o700)


def get_cipher() -> Fernet:
    secure_data_dir()
    key = keyring.get_password(SERVICE_NAME, KEY_NAME)
    if not key:
        key = Fernet.generate_key().decode("ascii")
        keyring.set_password(SERVICE_NAME, KEY_NAME, key)
    return Fernet(key.encode("ascii"))


def get_owner_token() -> str:
    secure_data_dir()
    if TOKEN_PATH.exists():
        return TOKEN_PATH.read_text(encoding="utf-8").strip()
    token = secrets.token_urlsafe(48)
    TOKEN_PATH.write_text(token, encoding="utf-8")
    if os.name == "nt":
        username = os.environ.get("USERNAME")
        if username:
            subprocess.run(
                ["icacls", str(TOKEN_PATH), "/inheritance:r", "/grant:r",
                 f"{username}:F", "SYSTEM:F"],
                capture_output=True, check=False,
            )
    else:
        TOKEN_PATH.chmod(0o600)
    print("\nDigi AI owner token (shown once; keep it private):\n" + token + "\n")
    print(f"Token file: {TOKEN_PATH}")
    return token


def db() -> sqlite3.Connection:
    secure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            encrypted_payload BLOB NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS memories_updated_idx ON memories(updated_at)")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS laptop_files (
            id TEXT PRIMARY KEY,
            encrypted_payload BLOB NOT NULL,
            path_hash TEXT NOT NULL UNIQUE,
            indexed_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


class MemoryCreate(BaseModel):
    title: str = Field(min_length=1, max_length=180)
    content: str = Field(min_length=1, max_length=30000)
    category: str = Field(default="general", max_length=60)
    tags: list[str] = Field(default_factory=list, max_length=30)


class MemoryUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=180)
    content: str | None = Field(default=None, min_length=1, max_length=30000)
    category: str | None = Field(default=None, max_length=60)
    tags: list[str] | None = Field(default=None, max_length=30)


def require_owner(authorization: str | None = Header(default=None)) -> None:
    expected = get_owner_token()
    if not authorization or not secrets.compare_digest(authorization, f"Bearer {expected}"):
        raise HTTPException(status_code=401, detail="Owner authentication required")


def decrypt_payload(row: sqlite3.Row) -> dict[str, Any]:
    try:
        raw = get_cipher().decrypt(row["encrypted_payload"])
        return json.loads(raw.decode("utf-8"))
    except (InvalidToken, ValueError, json.JSONDecodeError):
        raise HTTPException(status_code=500, detail="Memory record could not be decrypted")


@app.on_event("startup")
def startup() -> None:
    get_cipher()
    get_owner_token()
    db().close()



class LaptopScanRequest(BaseModel):
    folder: str = Field(min_length=1, max_length=2000)


def extract_document_text(path: Path) -> str:
    suffix = path.suffix.lower()
    try:
        if suffix in {".txt", ".md", ".csv", ".json", ".log", ".html", ".htm", ".xml"}:
            return path.read_text(encoding="utf-8", errors="replace")[:30000]
        if suffix == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            return "\n".join((page.extract_text() or "") for page in reader.pages[:40])[:30000]
        if suffix == ".docx":
            from docx import Document
            return "\n".join(p.text for p in Document(str(path)).paragraphs)[:30000]
        if suffix == ".xlsx":
            from openpyxl import load_workbook
            wb = load_workbook(path, read_only=True, data_only=True)
            lines = []
            for ws in wb.worksheets[:10]:
                lines.append("[Sheet: " + ws.title + "]")
                for row in ws.iter_rows(max_row=300, values_only=True):
                    line = " | ".join(str(v) for v in row if v is not None)
                    if line:
                        lines.append(line)
            wb.close()
            return "\n".join(lines)[:30000]
        if suffix == ".pptx":
            from pptx import Presentation
            prs = Presentation(str(path))
            return "\n".join(shape.text for slide in prs.slides[:50]
                             for shape in slide.shapes if hasattr(shape, "text"))[:30000]
    except Exception as exc:
        return "[Could not extract document text: " + type(exc).__name__ + "]"
    return ""


@app.post("/computer/scan", dependencies=[Depends(require_owner)])
def scan_laptop_folder(request: LaptopScanRequest) -> dict[str, Any]:
    root = Path(request.folder).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise HTTPException(status_code=400, detail="Selected folder does not exist")
    allowed = {".txt", ".md", ".csv", ".json", ".log", ".html", ".htm", ".xml",
               ".pdf", ".docx", ".xlsx", ".pptx"}
    ignored = {"AppData", "Windows", "Program Files", "Program Files (x86)",
               "$Recycle.Bin", "System Volume Information", ".git", "node_modules"}
    now = datetime.now(timezone.utc).isoformat()
    indexed = skipped = 0
    import hashlib
    with db() as conn:
        for current, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in ignored and not d.startswith(".")]
            for filename in files:
                path = Path(current) / filename
                if path.suffix.lower() not in allowed:
                    skipped += 1
                    continue
                try:
                    if path.is_symlink() or path.stat().st_size > 8 * 1024 * 1024:
                        skipped += 1
                        continue
                    stat = path.stat()
                    payload = {"name": path.name, "path": str(path), "extension": path.suffix.lower(),
                               "size_bytes": stat.st_size,
                               "modified_at": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                               "content": extract_document_text(path)}
                    path_hash = hashlib.sha256(str(path).casefold().encode("utf-8")).hexdigest()
                    encrypted = get_cipher().encrypt(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
                    conn.execute("""
                        INSERT INTO laptop_files(id, encrypted_payload, path_hash, indexed_at)
                        VALUES(?,?,?,?)
                        ON CONFLICT(path_hash) DO UPDATE SET
                        encrypted_payload=excluded.encrypted_payload, indexed_at=excluded.indexed_at
                    """, (secrets.token_hex(16), encrypted, path_hash, now))
                    indexed += 1
                    if indexed >= 500:
                        break
                except OSError:
                    skipped += 1
            if indexed >= 500:
                break
    return {"status": "indexed", "folder": str(root), "indexed": indexed,
            "skipped": skipped, "limit": 500, "storage": "local-encrypted"}


@app.get("/computer/files", dependencies=[Depends(require_owner)])
def list_laptop_files(q: str = Query(default="", max_length=300)) -> dict[str, Any]:
    with db() as conn:
        rows = conn.execute("SELECT * FROM laptop_files ORDER BY indexed_at DESC LIMIT 500").fetchall()
    items, needle = [], q.casefold().strip()
    for row in rows:
        try:
            payload = json.loads(get_cipher().decrypt(row["encrypted_payload"]).decode("utf-8"))
        except Exception:
            continue
        haystack = (payload.get("name", "") + " " + payload.get("path", "") + " " +
                    payload.get("content", "")).casefold()
        if not needle or needle in haystack:
            items.append({k: payload.get(k) for k in
                          ("name", "path", "extension", "size_bytes", "modified_at")})
    return {"items": items, "count": len(items), "storage": "local-encrypted"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "online", "service": "Digi AI Local Companion", "storage": "local-encrypted"}


@app.get("/owner/setup-status")
def setup_status() -> dict[str, str]:
    return {"status": "owner-token-created", "token_file": str(TOKEN_PATH)}


@app.post("/memory", dependencies=[Depends(require_owner)])
def create_memory(item: MemoryCreate) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    memory_id = secrets.token_hex(16)
    payload = item.model_dump()
    encrypted = get_cipher().encrypt(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
    with db() as conn:
        conn.execute(
            "INSERT INTO memories(id, encrypted_payload, created_at, updated_at) VALUES(?,?,?,?)",
            (memory_id, encrypted, now, now),
        )
    return {"id": memory_id, **payload, "created_at": now, "updated_at": now}


@app.get("/memory", dependencies=[Depends(require_owner)])
def list_memories(limit: int = Query(default=100, ge=1, le=500)) -> dict[str, Any]:
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM memories ORDER BY updated_at DESC LIMIT ?", (limit,)
        ).fetchall()
    items = [
        {"id": row["id"], **decrypt_payload(row),
         "created_at": row["created_at"], "updated_at": row["updated_at"]}
        for row in rows
    ]
    return {"items": items, "count": len(items), "storage": "local-encrypted"}


@app.get("/memory/search", dependencies=[Depends(require_owner)])
def search_memories(q: str = Query(min_length=1, max_length=300)) -> dict[str, Any]:
    needle = q.casefold()
    matches = []
    with db() as conn:
        rows = conn.execute("SELECT * FROM memories ORDER BY updated_at DESC").fetchall()
    for row in rows:
        payload = decrypt_payload(row)
        haystack = " ".join([
            payload.get("title", ""), payload.get("content", ""),
            payload.get("category", ""), " ".join(payload.get("tags", []))
        ]).casefold()
        if needle in haystack:
            matches.append({"id": row["id"], **payload,
                            "created_at": row["created_at"], "updated_at": row["updated_at"]})
    return {"items": matches, "count": len(matches), "query": q}


@app.patch("/memory/{memory_id}", dependencies=[Depends(require_owner)])
def update_memory(memory_id: str, patch: MemoryUpdate) -> dict[str, Any]:
    with db() as conn:
        row = conn.execute("SELECT * FROM memories WHERE id=?", (memory_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Memory not found")
        payload = decrypt_payload(row)
        payload.update({k: v for k, v in patch.model_dump(exclude_unset=True).items() if v is not None})
        now = datetime.now(timezone.utc).isoformat()
        encrypted = get_cipher().encrypt(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
        conn.execute("UPDATE memories SET encrypted_payload=?, updated_at=? WHERE id=?",
                     (encrypted, now, memory_id))
    return {"id": memory_id, **payload, "created_at": row["created_at"], "updated_at": now}


@app.delete("/memory/{memory_id}", dependencies=[Depends(require_owner)])
def delete_memory(memory_id: str) -> dict[str, str]:
    with db() as conn:
        cur = conn.execute("DELETE FROM memories WHERE id=?", (memory_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Memory not found")
    return {"status": "deleted", "id": memory_id}


if __name__ == "__main__":
    import uvicorn
    # Loopback-only: never expose this companion to the LAN or public internet.
    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
