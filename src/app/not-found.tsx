import Link from 'next/link'
import Nav from '@/components/layout/Nav'
import Footer from '@/components/layout/Footer'

export default function NotFound() {
  return (
    <>
      <Nav />
      <main className="max-w-site mx-auto px-5 py-20 text-center">
        <h1 className="text-6xl font-condensed font-bold text-ink4 mb-4">404</h1>
        <p className="text-lg text-ink3 mb-6">Page not found</p>
        <Link href="/" className="inline-block px-6 py-2.5 bg-ink text-white rounded font-condensed font-bold uppercase text-sm">
          Back to Home
        </Link>
      </main>
      <Footer />
    </>
  )
}
