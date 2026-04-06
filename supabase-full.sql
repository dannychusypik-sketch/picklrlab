-- ============================================================
-- PicklrLab — FULL Schema + Seed Data
-- Paste vào Supabase SQL Editor → Click Run
-- ============================================================

-- ==================== TABLES ====================

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

-- ==================== SEED: PLAYERS ====================

INSERT INTO players (name, country, sponsor, paddle, slug, bio) VALUES
  ('Ben Johns', 'US', 'JOOLA', 'Selkirk Halo', 'ben-johns', 'World #1 pickleball player. Multiple PPA Tour titles across singles, doubles, and mixed doubles. Known for his strategic play and unmatched court awareness.'),
  ('Tyson McGuffin', 'US', 'Selkirk', 'Selkirk AMPED', 'tyson-mcguffin', 'Fierce competitor known for his powerful drives and aggressive play style. Consistent top-5 player on the PPA Tour.'),
  ('Federico Staksrud', 'AR', 'JOOLA', 'JOOLA Perseus', 'federico-staksrud', 'Argentina''s top pickleball export, rising quickly through the PPA rankings with exceptional touch and finesse.'),
  ('JW Johnson', 'US', 'Paddletek', 'Paddletek', 'jw-johnson', 'Young sensation with incredible reflexes and court awareness. One of the most complete players in the game.'),
  ('Dylan Frazier', 'US', 'JOOLA', 'JOOLA Collin', 'dylan-frazier', 'Versatile player excelling in both singles and doubles formats. Known for his athleticism and power game.'),
  ('Rafa Hewett', 'GB', 'JOOLA', 'JOOLA', 'rafa-hewett', 'Great Britain''s leading pickleball player, making waves on the international circuit with rapid improvement.'),
  ('Christian Alshon', 'US', 'Engage', 'Engage', 'christian-alshon', 'Consistent performer with a strong all-around game. Rising steadily through the professional ranks.'),
  ('Anna Leigh Waters', 'US', 'Paddletek', 'Paddletek', 'anna-leigh-waters', 'Dominant force in women''s pickleball. Multiple Triple Crown winner and youngest #1 ranked player in history.'),
  ('Catherine Parenteau', 'CA', 'JOOLA', 'JOOLA Perseus', 'catherine-parenteau', 'Canadian-born powerhouse competing at the highest level. Known for her aggressive baseline play.'),
  ('Lea Jansen', 'US', 'Selkirk', 'Selkirk Halo', 'lea-jansen', 'Rising star on the women''s tour with exceptional defensive skills and court coverage.');

-- ==================== SEED: RANKINGS ====================

-- Men's Singles
INSERT INTO rankings (player_id, category, rank, points, win_rate, titles, delta, period)
SELECT p.id, 'mens_singles', r.rank, r.points, r.win_rate, r.titles, r.delta, '2025-04-01'
FROM (VALUES
  ('ben-johns',         1, 12480, 78.0, 12, 0),
  ('tyson-mcguffin',    2, 10240, 71.0, 8,  0),
  ('federico-staksrud', 3, 9880,  68.0, 5,  1),
  ('jw-johnson',        4, 9120,  65.0, 4, -1),
  ('dylan-frazier',     5, 8760,  62.0, 3,  0),
  ('rafa-hewett',       6, 8420,  61.0, 2,  3),
  ('christian-alshon',  7, 7980,  59.0, 1, -2)
) AS r(slug, rank, points, win_rate, titles, delta)
JOIN players p ON p.slug = r.slug;

-- Women's Singles
INSERT INTO rankings (player_id, category, rank, points, win_rate, titles, delta, period)
SELECT p.id, 'womens_singles', r.rank, r.points, r.win_rate, r.titles, r.delta, '2025-04-01'
FROM (VALUES
  ('anna-leigh-waters',    1, 13200, 82.0, 15, 0),
  ('catherine-parenteau',  2, 10800, 74.0, 9,  0),
  ('lea-jansen',           3, 9500,  69.0, 4,  1)
) AS r(slug, rank, points, win_rate, titles, delta)
JOIN players p ON p.slug = r.slug;

