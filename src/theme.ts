export interface SportTheme {
  name: string;
  gradient: [string, string];
  pill: string;
  label: string;
  accent: string;
}

export type SportCategory =
  | 'sepakbola-luar'
  | 'sepakbola-lokal'
  | 'sepakbola-putri'
  | 'bulutangkis'
  | 'voli'
  | 'basket'
  | 'futsal'
  | 'esports';

export const SPORTS_THEMES: Record<SportCategory, SportTheme> = {
  'sepakbola-luar': {
    name: 'Sepakbola Luar',
    gradient: ['#08452b', '#052618'],
    pill: '#14532d',
    label: '#4ade80',
    accent: '#22c55e',
  },
  'sepakbola-lokal': {
    name: 'Sepakbola Lokal (Liga 1 + Timnas)',
    gradient: ['#0a337a', '#061f49'],
    pill: '#1565c0',
    label: '#60a5fa',
    accent: '#1565c0',
  },
  'sepakbola-putri': {
    name: 'Sepakbola Putri',
    gradient: ['#0a337a', '#061f49'],
    pill: '#1565c0',
    label: '#60a5fa',
    accent: '#1565c0',
  },
  bulutangkis: {
    name: 'Bulutangkis',
    gradient: ['#6a1215', '#440b11'],
    pill: '#b91c1c',
    label: '#f87171',
    accent: '#ef4444',
  },
  voli: {
    name: 'Voli',
    gradient: ['#7c2d12', '#431407'],
    pill: '#c2410c',
    label: '#fdba74',
    accent: '#f97316',
  },
  basket: {
    name: 'Basket',
    gradient: ['#744f05', '#4e3805'],
    pill: '#a16207',
    label: '#fcd34d',
    accent: '#f59e0b',
  },
  futsal: {
    name: 'Futsal',
    gradient: ['#134e4a', '#042f2e'],
    pill: '#0f766e',
    label: '#5eead4',
    accent: '#14b8a6',
  },
  esports: {
    name: 'Esports',
    gradient: ['#580f58', '#2d0625'],
    pill: '#a21caf',
    label: '#e879f9',
    accent: '#c026d3',
  },
};
