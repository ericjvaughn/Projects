-- Enable necessary extensions
create extension if not exists "uuid-ossp";
create extension if not exists "pgcrypto";

-- Channels table
create table public.channels (
    id uuid default uuid_generate_v4() primary key,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    name text not null,
    metadata jsonb default '{}'::jsonb,
    is_active boolean default true
);

-- Messages table
create table public.messages (
    id uuid default uuid_generate_v4() primary key,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    content text not null,
    channel_id uuid references public.channels(id) on delete cascade,
    user_id uuid references auth.users(id) on delete set null,
    agent_mention text,
    response_content text,
    response_agent text,
    confidence numeric(4,3),
    metadata jsonb default '{}'::jsonb,
    status text default 'pending'
);

-- Agents table
create table public.agents (
    id uuid default uuid_generate_v4() primary key,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    name text not null unique,
    description text,
    status text default 'active',
    capabilities jsonb default '{}'::jsonb,
    metadata jsonb default '{}'::jsonb
);

-- Session context table
create table public.session_contexts (
    id uuid default uuid_generate_v4() primary key,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    channel_id uuid references public.channels(id) on delete cascade,
    context_data jsonb default '{}'::jsonb,
    expires_at timestamp with time zone
);

-- Create indexes
create index messages_channel_id_idx on public.messages(channel_id);
create index messages_user_id_idx on public.messages(user_id);
create index messages_created_at_idx on public.messages(created_at);
create index session_contexts_channel_id_idx on public.session_contexts(channel_id);
create index agents_name_idx on public.agents(name);

-- Enable Row Level Security (RLS)
alter table public.channels enable row level security;
alter table public.messages enable row level security;
alter table public.agents enable row level security;
alter table public.session_contexts enable row level security;

-- Policies
-- Channels
create policy "Channels are viewable by authenticated users"
    on public.channels for select
    to authenticated
    using (true);

create policy "Channels are insertable by authenticated users"
    on public.channels for insert
    to authenticated
    with check (true);

-- Messages
create policy "Messages are viewable by authenticated users"
    on public.messages for select
    to authenticated
    using (true);

create policy "Messages are insertable by authenticated users"
    on public.messages for insert
    to authenticated
    with check (true);

-- Agents
create policy "Agents are viewable by authenticated users"
    on public.agents for select
    to authenticated
    using (true);

create policy "Agents are updatable by service role only"
    on public.agents for update
    using (auth.role() = 'service_role');

-- Session contexts
create policy "Session contexts are viewable by authenticated users"
    on public.session_contexts for select
    to authenticated
    using (true);

-- Functions
-- Update updated_at timestamp
create or replace function public.handle_updated_at()
returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

-- Create triggers
create trigger handle_updated_at
    before update on public.channels
    for each row
    execute function public.handle_updated_at();

create trigger handle_updated_at
    before update on public.messages
    for each row
    execute function public.handle_updated_at();

create trigger handle_updated_at
    before update on public.agents
    for each row
    execute function public.handle_updated_at();

create trigger handle_updated_at
    before update on public.session_contexts
    for each row
    execute function public.handle_updated_at();