-- ==================== SEED: PADDLES ====================

INSERT INTO paddles (brand, name, slug, price_usd, score_overall, score_control, score_power, score_spin, score_durability, score_feel, score_value, verdict, featured, good_for, bad_for, core_mm, face_material, weight_oz, length_in, width_in) VALUES
  ('JOOLA', 'Perseus Carbon 14mm', 'joola-perseus-carbon-14mm', 229, 9.2, 9.5, 8.8, 9.0, 9.1, 9.3, 8.5, 'Editors'' Choice 2025', true, ARRAY['control players', 'advanced', 'tournament'], ARRAY['beginners', 'budget seekers'], 14, 'Carbon Fiber', 8.2, 16.5, 7.5),
  ('Selkirk', 'Halo Power Air Invikta', 'selkirk-halo-power-air-invikta', 249, 8.8, 8.5, 9.2, 8.7, 8.6, 8.8, 7.5, 'Power Beast', true, ARRAY['power players', 'singles'], ARRAY['touch players', 'budget seekers'], 16, 'Carbon Fiber', 8.4, 16.5, 7.4),
  ('SYPIK', 'Triton 5 Pro', 'sypik-triton-5-pro', 179, 8.5, 8.7, 8.3, 8.5, 8.8, 8.4, 9.2, 'Best Value SEA', true, ARRAY['all-around', 'value seekers', 'SEA players'], ARRAY['pro singles'], 14, 'Fiberglass + Carbon', 7.9, 16.0, 7.5),
  ('Paddletek', 'Bantam EX-L Pro', 'paddletek-bantam-ex-l-pro', 189, 8.1, 8.3, 8.0, 7.8, 8.5, 8.2, 8.0, 'Solid All-Round', false, ARRAY['all-around', 'recreational'], ARRAY['competitive singles'], 13, 'Fiberglass', 7.8, 15.75, 8.0),
  ('Engage', 'Pursuit MX 6.0', 'engage-pursuit-mx-60', 199, 8.3, 8.6, 8.1, 8.4, 8.2, 8.5, 8.0, 'Touch Master', false, ARRAY['control', 'doubles'], ARRAY['power players'], 14, 'Carbon Fiber', 7.9, 16.0, 7.5),
  ('CRBN', 'CRBN 1X Power Series', 'crbn-1x-power-series', 219, 8.9, 8.4, 9.3, 9.1, 8.3, 8.7, 8.2, 'Spin King', true, ARRAY['spin players', 'advanced'], ARRAY['beginners', 'touch players'], 16, 'Raw Carbon Fiber', 8.3, 16.5, 7.4);

-- ==================== SEED: ARTICLES ====================

