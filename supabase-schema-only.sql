-- ============================================================
-- PicklrLab — Schema Only (no seed data)
-- Paste vào Supabase SQL Editor → Click Run
-- ============================================================

CREATE TABLE IF NOT EXISTS players (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        TEXT NOT NULL,
  country     CHAR(2) NOT NULL,
  sponsor     TEXT,
  paddle      TEXT,
  photo_url   TEXT,
  slug        TEXT UNIQUE,
  bio         TEXT,
  birth_year  INT,
  created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS rankings (
  id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  player_id UUID REFERENCES players(id),
  category  TEXT NOT NULL,
  rank      INT NOT NULL,
  points    INT NOT NULL,
  win_rate  NUMERIC(4,1),
  titles    INT DEFAULT 0,
  delta     INT DEFAULT 0,
  period    DATE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS paddles (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand            TEXT NOT NULL,
  name             TEXT NOT NULL,
  slug             TEXT UNIQUE,
  price_usd        NUMERIC(7,2),
  buy_url          TEXT,
  core_mm          INT,
  face_material    TEXT,
  weight_oz        NUMERIC(4,2),
  length_in        NUMERIC(4,2),
  width_in         NUMERIC(4,2),
  score_overall    NUMERIC(3,1),
  score_control    NUMERIC(3,1),
  score_power      NUMERIC(3,1),
  score_spin       NUMERIC(3,1),
  score_durability NUMERIC(3,1),
  score_feel       NUMERIC(3,1),
  score_value      NUMERIC(3,1),
  verdict          TEXT,
  good_for         TEXT[],
  bad_for          TEXT[],
  featured         BOOLEAN DEFAULT false,
  tested_at        DATE,
  created_at       TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tournaments (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name         TEXT NOT NULL,
  slug         TEXT UNIQUE NOT NULL,
  location     TEXT,
  country      CHAR(2),
  start_date   DATE,
  end_date     DATE,
  prize_money  INT,
  status       TEXT DEFAULT 'upcoming',
  category     TEXT NOT NULL,
  description  TEXT,
  created_at   TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS articles (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title        TEXT NOT NULL,
  slug         TEXT UNIQUE NOT NULL,
  category     TEXT NOT NULL,
  excerpt      TEXT,
  content      TEXT,
  author       TEXT DEFAULT 'PicklrLab Editorial',
  published_at TIMESTAMPTZ,
  is_featured  BOOLEAN DEFAULT false,
  views        INT DEFAULT 0,
  created_at   TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS matches (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tournament   TEXT NOT NULL,
  round        TEXT,
  category     TEXT,
  player1_id   UUID REFERENCES players(id),
  player2_id   UUID REFERENCES players(id),
  score_p1     INT,
  score_p2     INT,
  status       TEXT DEFAULT 'upcoming',
  odds_p1      TEXT,
  scheduled_at TIMESTAMPTZ,
  created_at   TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS courts (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name       TEXT NOT NULL,
  country    CHAR(2),
  city       TEXT,
  address    TEXT,
  lat        NUMERIC(9,6),
  lng        NUMERIC(9,6),
  indoor     BOOLEAN,
  rating     NUMERIC(2,1),
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS newsletter_subscribers (
  email         TEXT PRIMARY KEY,
  subscribed_at TIMESTAMPTZ DEFAULT now()
);

-- ==================== RLS ====================
ALTER TABLE players    ENABLE ROW LEVEL SECURITY;
ALTER TABLE rankings   ENABLE ROW LEVEL SECURITY;
ALTER TABLE paddles    ENABLE ROW LEVEL SECURITY;
ALTER TABLE articles   ENABLE ROW LEVEL SECURITY;
ALTER TABLE matches    ENABLE ROW LEVEL SECURITY;
ALTER TABLE courts     ENABLE ROW LEVEL SECURITY;
ALTER TABLE tournaments ENABLE ROW LEVEL SECURITY;
ALTER TABLE newsletter_subscribers ENABLE ROW LEVEL SECURITY;

CREATE POLICY "public read" ON players    FOR SELECT USING (true);
CREATE POLICY "public read" ON rankings   FOR SELECT USING (true);
CREATE POLICY "public read" ON paddles    FOR SELECT USING (true);
CREATE POLICY "public read" ON articles   FOR SELECT USING (published_at IS NOT NULL);
CREATE POLICY "public read" ON matches    FOR SELECT USING (true);
CREATE POLICY "public read" ON courts     FOR SELECT USING (true);
CREATE POLICY "public read" ON tournaments FOR SELECT USING (true);
