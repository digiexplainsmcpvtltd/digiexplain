# Digi AI Windows Desktop Companion (M1)

This first runnable Windows MVP provides a desktop interface for an encrypted, local-only knowledge vault.

## Included in this release

- Windows desktop UI built with Python Tkinter.
- Local FastAPI companion bound only to 127.0.0.1.
- Encrypted memory payloads stored in %LOCALAPPDATA%\\DigiAI\\memory.sqlite3.
- Encryption key stored through Windows Credential Manager via Python Keyring.
- Owner bearer token stored in the current Windows user's DigiAI data folder.
- Add, list, search, view, edit and delete memory from the desktop app.
- No cloud memory sync, telemetry, public listener, WhatsApp sender or email sender.

## Install and run

1. Install Python 3.11 or newer from https://www.python.org/downloads/windows/ and enable Add Python to PATH.
2. Download this repository branch or open the digi-ai/desktop-agent folder locally.
3. Double-click install.bat and wait for dependency installation.
4. Double-click DigiAI.bat to open the desktop application.

The desktop app starts the local companion automatically. On first launch an owner token is created in %LOCALAPPDATA%\\DigiAI\\owner.token. Keep this token private; never paste it into chats or commit it to Git.

## Local API

Base URL: http://127.0.0.1:8765

- GET /health — basic health only.
- POST /memory — create encrypted memory.
- GET /memory — list memories.
- GET /memory/search?q=... — local keyword search.
- PATCH /memory/{id} — update memory.
- DELETE /memory/{id} — delete memory.

All memory routes require Authorization: Bearer <owner-token>.

## What this MVP does not do yet

It does not yet read your documents automatically, watch or control the laptop screen, operate Photoshop or other Windows applications, connect Gmail/WhatsApp, send messages, or provide a live AI conversation. The dashboard's chat/voice and chatbot screens are not connected to a live AI model yet. These are subsequent milestones and will require explicit account permissions and owner-controlled approval rules.

## Security boundaries

- The local API binds to 127.0.0.1 only; do not change it to 0.0.0.0.
- Do not expose port 8765 through router port-forwarding.
- Do not put the owner token in Git, a public web page, browser localStorage or chat.
- The local app uses Windows Credential Manager for the encryption key and attempts to restrict the data directory/token file to the current Windows account and SYSTEM.
- This first release has no dashboard pairing flow yet.
- Imported or AI-generated information should be reviewed before treating it as trusted company pricing or policy.
- Sending external messages, quotations, invoices, payments, deleting records and other consequential actions must require owner approval unless a narrowly scoped automatic rule is configured later.

## Development roadmap

M1 — Local encrypted memory service and desktop memory UI.
M2 — Windows tray app, owner pairing, permission settings and emergency stop.
M3 — Local document ingestion (PDF/DOCX/XLSX/TXT) with source references and duplicate detection.
M4 — AI orchestration with tool permissions and action audit log.
M5 — Urdu speech-to-text and text-to-speech, then visible desktop screen understanding.
M6 — Gmail and WhatsApp Business adapters with separate approval/automatic policies.
M7 — Printing-company CRM, quotations, costing, production, vendors, marketing and accounts modules.
M8 — Chatbot Studio: create, test, version and publish specialist bots to approved channels.
