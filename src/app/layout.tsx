import type { Metadata } from 'next'
import { Inter, Oswald } from 'next/font/google'
import Script from 'next/script'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const oswald = Oswald({ subsets: ['latin'], variable: '--font-oswald', weight: ['400', '500', '600', '700'] })

const GA_ID = 'G-63TYQPYCDX'

export const metadata: Metadata = {
  title: { default: 'PicklrLab — The World\'s #1 Pickleball Authority', template: '%s — PicklrLab' },
  description: 'Rankings, reviews, news, and tools for the global pickleball community.',
  metadataBase: new URL('https://picklrlab.com'),
  openGraph: { siteName: 'PicklrLab', type: 'website', locale: 'en_US' },
  verification: {
    google: 'G-63TYQPYCDX',
  },
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${oswald.variable}`}>
      <head>
        <Script src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`} strategy="afterInteractive" />
        <Script id="gtag-init" strategy="afterInteractive">
          {`window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','${GA_ID}');`}
        </Script>
      </head>
      <body>{children}</body>
    </html>
  )
}
