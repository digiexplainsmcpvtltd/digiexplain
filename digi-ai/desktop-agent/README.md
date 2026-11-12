# Digi AI Windows Local Companion (M1)

This is the first local-only memory service for the Windows desktop companion.

## What this milestone provides

- A local FastAPI service bound only to 127.0.0.1.
- Encrypted memory payloads stored in %LOCALAPPDATA%\DigiAI\memory.sqlite3.
- The encryption key stored through Windows Credential Manager via Python Keyring.
- A random owner bearer token stored in the current Windows user's DigiAI data folder.
- Owner-authenticated create, list, search, update and delete memory endpoints.
- No cloud database, telemetry, public listener, WhatsApp sender or email sender.

## Windows setup

1. Install Python 3.11 or newer.
2. Open PowerShell in this folder.
3. Create and activate a virtual environment:

   py -3 -m venv .venv

   .\.venv\Scripts\Activate.ps1

4. Install dependencies:

   pip install -r requirements.txt

5. Start the local companion:

   python agent.py

On first launch, copy the owner token printed in the terminal and keep it private. The token is also saved under %LOCALAPPDATA%\DigiAI\owner.token; the folder/file ACL is restricted to the current Windows account and SYSTEM where icacls is available.

## Local API

Base URL: http://127.0.0.1:8765

- GET /health — basic health only.
- POST /memory — create an encrypted memory.
- GET /memory — list memories.
- GET /memory/search?q=... — local keyword search.
- PATCH /memory/{id} — update a memory.
- DELETE /memory/{id} — delete a memory.

All memory routes require Authorization: Bearer <owner-token>.

## Security boundaries

- Do not bind this service to 0.0.0.0.
- Do not expose port 8765 through router port-forwarding.
- Do not place the owner token in Git, a public web page, browser localStorage, or chat.
- The dashboard must use a deliberate local pairing flow before calling this service. Do not add permissive wildcard CORS.
- This service stores memory locally; it does not yet read the user's documents or control Windows applications.
- AI-generated or imported knowledge should be labelled with its source and reviewed before it becomes trusted company policy or pricing.
- Outbound messages, quotation delivery, payments, deletion of business records and other consequential actions must remain behind owner approval unless a specific safe routine is explicitly allowlisted.

## Next milestones

M2: Windows tray app, local pairing UX, signed command allowlist, stop/pause control.
M3: local document ingestion (PDF/DOCX/XLSX/TXT) with source citations and duplicate detection.
M4: AI orchestration with tool permissions and action audit log.
M5: Urdu speech-to-text and text-to-speech, then desktop screen understanding.
M6: Gmail and WhatsApp Business integrations with separate approval/automatic policies.