INSERT INTO articles (title, slug, category, excerpt, content, author, published_at, is_featured, views) VALUES
  ('Ben Johns Wins PPA Austin Open', 'ben-johns-wins-ppa-austin-open', 'tournament',
   'Back-to-back titles for the world number one in a dominant display at the PPA Austin Open.',
   '<p>Ben Johns has once again proven why he is the undisputed world number one, claiming his second consecutive PPA Austin Open title with a commanding 11-7 victory over Tyson McGuffin in the final.</p><p>The 25-year-old was in imperious form throughout the tournament, dropping just one game en route to the final. His serve was particularly devastating, with 15 aces across the three-day event.</p><p>"I felt really locked in this week," Johns said. "The crowd energy in Austin is always incredible."</p>',
   'PicklrLab Editorial', now() - interval '1 day', true, 5420),

  ('JOOLA Perseus 14mm — Full Lab Review', 'joola-perseus-14mm-full-lab-review', 'review',
   'Score 9.2 — the best control paddle we have tested this year. Detailed breakdown inside.',
   '<p>The JOOLA Perseus Carbon 14mm has set a new standard for control paddles in 2025.</p><p><strong>Control (9.5/10):</strong> Exceptional touch at the kitchen line.</p><p><strong>Power (8.8/10):</strong> Surprising pop despite being control-oriented.</p><p><strong>Spin (9.0/10):</strong> Excellent spin rates on serves and drops.</p><p>At $229, it''s premium but worth every penny for serious players.</p>',
   'PicklrLab Editorial', now() - interval '3 days', true, 3210),

  ('Truong Vinh Hien Makes History at PPA MB Cup', 'truong-vinh-hien-ppa-mb-cup', 'vietnam',
   'Vietnam''s top player becomes the first SEA athlete to reach a PPA quarterfinal.',
   '<p>In a historic moment for Southeast Asian pickleball, Vietnam''s Truong Vinh Hien has become the first player from the region to reach a PPA Tour quarterfinal.</p><p>"This is just the beginning for Vietnamese pickleball," Hien said.</p>',
   'PicklrLab Editorial', now() - interval '5 days', true, 8900),

  ('April 2025 Rankings — 12 Major Moves', 'april-2025-rankings-12-major-moves', 'rankings',
   'Weekly rankings update with 12 significant position changes across all categories.',
   '<p>This week''s rankings update features 12 significant position changes.</p><p><strong>Biggest Movers:</strong></p><ul><li>Rafa Hewett: +3 to #6</li><li>Federico Staksrud: +1 to #3</li></ul>',
   'PicklrLab Editorial', now() - interval '7 days', false, 2100),

  ('Why Carbon Fiber Is Taking Over the Pro Circuit', 'carbon-fiber-pro-circuit', 'opinion',
   'Analysis of equipment trends showing carbon fiber face paddles now dominate the top 50.',
   '<p>Carbon fiber face paddles now account for 78% of paddles used by top-50 ranked players, up from 35% two years ago.</p>',
   'PicklrLab Editorial', now() - interval '10 days', false, 1890),

  ('Selkirk Halo Power Air — Lab Review', 'selkirk-halo-power-air-review', 'review',
   'Score 8.8 — a power-oriented paddle that delivers devastating drives without sacrificing feel.',
   '<p>The Selkirk Halo Power Air Invikta brings serious firepower to the court.</p>',
   'PicklrLab Editorial', now() - interval '12 days', false, 1540),

  ('SEA Pickleball Explodes: 40% Growth in 2025', 'sea-pickleball-growth-2025', 'sea',
   'Court bookings across Southeast Asia are up 40% year-over-year.',
   '<p>Pickleball in Southeast Asia is experiencing unprecedented growth.</p>',
   'PicklrLab Editorial', now() - interval '14 days', false, 2450),

  ('5 Drills to Improve Your Dinking Game', '5-drills-improve-dinking', 'training',
   'Master the most important shot in pickleball with these five proven drills.',
   '<p>Dinking is the foundation of competitive pickleball. Here are 5 drills to level up.</p>',
   'PicklrLab Editorial', now() - interval '16 days', false, 3100),

  ('SYPIK Triton 5 Pro — Best Value in SEA', 'sypik-triton-5-pro-review', 'review',
   'At $179, the Triton 5 Pro delivers 90% of the performance of paddles costing $70 more.',
   '<p>SYPIK has quickly established itself as the value leader in Southeast Asian pickleball.</p>',
   'PicklrLab Editorial', now() - interval '18 days', false, 1200),

  ('Vietnam Open 2025 Draw Announced', 'vietnam-open-2025-draw', 'vietnam',
   'The largest pickleball tournament in Vietnam history with 256 players.',
   '<p>The Vietnam Open 2025 will feature 256 players across 8 categories.</p>',
   'PicklrLab Editorial', now() - interval '20 days', false, 4200),

  ('MLP Draft Results: Who Went Where', 'mlp-draft-results-2025', 'tournament',
   'Complete MLP draft recap with analysis of every pick.',
   '<p>The 2025 MLP Draft delivered plenty of surprises.</p>',
   'PicklrLab Editorial', now() - interval '22 days', false, 1780),

  ('The Science of Paddle Spin: RPM Data Revealed', 'science-paddle-spin-rpm', 'gear',
   'We tested 20 paddles with a high-speed camera to measure actual spin rates.',
   '<p>We used a 1000fps camera to measure actual RPM on 20 different paddles.</p>',
   'PicklrLab Editorial', now() - interval '25 days', false, 2890);

