import { formatDistanceToNow, format } from 'date-fns'

export function timeAgo(date: string | Date): string {
  return formatDistanceToNow(new Date(date), { addSuffix: true })
}
export function formatDate(date: string | Date): string {
  return format(new Date(date), 'MMM d, yyyy')
}
export function formatScore(score: number | undefined): string {
  if (score === undefined || score === null) return '-'
  return score.toFixed(1)
}
export function countryFlag(code: string): string {
  if (!code || code.length !== 2) return ''
  const offset = 127397
  return String.fromCodePoint(...code.toUpperCase().split('').map(c => c.charCodeAt(0) + offset))
}
