import type { Player, Ranking, Paddle, Article, Match, Tournament } from './types'

export const seedPlayers: Player[] = [
  { id: '1', name: 'Ben Johns', country: 'US', sponsor: 'JOOLA', paddle: 'Selkirk Halo', slug: 'ben-johns', bio: 'World #1 pickleball player. Multiple PPA Tour titles across singles, doubles, and mixed doubles.' },
  { id: '2', name: 'Tyson McGuffin', country: 'US', sponsor: 'Selkirk', paddle: 'Selkirk AMPED', slug: 'tyson-mcguffin', bio: 'Fierce competitor known for his powerful drives and aggressive play style.' },
  { id: '3', name: 'Federico Staksrud', country: 'AR', sponsor: 'JOOLA', paddle: 'JOOLA Perseus', slug: 'federico-staksrud', bio: 'Argentina\'s top pickleball export, rising quickly through the PPA rankings.' },
  { id: '4', name: 'JW Johnson', country: 'US', sponsor: 'Paddletek', paddle: 'Paddletek', slug: 'jw-johnson', bio: 'Young sensation with incredible reflexes and court awareness.' },
  { id: '5', name: 'Dylan Frazier', country: 'US', sponsor: 'JOOLA', paddle: 'JOOLA Collin', slug: 'dylan-frazier', bio: 'Versatile player excelling in both singles and doubles formats.' },
  { id: '6', name: 'Rafa Hewett', country: 'GB', sponsor: 'JOOLA', paddle: 'JOOLA', slug: 'rafa-hewett', bio: 'Great Britain\'s leading pickleball player, making waves on the international circuit.' },
  { id: '7', name: 'Christian Alshon', country: 'US', sponsor: 'Engage', paddle: 'Engage', slug: 'christian-alshon', bio: 'Consistent performer with strong all-around game.' },
]

export const seedRankings: Ranking[] = [
  { id: 'r1', player_id: '1', player: seedPlayers[0], category: 'mens_singles', rank: 1, points: 12480, win_rate: 78, titles: 12, delta: 0, period: '2025-04-01' },
  { id: 'r2', player_id: '2', player: seedPlayers[1], category: 'mens_singles', rank: 2, points: 10240, win_rate: 71, titles: 8, delta: 0, period: '2025-04-01' },
  { id: 'r3', player_id: '3', player: seedPlayers[2], category: 'mens_singles', rank: 3, points: 9880, win_rate: 68, titles: 5, delta: 1, period: '2025-04-01' },
  { id: 'r4', player_id: '4', player: seedPlayers[3], category: 'mens_singles', rank: 4, points: 9120, win_rate: 65, titles: 4, delta: -1, period: '2025-04-01' },
  { id: 'r5', player_id: '5', player: seedPlayers[4], category: 'mens_singles', rank: 5, points: 8760, win_rate: 62, titles: 3, delta: 0, period: '2025-04-01' },
  { id: 'r6', player_id: '6', player: seedPlayers[5], category: 'mens_singles', rank: 6, points: 8420, win_rate: 61, titles: 2, delta: 3, period: '2025-04-01' },
  { id: 'r7', player_id: '7', player: seedPlayers[6], category: 'mens_singles', rank: 7, points: 7980, win_rate: 59, titles: 1, delta: -2, period: '2025-04-01' },
]

export const seedPaddles: Paddle[] = [
  {
    id: 'p1', brand: 'JOOLA', name: 'Perseus Carbon 14mm', slug: 'joola-perseus-carbon-14mm',
    price_usd: 229, score_overall: 9.2, score_control: 9.5, score_power: 8.8,
    score_spin: 9.0, score_durability: 9.1, score_feel: 9.3, score_value: 8.5,
    verdict: "Editors' Choice 2025", featured: true,
    core_mm: 14, face_material: 'Carbon Fiber', weight_oz: 8.2, length_in: 16.5, width_in: 7.5,
    good_for: ['Control players', 'Advanced', 'Tournament'], bad_for: ['Beginners', 'Budget seekers'],
  },
  {
    id: 'p2', brand: 'Selkirk', name: 'Halo Power Air Invikta', slug: 'selkirk-halo-power-air-invikta',
    price_usd: 249, score_overall: 8.8, score_control: 8.5, score_power: 9.2,
    score_spin: 8.7, score_durability: 8.6, score_feel: 8.8, score_value: 7.5,
    verdict: 'Power Beast', featured: true,
    core_mm: 16, face_material: 'Carbon Fiber', weight_oz: 8.4, length_in: 16.5, width_in: 7.4,
    good_for: ['Power players', 'Singles'], bad_for: ['Touch players', 'Budget seekers'],
  },
  {
    id: 'p3', brand: 'SYPIK', name: 'Triton 5 Pro', slug: 'sypik-triton-5-pro',
    price_usd: 179, score_overall: 8.5, score_control: 8.7, score_power: 8.3,
    score_spin: 8.5, score_durability: 8.8, score_feel: 8.4, score_value: 9.2,
    verdict: 'Best Value SEA', featured: true,
    core_mm: 14, face_material: 'Fiberglass + Carbon', weight_oz: 7.9, length_in: 16.0, width_in: 7.5,
    good_for: ['All-around', 'Value seekers', 'SEA players'], bad_for: ['Pro singles'],
  },
  {
    id: 'p4', brand: 'Paddletek', name: 'Bantam EX-L Pro', slug: 'paddletek-bantam-ex-l-pro',
    price_usd: 189, score_overall: 8.1, score_control: 8.3, score_power: 8.0,
    score_spin: 7.8, score_durability: 8.5, score_feel: 8.2, score_value: 8.0,
    verdict: 'Solid All-Round', featured: false,
    core_mm: 13, face_material: 'Fiberglass', weight_oz: 7.8, length_in: 15.75, width_in: 8.0,
    good_for: ['All-around', 'Recreational'], bad_for: ['Competitive singles'],
  },
]

