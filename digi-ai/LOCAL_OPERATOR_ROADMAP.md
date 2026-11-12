# Digi AI — Personal Computer Operator Implementation Plan

## Confirmed owner configuration

- Platform: Windows 10/11.
- Memory: local-first; no cloud memory sync.
- Conversation: Urdu/Roman Urdu voice and text.
- WhatsApp and email: both approval-required and owner-configured automatic modes.
- Owner: retains a global pause/stop control and can revoke integrations.
- Brand: black with lime green #81D100.

## Product architecture

1. Existing web dashboard remains the command centre.
2. A Windows desktop companion runs locally and exposes a loopback-only authenticated API.
3. The local memory vault encrypts stored knowledge; keys are held by Windows Credential Manager.
4. An AI orchestrator plans work but can invoke only explicitly registered tools.
5. A permission engine evaluates every action before execution.
6. An audit log records proposals, approvals, executions, failures and cancellations.
7. Channel adapters connect Gmail and WhatsApp Business only after owner authorization.

## Action policy

| Action | Default policy |
|---|---|
| Read/search approved local files | Allow after folder permission |
| Summarize chats/emails | Allow after account permission |
| Draft a reply | Allow |
| Send a reply | Approval by default; automatic only for owner-defined rules |
| Create a quotation | Draft and calculate; owner approves issue/send |
| Send quotation/invoice/contract | Approval required |
| Payments, financial transfers | Never autonomous |
| Delete files or business records | Approval required |
| Install software, change security settings | Approval required |
| Screen capture / screen understanding | Visible, session-based permission |
| Emergency stop | Always available to owner |

Automatic mode is not blanket permission. It applies only to explicitly selected channels, contacts/categories, hours, message types and rate limits. Ambiguous, sensitive, financial, legal or high-impact messages are escalated.

## Delivery sequence

- M1 — Local encrypted memory service and Windows companion foundation.
- M2 — Windows tray app, owner pairing, permission settings and emergency stop.
- M3 — Local file indexing with source references and review workflow.
- M4 — AI command planner, allowlisted Windows/browser tools and audit log.
- M5 — Urdu voice interface and spoken confirmations.
- M6 — Gmail + WhatsApp Business adapters; approval queue and constrained automatic rules.
- M7 — Printing-company CRM, quotations, costing, production, vendors, marketing and accounts modules.
- M8 — Chatbot Studio: create, test, version and publish specialist bots to approved channels.

## Release gate

No feature is labelled live until it has been implemented, tested on Windows, and connected to the actual account/service. Sample data and simulated actions must remain visibly marked as demos.
