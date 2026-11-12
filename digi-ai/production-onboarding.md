# Digi AI production onboarding configuration

This file intentionally excludes phone numbers, email addresses, API keys, OAuth tokens, and other private credentials. Store those only in the approved secret manager / provider settings.

## Owner-provided choices

- Product: Digi AI
- Scope: Digi Explain business + owner's personal productivity
- Initial access model: Owner + Managers
- Automation: approval required for consequential external actions
- Preferred hosting URL: subdomain of the company's existing domain
- WhatsApp channel: Business number supplied by owner; register/configure it in WhatsApp Business Platform and store credentials only in server-side secrets.

## Proposed host name

Proposed URL: `ai.digiexplain.com`

This is a proposed hostname only. Before attaching it, confirm that the company controls the parent domain `digiexplain.com` and can edit its DNS records. No DNS change has been made.

## Initial access policy

- Owner: full access, including finance, approvals, user management, integrations and audit logs.
- Managers: access only to assigned operational modules (CRM, projects, tasks and approved reporting); no owner-only security settings or unrestricted finance/payment permissions by default.
- No employee accounts are provisioned until the owner supplies manager identities and confirms module permissions.
- Personal workspace records are private to the owner unless explicitly shared.

## Approval policy

Require explicit owner approval before sending WhatsApp messages or emails, issuing quotations/invoices/contracts, publishing content, changing advertising budgets, modifying financial records, initiating payments, deleting data, or changing security/access settings.

## Deployment blockers / prerequisites

1. Vercel connection currently returns no accessible teams; select/authorize the intended Vercel team or personal workspace before project creation.
2. Supabase project connection and database provisioning are still required. Apply `supabase/schema.sql` only after reviewing the target project and migration plan.
3. Confirm the parent domain and DNS access before attaching the proposed subdomain.
4. Configure WhatsApp Business Platform, including business verification/phone registration as required by Meta. Keep access tokens server-side.
5. Confirm manager names, work email addresses, and permissions before issuing invitations.
6. Set production secrets in Vercel/Supabase secret settings. Never commit real credentials to Git.

## Current status

The GitHub branch contains a dashboard prototype and initial schema. It is not yet an authenticated or production-ready application. No external messages, domain changes, payments, or deployments have been executed as part of this configuration.
