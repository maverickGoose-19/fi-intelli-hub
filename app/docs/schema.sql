create table sources (
  id text primary key,
  name text not null,
  kind text not null,
  reliability_tier text not null,
  base_url text not null
);

create table entities (
  id text primary key,
  name text not null,
  kind text not null,
  slug text not null unique
);

create table weekends (
  id text primary key,
  name text not null,
  slug text not null unique,
  circuit_entity_id text not null references entities(id),
  season integer not null,
  current boolean not null default false,
  stage text not null,
  started_at timestamptz not null,
  ended_at timestamptz not null
);

create table weekend_phases (
  id bigserial primary key,
  weekend_id text not null references weekends(id),
  phase text not null,
  state text not null,
  headline text not null,
  focus text not null,
  display_order integer not null
);

create table documents (
  id text primary key,
  source_id text not null references sources(id),
  weekend_id text not null references weekends(id),
  title text not null,
  url text not null,
  kind text not null,
  publish_time timestamptz not null,
  race_stage text not null,
  stance text not null,
  cluster_hint text,
  content text not null
);

create table entities_documents (
  entity_id text not null references entities(id),
  document_id text not null references documents(id),
  primary key (entity_id, document_id)
);

create table clusters (
  id text primary key,
  weekend_id text not null references weekends(id),
  slug text not null unique,
  title text not null,
  label text not null,
  status text not null,
  race_stage text not null,
  freshness text not null,
  confidence numeric(4,3) not null,
  trend text not null,
  summary_output_id text not null
);

create table cluster_documents (
  cluster_id text not null references clusters(id),
  document_id text not null references documents(id),
  primary key (cluster_id, document_id)
);

create table cluster_entities (
  cluster_id text not null references clusters(id),
  entity_id text not null references entities(id),
  primary key (cluster_id, entity_id)
);

create table summary_outputs (
  id text primary key,
  cluster_id text not null references clusters(id),
  label text not null,
  title text not null,
  body text not null,
  editorial_status text not null,
  updated_at timestamptz not null
);

create table distribution_assets (
  id text primary key,
  summary_output_id text not null references summary_outputs(id),
  kind text not null,
  title text not null,
  body text not null
);

