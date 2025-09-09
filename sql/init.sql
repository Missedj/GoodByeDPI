CREATE TABLE IF NOT EXISTS accounts (
  id SERIAL PRIMARY KEY,
  phone TEXT UNIQUE NOT NULL,
  username TEXT,
  premium BOOLEAN DEFAULT FALSE,
  session_path TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'NEW',
  next_allowed_at TIMESTAMPTZ,
  proxy_id INTEGER,
  last_error TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS proxies (
  id SERIAL PRIMARY KEY,
  kind TEXT NOT NULL,
  host TEXT NOT NULL,
  port INTEGER NOT NULL,
  login TEXT,
  password TEXT,
  mtproto_secret TEXT,
  last_ok_at TIMESTAMPTZ,
  fail_streak INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS jobs (
  id BIGSERIAL PRIMARY KEY,
  account_id INTEGER NOT NULL,
  kind TEXT NOT NULL,
  payload_json JSONB NOT NULL,
  state TEXT NOT NULL DEFAULT 'PENDING',
  run_at TIMESTAMPTZ DEFAULT NOW(),
  attempts INTEGER DEFAULT 0,
  last_error TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS events (
  id BIGSERIAL PRIMARY KEY,
  account_id INTEGER,
  level TEXT NOT NULL,
  code TEXT NOT NULL,
  meta_json JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS jobs_state_run_at_idx ON jobs(state, run_at);
CREATE INDEX IF NOT EXISTS events_account_created_idx ON events(account_id, created_at);
