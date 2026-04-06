import type { Metadata } from 'next'
import Nav from '@/components/layout/Nav'
import Footer from '@/components/layout/Footer'
import { getCourts } from '@/lib/supabase'

export const metadata: Metadata = {
  title: 'Courts',
}

export default async function CourtsPage() {
  const courts = await getCourts()

  return (
    <>
      <Nav />
      <main className="max-w-site mx-auto px-5 py-6">
        <h1 className="font-condensed text-3xl font-bold uppercase border-b-2 border-ink pb-2.5">
          Courts
        </h1>
        <p className="text-sm text-ink4 mt-2 mb-6">
          Find pickleball courts near you.
        </p>

        {courts.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {courts.map((court) => (
              <div
                key={court.id}
                className="border border-border rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <h3 className="font-condensed text-md font-bold uppercase">{court.name}</h3>
                <p className="text-xs text-ink4 mt-1">
                  {[court.city, court.country].filter(Boolean).join(', ')}
                </p>
                {court.indoor !== undefined && (
                  <span className="inline-block mt-2 text-2xs font-bold uppercase bg-bg2 text-ink3 px-2 py-0.5 rounded-pill">
                    {court.indoor ? 'Indoor' : 'Outdoor'}
                  </span>
                )}
                {court.rating && (
                  <p className="text-sm mt-1">
                    {'★'.repeat(Math.round(court.rating))}
                    <span className="text-ink4 ml-1">{court.rating}/5</span>
                  </p>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-20">
            <div className="w-20 h-20 mx-auto bg-bg2 rounded-full flex items-center justify-center mb-4">
              <svg className="w-10 h-10 text-ink5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <h2 className="font-condensed text-xl font-bold uppercase">Coming Soon</h2>
            <p className="text-sm text-ink4 mt-2 max-w-md mx-auto">
              We are building a comprehensive database of pickleball courts worldwide. Check back soon for court finder with map integration.
            </p>
          </div>
        )}
      </main>
      <Footer />
    </>
  )
}