const now = new Date()
const day = 24 * 60 * 60 * 1000

export const seedArticles: Article[] = [
  {
    id: 'a1', title: 'Ben Johns Wins PPA Austin Open', slug: 'ben-johns-wins-ppa-austin-open',
    category: 'tournament', excerpt: 'Back-to-back titles for the world number one in a dominant display at the PPA Austin Open. Johns defeated Tyson McGuffin 11-7 in the final.',
    content: '<p>Ben Johns has once again proven why he is the undisputed world number one, claiming his second consecutive PPA Austin Open title with a commanding 11-7 victory over Tyson McGuffin in the final.</p><p>The 25-year-old was in imperious form throughout the tournament, dropping just one game en route to the final. His serve was particularly devastating, with 15 aces across the three-day event.</p><p>"I felt really locked in this week," Johns said after the match. "The crowd energy in Austin is always incredible and it pushes me to play my best."</p><p>McGuffin, despite the loss, showed impressive form in reaching the final, defeating Federico Staksrud in a thrilling semifinal 11-9.</p>',
    author: 'PicklrLab Editorial', published_at: new Date(now.getTime() - 1 * day).toISOString(),
    is_featured: true, views: 5420,
  },
  {
    id: 'a2', title: 'JOOLA Perseus 14mm — Full Lab Review', slug: 'joola-perseus-14mm-full-lab-review',
    category: 'review', excerpt: 'Score 9.2 — the best control paddle we have tested this year. Detailed breakdown of every metric inside.',
    content: '<p>The JOOLA Perseus Carbon 14mm has set a new standard for control paddles in 2025. After extensive lab testing and on-court evaluation, we\'re awarding it our Editors\' Choice badge.</p><p><strong>Control (9.5/10):</strong> The 14mm core thickness provides exceptional touch at the kitchen line. Dinks felt precise and predictable, even under pressure.</p><p><strong>Power (8.8/10):</strong> Despite being a control-oriented paddle, the carbon fiber face generates surprising pop on drives and overheads.</p><p><strong>Spin (9.0/10):</strong> The textured surface creates excellent spin rates, particularly on serves and third-shot drops.</p><p>At $229, it\'s a premium investment, but for serious players looking for tournament-grade equipment, the Perseus Carbon delivers.</p>',
    author: 'PicklrLab Editorial', published_at: new Date(now.getTime() - 3 * day).toISOString(),
    is_featured: true, views: 3210,
  },
  {
    id: 'a3', title: 'Truong Vinh Hien Makes History at PPA MB Cup', slug: 'truong-vinh-hien-ppa-mb-cup',
    category: 'vietnam', excerpt: "Vietnam's top player becomes the first Southeast Asian athlete to reach a PPA quarterfinal, putting SEA pickleball on the global map.",
    content: '<p>In a historic moment for Southeast Asian pickleball, Vietnam\'s Truong Vinh Hien has become the first player from the region to reach a PPA Tour quarterfinal.</p><p>Hien, ranked #1 in Vietnam and #3 in Southeast Asia, stunned the crowd at the MB Cup with upset victories over two top-30 players before bowing out to eventual finalist Tyson McGuffin.</p><p>"This is just the beginning for Vietnamese pickleball," Hien said. "We have so many talented players back home who are hungry to compete at this level."</p><p>The achievement has sparked significant interest in pickleball across Vietnam, with court bookings reportedly doubling in Ho Chi Minh City and Hanoi following his run.</p>',
    author: 'PicklrLab Editorial', published_at: new Date(now.getTime() - 5 * day).toISOString(),
    is_featured: true, views: 8900,
  },
  {
    id: 'a4', title: 'April 2025 Rankings — 12 Major Moves', slug: 'april-2025-rankings-12-major-moves',
    category: 'rankings', excerpt: 'Weekly rankings update with 12 significant position changes across all categories. Rafa Hewett surges 3 spots.',
    content: '<p>This week\'s rankings update features 12 significant position changes, the most movement we\'ve seen since January.</p><p><strong>Biggest Movers:</strong></p><ul><li>Rafa Hewett: +3 to #6 (career high)</li><li>Federico Staksrud: +1 to #3</li><li>JW Johnson: -1 to #4</li><li>Christian Alshon: -2 to #7</li></ul><p>Ben Johns and Tyson McGuffin remain locked in the top two positions, with Johns extending his points lead after the Austin Open victory.</p>',
    author: 'PicklrLab Editorial', published_at: new Date(now.getTime() - 7 * day).toISOString(),
    is_featured: false, views: 2100,
  },
  {
    id: 'a5', title: 'Why Carbon Fiber Is Taking Over the Pro Circuit', slug: 'carbon-fiber-pro-circuit',
    category: 'opinion', excerpt: 'Analysis of equipment trends showing carbon fiber face paddles now dominate the top 50 players worldwide.',
    content: '<p>A quiet revolution has been taking place in professional pickleball equipment. Carbon fiber face paddles now account for 78% of paddles used by top-50 ranked players, up from just 35% two years ago.</p><p>The shift is driven by three key advantages: superior spin generation from textured carbon surfaces, better power transfer efficiency, and increased durability under tournament conditions.</p><p>JOOLA, Selkirk, and Engage have led the charge, with their carbon fiber models becoming the weapons of choice for the game\'s elite players.</p><p>For recreational players, the question is whether the premium price tag (typically $180-$260) is justified. Our lab data suggests that above a 3.5 skill level, the performance benefits become meaningful.</p>',
    author: 'PicklrLab Editorial', published_at: new Date(now.getTime() - 10 * day).toISOString(),
    is_featured: false, views: 1890,
  },
  {
    id: 'a6', title: 'Selkirk Halo Power Air — Lab Review', slug: 'selkirk-halo-power-air-review',
    category: 'review', excerpt: 'Score 8.8 — a power-oriented paddle that delivers devastating drives without sacrificing feel.',
    author: 'PicklrLab Editorial', published_at: new Date(now.getTime() - 12 * day).toISOString(),
    is_featured: false, views: 1540,
  },
  {
    id: 'a7', title: 'SEA Pickleball Explodes: 40% Growth in 2025', slug: 'sea-pickleball-growth-2025',
    category: 'sea', excerpt: 'Court bookings across Southeast Asia are up 40% year-over-year as the sport gains mainstream recognition.',
    author: 'PicklrLab Editorial', published_at: new Date(now.getTime() - 14 * day).toISOString(),
    is_featured: false, views: 2450,
  },
  {
    id: 'a8', title: '5 Drills to Improve Your Dinking Game', slug: '5-drills-improve-dinking',
    category: 'training', excerpt: 'Master the most important shot in pickleball with these five proven drills from pro coaches.',
    author: 'PicklrLab Editorial', published_at: new Date(now.getTime() - 16 * day).toISOString(),
    is_featured: false, views: 3100,
  },
  {
    id: 'a9', title: 'SYPIK Triton 5 Pro — Best Value in SEA', slug: 'sypik-triton-5-pro-review',
    category: 'review', excerpt: 'At $179, the Triton 5 Pro delivers 90% of the performance of paddles costing $70 more.',
    author: 'PicklrLab Editorial', published_at: new Date(now.getTime() - 18 * day).toISOString(),
    is_featured: false, views: 1200,
  },
  {
    id: 'a10', title: 'Vietnam Open 2025 Draw Announced', slug: 'vietnam-open-2025-draw',
    category: 'vietnam', excerpt: 'The largest pickleball tournament in Vietnam history with 256 players across 8 categories.',
    author: 'PicklrLab Editorial', published_at: new Date(now.getTime() - 20 * day).toISOString(),
    is_featured: false, views: 4200,
  },
  {
    id: 'a11', title: 'MLP Draft Results: Who Went Where', slug: 'mlp-draft-results-2025',
    category: 'tournament', excerpt: 'Complete MLP draft recap with analysis of every pick and team composition breakdown.',
    author: 'PicklrLab Editorial', published_at: new Date(now.getTime() - 22 * day).toISOString(),
    is_featured: false, views: 1780,
  },
  {
    id: 'a12', title: 'The Science of Paddle Spin: RPM Data Revealed', slug: 'science-paddle-spin-rpm',
    category: 'gear', excerpt: 'We tested 20 paddles with a high-speed camera to measure actual spin rates in RPM.',
    author: 'PicklrLab Editorial', published_at: new Date(now.getTime() - 25 * day).toISOString(),
    is_featured: false, views: 2890,
  },
]

