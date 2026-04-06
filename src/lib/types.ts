export interface Player {
  id: string; name: string; country: string; sponsor?: string; paddle?: string;
  photo_url?: string; slug: string; bio?: string; bio_html?: string; birth_year?: number;
}
export interface Ranking {
  id: string; player_id: string; player?: Player; category: string;
  rank: number; points: number; win_rate?: number; titles: number; delta: number; period: string;
}
export interface Paddle {
  id: string; brand: string; name: string; slug: string; price_usd?: number;
  buy_url?: string; core_mm?: number; face_material?: string; weight_oz?: number;
  length_in?: number; width_in?: number; score_overall?: number; score_control?: number;
  score_power?: number; score_spin?: number; score_durability?: number; score_feel?: number;
  score_value?: number; verdict?: string; good_for?: string[]; bad_for?: string[]; featured: boolean;
}
export interface Article {
  id: string; title: string; slug: string; category: string; excerpt?: string;
  content?: string; author: string; published_at?: string; is_featured: boolean; views: number;
  image_url?: string;
}
export interface Match {
  id: string; tournament: string; round?: string; category?: string;
  player1?: Player; player2?: Player; score_p1?: number; score_p2?: number;
  status: 'live' | 'done' | 'upcoming'; odds_p1?: string; scheduled_at?: string;
}
export interface Tournament {
  id: string; name: string; slug: string; location: string; country: string;
  start_date: string; end_date: string; prize_money?: number;
  status: 'upcoming' | 'live' | 'past'; category: 'PPA' | 'MLP' | 'SEA' | 'Vietnam';
  description?: string;
}
export interface Court {
  id: string; name: string; country?: string; city?: string; address?: string;
  lat?: number; lng?: number; indoor?: boolean; rating?: number;
}
