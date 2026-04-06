import type { Metadata } from 'next'
import { Inter, Oswald } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const oswald = Oswald({ subsets: ['latin'], variable: '--font-oswald', weight: ['400', '500', '600', '700'] })

export const metadata: Metadata = {
  title: { default: 'PicklrLab — The World\'s #1 Pickleball Authority', template: '%s — PicklrLab' },
  description: 'Rankings, reviews, news, and tools for the global pickleball community.',
  metadataBase: new URL('https://picklrlab.com'),
  openGraph: { siteName: 'PicklrLab', type: 'website', locale: 'en_US' },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${oswald.variable}`}>
      <body>{children}</body>
    </html>
  )
}