export const seedMatches: Match[] = [
  {
    id: 'm1', tournament: 'PPA Austin Open', round: 'Final', category: 'mens_singles',
    player1: seedPlayers[0], player2: seedPlayers[1],
    score_p1: 11, score_p2: 7, status: 'done', odds_p1: '-180',
    scheduled_at: new Date(now.getTime() - 1 * day).toISOString(),
  },
  {
    id: 'm2', tournament: 'PPA Austin Open', round: 'Semi', category: 'mens_singles',
    player1: seedPlayers[2], player2: seedPlayers[3],
    score_p1: 11, score_p2: 9, status: 'done', odds_p1: '+120',
    scheduled_at: new Date(now.getTime() - 2 * day).toISOString(),
  },
  {
    id: 'm3', tournament: 'MLP Championship', round: 'R16', category: 'mixed_doubles',
    player1: seedPlayers[0], player2: seedPlayers[4],
    status: 'upcoming', odds_p1: '-200',
    scheduled_at: new Date(now.getTime() + 2 * day).toISOString(),
  },
  {
    id: 'm4', tournament: 'PPA Tour — NYC Open', round: 'QF', category: 'mens_singles',
    player1: seedPlayers[5], player2: seedPlayers[6],
    status: 'upcoming', odds_p1: '+110',
    scheduled_at: new Date(now.getTime() + 5 * day).toISOString(),
  },
  {
    id: 'm5', tournament: 'SEA Open Bangkok', round: 'Final', category: 'mens_singles',
    player1: seedPlayers[2], player2: seedPlayers[5],
    score_p1: 11, score_p2: 8, status: 'done',
    scheduled_at: new Date(now.getTime() - 4 * day).toISOString(),
  },
]

