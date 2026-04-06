import type { Metadata } from 'next'
import Nav from '@/components/layout/Nav'
import Footer from '@/components/layout/Footer'
import EloCalculator from '@/components/tools/EloCalculator'

export const metadata: Metadata = {
  title: 'ELO Calculator',
}

export default function EloPage() {
  return (
    <>
      <Nav />
      <main className="max-w-site mx-auto px-5 py-6">
        <h1 className="font-condensed text-3xl font-bold uppercase border-b-2 border-ink pb-2.5">
          ELO Rating Calculator
        </h1>
        <p className="text-sm text-ink4 mt-2 mb-6">
          Calculate expected outcomes and rating changes based on the ELO system.
        </p>
        <EloCalculator />
      </main>
      <Footer />
    </>
  )
}
