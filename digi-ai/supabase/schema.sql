-- Digi AI initial schema. Apply to a fresh Supabase project.
-- All business tables are scoped to an organization and protected by RLS.

create extension if not exists pgcrypto;

create table if not exists public.organizations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  created_at timestamptz not null default now()
);

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  organization_id uuid not null references public.organizations(id) on delete restrict,
  full_name text,
  role text not null default 'member' check (role in ('owner','admin','manager','member')),
  created_at timestamptz not null default now()
);

create table if not exists public.contacts (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references public.organizations(id) on delete cascade,
  name text not null,
  company text,
  email text,
  phone text,
  city text,
  source text,
  created_at timestamptz not null default now()
);

create table if not exists public.leads (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references public.organizations(id) on delete cascade,
  contact_id uuid references public.contacts(id) on delete set null,
  service text,
  estimated_value numeric(14,2),
  currency text not null default 'PKR',
  status text not null default 'new' check (status in ('new','contacted','qualified','quotation_pending','quotation_sent','won','lost')),
  next_follow_up_at timestamptz,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.projects (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references public.organizations(id) on delete cascade,
  lead_id uuid references public.leads(id) on delete set null,
  name text not null,
  service text,
  status text not null default 'planned' check (status in ('planned','in_progress','blocked','completed','cancelled')),
  start_date date,
  due_date date,
  budget numeric(14,2),
  currency text not null default 'PKR',
  created_at timestamptz not null default now()
);

create table if not exists public.tasks (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references public.organizations(id) on delete cascade,
  project_id uuid references public.projects(id) on delete cascade,
  title text not null,
  description text,
  assigned_to uuid references public.profiles(id) on delete set null,
  due_at timestamptz,
  status text not null default 'todo' check (status in ('todo','in_progress','blocked','done')),
  created_at timestamptz not null default now()
);

create table if not exists public.expenses (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references public.organizations(id) on delete cascade,
  description text not null,
  category text,
  amount numeric(14,2) not null check (amount >= 0),
  currency text not null default 'PKR',
  incurred_on date not null default current_date,
  created_by uuid references public.profiles(id) on delete set null,
  created_at timestamptz not null default now()
);

create table if not exists public.approvals (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references public.organizations(id) on delete cascade,
  action_type text not null,
  title text not null,
  payload jsonb not null default '{}'::jsonb,
  status text not null default 'pending' check (status in ('pending','approved','rejected','executed','failed','cancelled')),
  requested_by uuid references public.profiles(id) on delete set null,
  reviewed_by uuid references public.profiles(id) on delete set null,
  reviewed_at timestamptz,
  executed_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.audit_logs (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references public.organizations(id) on delete cascade,
  actor_id uuid references public.profiles(id) on delete set null,
  event_type text not null,
  entity_type text,
  entity_id uuid,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists leads_org_status_idx on public.leads(organization_id, status);
create index if not exists leads_followup_idx on public.leads(organization_id, next_follow_up_at);
create index if not exists tasks_org_due_idx on public.tasks(organization_id, due_at);
create index if not exists approvals_org_status_idx on public.approvals(organization_id, status);

-- Organization membership helper: the signed-in user can only see their own organization.
create or replace function public.current_user_org_id()
returns uuid
language sql
stable
security definer
set search_path = public
as $$
  select organization_id from public.profiles where id = auth.uid() limit 1;
$$;

alter table public.organizations enable row level security;
alter table public.profiles enable row level security;
alter table public.contacts enable row level security;
alter table public.leads enable row level security;
alter table public.projects enable row level security;
alter table public.tasks enable row level security;
alter table public.expenses enable row level security;
alter table public.approvals enable row level security;
alter table public.audit_logs enable row level security;

create policy "members read own organization" on public.organizations
for select using (id = public.current_user_org_id());

create policy "members read organization profiles" on public.profiles
for select using (organization_id = public.current_user_org_id());
create policy "users update own profile" on public.profiles
for update using (id = auth.uid()) with check (id = auth.uid());

create policy "organization access contacts" on public.contacts
for all using (organization_id = public.current_user_org_id())
with check (organization_id = public.current_user_org_id());
create policy "organization access leads" on public.leads
for all using (organization_id = public.current_user_org_id())
with check (organization_id = public.current_user_org_id());
create policy "organization access projects" on public.projects
for all using (organization_id = public.current_user_org_id())
with check (organization_id = public.current_user_org_id());
create policy "organization access tasks" on public.tasks
for all using (organization_id = public.current_user_org_id())
with check (organization_id = public.current_user_org_id());
create policy "organization access expenses" on public.expenses
for all using (organization_id = public.current_user_org_id())
with check (organization_id = public.current_user_org_id());
create policy "organization access approvals" on public.approvals
for all using (organization_id = public.current_user_org_id())
with check (organization_id = public.current_user_org_id());
create policy "organization access audit logs" on public.audit_logs
for select using (organization_id = public.current_user_org_id());

-- Production hardening still required before onboarding:
-- 1) Add role-aware policies for owner/admin-only financial and approval actions.
-- 2) Restrict approval status transitions to a server-side function.
-- 3) Add updated_at triggers and immutable audit-log insertion via server-side code.
-- 4) Never expose the service-role key to browser clients.
