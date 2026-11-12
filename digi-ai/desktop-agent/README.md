# Digi AI Windows Desktop Companion

This Windows desktop MVP includes an encrypted local Memory Vault and owner-triggered laptop document indexing.

## Included

- Windows desktop application with black and #81D100 branding.
- Local FastAPI companion bound only to 127.0.0.1.
- Encrypted memory and indexed document content stored under %LOCALAPPDATA%\DigiAI.
- Encryption key held through Windows Credential Manager.
- Add, list, search, view, edit and delete personal/company knowledge.
- Laptop Data screen: choose a folder, scan supported documents, and index locally.
- Supported file types: PDF, DOCX, XLSX, PPTX, TXT, MD, CSV, JSON, LOG, HTML and XML.
- Folder scans are owner-initiated, limited to 500 files per scan and 8 MB per file.
- No cloud upload of scanned documents.

## Run the portable Windows build

1. Download and extract the DigiAI-Windows-Portable artifact.
2. Keep DigiAI.exe and DigiAI-Service.exe together in the same folder.
3. Double-click DigiAI.exe.
4. Open Laptop Data, select a folder (for example Documents or a Digi Explain work folder), then choose folder & scan.

On first launch an owner token and encryption key are created locally. Do not share the owner token.

## Local data

- Memory database: %LOCALAPPDATA%\DigiAI\memory.sqlite3
- Owner token: %LOCALAPPDATA%\DigiAI\owner.token
- Encryption key: Windows Credential Manager

## Safety boundaries

- Only folders explicitly selected by the owner in the desktop app are scanned.
- Hidden/system folders and common developer/system directories are skipped.
- Supported files larger than 8 MB are skipped; each scan stops after 500 indexed files.
- Scanned content is encrypted before it is saved to the local database.
- The service listens only on 127.0.0.1. Do not expose port 8765 to your network or the internet.
- This release indexes documents locally; it does not yet give a live AI model access to the index, read WhatsApp/email chats, capture the screen, or control Photoshop/other apps.
- Urdu voice, WhatsApp/email integration, live AI chat, CRM/finance/production automation and chatbot publishing remain future milestones.
- Review imported information before treating it as approved company pricing or policy.

## Development

Install Python 3.12 (64-bit), run install.bat, then DigiAI.bat. The GitHub Actions workflow builds the portable Windows executables.