export const seedTournaments: Tournament[] = [
  {
    id: 't1', name: 'PPA Austin Open', slug: 'ppa-austin-open',
    location: 'Austin, TX', country: 'US',
    start_date: '2025-03-28', end_date: '2025-03-30',
    prize_money: 150000, status: 'past', category: 'PPA',
    description: 'The PPA Austin Open returns for its third year with a $150K prize pool.',
  },
  {
    id: 't2', name: 'MLP Championship Series', slug: 'mlp-championship-series',
    location: 'Dallas, TX', country: 'US',
    start_date: '2025-04-11', end_date: '2025-04-13',
    prize_money: 200000, status: 'upcoming', category: 'MLP',
    description: 'The premier team-based pickleball event featuring the best players worldwide.',
  },
  {
    id: 't3', name: 'PPA NYC Open', slug: 'ppa-nyc-open',
    location: 'New York, NY', country: 'US',
    start_date: '2025-04-25', end_date: '2025-04-27',
    prize_money: 175000, status: 'upcoming', category: 'PPA',
    description: 'PPA Tour heads to the Big Apple for three days of elite pickleball action.',
  },
  {
    id: 't4', name: 'SEA Open Bangkok', slug: 'sea-open-bangkok',
    location: 'Bangkok', country: 'TH',
    start_date: '2025-03-21', end_date: '2025-03-23',
    prize_money: 50000, status: 'past', category: 'SEA',
    description: 'Southeast Asia\'s premier pickleball tournament hosted in Thailand.',
  },
  {
    id: 't5', name: 'Vietnam National Championships', slug: 'vietnam-national-championships',
    location: 'Ho Chi Minh City', country: 'VN',
    start_date: '2025-05-10', end_date: '2025-05-12',
    prize_money: 25000, status: 'upcoming', category: 'Vietnam',
    description: 'The biggest pickleball event in Vietnam with national ranking points.',
  },
  {
    id: 't6', name: 'PPA Tour Finals', slug: 'ppa-tour-finals',
    location: 'Las Vegas, NV', country: 'US',
    start_date: '2025-11-14', end_date: '2025-11-16',
    prize_money: 500000, status: 'upcoming', category: 'PPA',
    description: 'Season-ending championship for the top PPA Tour players.',
  },
]

export const seedMostRead = seedArticles
  .slice()
  .sort((a, b) => b.views - a.views)
  .slice(0, 5)
  .map(({ id, title, slug, category, views }) => ({ id, title, slug, category, views }))
