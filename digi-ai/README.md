# Digi AI — Foundation

Digi AI is the proposed AI executive assistant for Digi Explain (SMC-Private) Limited and the owner's personal productivity.

## Current milestone

This branch adds the first front-end command-centre prototype and an initial Supabase data model. It is a prototype only: the dashboard uses clearly labelled sample data and does not yet connect to live business systems.

## Product scope

- Business: leads, quotations, projects, team tasks, marketing, finance overview.
- Personal: tasks, reminders, calendar and daily briefing.
- Interfaces: responsive web first; mobile-friendly PWA next; desktop packaging and WhatsApp channel after the web MVP.
- Languages: English, Urdu and Roman Urdu.
- Automation policy: draft and recommend by default; external or consequential actions require explicit owner approval.

## Architecture

1. **Web app:** Next.js + TypeScript (production target); responsive dashboard prototype currently provided as standalone HTML.
2. **AI orchestration:** OpenAI API with tool allowlists, structured outputs, approval gates and audit trails.
3. **Data/auth:** Supabase Postgres, Auth, Storage and Row Level Security.
4. **Workflow automation:** n8n for event-driven workflows and scheduled jobs.
5. **Channels:** WhatsApp Business Cloud API, website enquiry form, Gmail and Google Calendar.
6. **Hosting:** Vercel for the web app; Supabase for data services.

## Approval rules

The agent may read authorized records, summarize, classify, draft and prepare proposed actions. It must request approval before:
- sending external messages or emails;
- publishing social content or changing ad campaigns/budgets;
- issuing or sending quotations, invoices or contracts;
- changing financial records or initiating payments;
- assigning/closing tasks that materially affect staff or clients;
- deleting records or changing access/security settings.

Every proposed action should record actor, payload, status, approver, timestamp and result in an audit log.

## Setup sequence

1. Create/connect Supabase project and apply `supabase/schema.sql`.
2. Configure environment variables from `.env.example` in the production Next.js app.
3. Deploy web app through Vercel.
4. Connect Gmail and Google Calendar after owner authorization.
5. Set up WhatsApp Business Cloud API and n8n workflows.
6. Import verified staff, service, client and project records; do not use sample dashboard values as real data.

## Next implementation milestones

- M1: dashboard prototype + database schema (this branch).
- M2: authentication, organization setup, role permissions and live dashboard.
- M3: CRM leads, follow-up queue and quotation approval workflow.
- M4: projects, employee tasks and operational reporting.
- M5: finance records and owner-only reporting.
- M6: Gmail, Calendar, WhatsApp and Meta integrations.
- M7: personal assistant, mobile/PWA and desktop packaging.

## Important

No external account is connected by this repository change. API keys, WhatsApp credentials, Meta tokens and database secrets must be stored in the hosting provider's secret manager, never committed to Git.
