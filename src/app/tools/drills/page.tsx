import type { Metadata } from 'next'
import Nav from '@/components/layout/Nav'
import Footer from '@/components/layout/Footer'
import DrillPlanner from '@/components/tools/DrillPlanner'

export const metadata: Metadata = {
  title: 'AI Drill Planner',
}

export default function DrillsPage() {
  return (
    <>
      <Nav />
      <main className="max-w-site mx-auto px-5 py-6">
        <h1 className="font-condensed text-3xl font-bold uppercase border-b-2 border-ink pb-2.5">
          AI Drill Planner
        </h1>
        <p className="text-sm text-ink4 mt-2 mb-6">
          Get personalized practice plans powered by AI. Select your skill level and focus areas.
        </p>
        <DrillPlanner />
      </main>
      <Footer />
    </>
  )
}