-- ==================== SEED: TOURNAMENTS ====================

INSERT INTO tournaments (name, slug, location, country, start_date, end_date, prize_money, status, category, description) VALUES
  ('PPA Austin Open', 'ppa-austin-open', 'Austin, TX', 'US', '2025-03-28', '2025-03-30', 150000, 'past', 'PPA', 'The PPA Austin Open returns with a $150K prize pool.'),
  ('MLP Championship Series', 'mlp-championship-series', 'Dallas, TX', 'US', '2025-04-11', '2025-04-13', 200000, 'upcoming', 'MLP', 'Premier team-based pickleball event.'),
  ('PPA NYC Open', 'ppa-nyc-open', 'New York, NY', 'US', '2025-04-25', '2025-04-27', 175000, 'upcoming', 'PPA', 'PPA Tour heads to the Big Apple.'),
  ('SEA Open Bangkok', 'sea-open-bangkok', 'Bangkok', 'TH', '2025-03-21', '2025-03-23', 50000, 'past', 'SEA', 'Southeast Asia''s premier pickleball tournament.'),
  ('Vietnam National Championships', 'vietnam-national-championships', 'Ho Chi Minh City', 'VN', '2025-05-10', '2025-05-12', 25000, 'upcoming', 'Vietnam', 'The biggest pickleball event in Vietnam.'),
  ('PPA Tour Finals', 'ppa-tour-finals', 'Las Vegas, NV', 'US', '2025-11-14', '2025-11-16', 500000, 'upcoming', 'PPA', 'Season-ending championship for top PPA players.');

-- ==================== SEED: MATCHES ====================

INSERT INTO matches (tournament, round, category, player1_id, player2_id, score_p1, score_p2, status, odds_p1, scheduled_at)
SELECT m.tournament, m.round, m.category, p1.id, p2.id, m.score_p1, m.score_p2, m.status, m.odds_p1, m.scheduled_at
FROM (VALUES
  ('PPA Austin Open', 'Final', 'mens_singles', 'ben-johns', 'tyson-mcguffin', 11, 7, 'done', '-180', now() - interval '1 day'),
  ('PPA Austin Open', 'Semi', 'mens_singles', 'federico-staksrud', 'jw-johnson', 11, 9, 'done', '+120', now() - interval '2 days'),
  ('MLP Championship', 'R16', 'mixed_doubles', 'ben-johns', 'dylan-frazier', NULL, NULL, 'upcoming', '-200', now() + interval '5 days'),
  ('PPA NYC Open', 'QF', 'mens_singles', 'rafa-hewett', 'christian-alshon', NULL, NULL, 'upcoming', '+110', now() + interval '19 days'),
  ('SEA Open Bangkok', 'Final', 'mens_singles', 'federico-staksrud', 'rafa-hewett', 11, 8, 'done', NULL, now() - interval '16 days')
) AS m(tournament, round, category, slug1, slug2, score_p1, score_p2, status, odds_p1, scheduled_at)
JOIN players p1 ON p1.slug = m.slug1
JOIN players p2 ON p2.slug = m.slug2;

-- ==================== DONE ====================
-- Verify: SELECT count(*) FROM players; -- should be 10
-- Verify: SELECT count(*) FROM articles; -- should be 12
-- Verify: SELECT count(*) FROM paddles; -- should be 6
