import type { Metadata } from 'next'
import Nav from '@/components/layout/Nav'
import Footer from '@/components/layout/Footer'
import BracketGenerator from '@/components/tools/BracketGenerator'

export const metadata: Metadata = {
  title: 'Bracket Generator',
}

export default function BracketsPage() {
  return (
    <>
      <Nav />
      <main className="max-w-site mx-auto px-5 py-6">
        <h1 className="font-condensed text-3xl font-bold uppercase border-b-2 border-ink pb-2.5">
          Bracket Generator
        </h1>
        <p className="text-sm text-ink4 mt-2 mb-6">
          Create tournament brackets instantly. Add players and generate single elimination brackets.
        </p>
        <BracketGenerator />
      </main>
      <Footer />
    </>
  )
}
