'use client'

import { useState } from 'react'

const SKILL_LEVELS = ['Beginner (2.0-3.0)', 'Intermediate (3.5-4.0)', 'Advanced (4.5-5.0)', 'Pro (5.0+)']
const FOCUS_AREAS = ['Serves', 'Returns', 'Third Shot Drop', 'Dinking', 'Volleys', 'Drives', 'Lobs', 'Footwork', 'Strategy', 'Fitness']

export default function DrillPlanner() {
  const [skillLevel, setSkillLevel] = useState('')
  const [selectedAreas, setSelectedAreas] = useState<string[]>([])
  const [duration, setDuration] = useState('30')
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function toggleArea(area: string) {
    setSelectedAreas((prev) =>
      prev.includes(area) ? prev.filter((a) => a !== area) : [...prev, area],
    )
  }

  async function generate() {
    if (!skillLevel || selectedAreas.length === 0) {
      setError('Please select a skill level and at least one focus area.')
      return
    }
    setError('')
    setLoading(true)
    setResult('')

    try {
      const res = await fetch('/api/drill-generator', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skillLevel, focusAreas: selectedAreas, duration: Number(duration) }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Failed to generate plan')
      setResult(data.plan)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl">
      {/* Skill level */}
      <div className="mb-4">
        <label className="font-condensed text-sm font-bold uppercase tracking-wider block mb-2">
          Skill Level
        </label>
        <select
          value={skillLevel}
          onChange={(e) => setSkillLevel(e.target.value)}
          className="border border-border rounded-lg px-3 py-2 text-sm w-full focus:outline-none focus:ring-2 focus:ring-blue/30"
        >
          <option value="">Select level...</option>
          {SKILL_LEVELS.map((l) => (
            <option key={l} value={l}>{l}</option>
          ))}
        </select>
      </div>

      {/* Focus areas */}
      <div className="mb-4">
        <label className="font-condensed text-sm font-bold uppercase tracking-wider block mb-2">
          Focus Areas
        </label>
        <div className="flex flex-wrap gap-2">
          {FOCUS_AREAS.map((area) => (
            <button
              key={area}
              onClick={() => toggleArea(area)}
              className={`text-sm px-3 py-1.5 rounded-pill transition-all duration-fast ${
                selectedAreas.includes(area)
                  ? 'bg-blue text-white'
                  : 'bg-bg2 text-ink3 hover:bg-bg3'
              }`}
            >
              {area}
            </button>
          ))}
        </div>
      </div>

      {/* Duration */}
      <div className="mb-6">
        <label className="font-condensed text-sm font-bold uppercase tracking-wider block mb-2">
          Session Duration (minutes)
        </label>
        <select
          value={duration}
          onChange={(e) => setDuration(e.target.value)}
          className="border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue/30"
        >
          <option value="15">15 min</option>
          <option value="30">30 min</option>
          <option value="45">45 min</option>
          <option value="60">60 min</option>
          <option value="90">90 min</option>
        </select>
      </div>

      {error && (
        <p className="text-red text-sm mb-4">{error}</p>
      )}

      <button
        onClick={generate}
        disabled={loading}
        className="font-condensed text-sm font-bold uppercase tracking-wide bg-blue text-white px-6 py-2.5 rounded-lg hover:bg-blue-hover transition disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Generating...' : 'Generate Drill Plan'}
      </button>

      {/* Result */}
      {result && (
        <div className="mt-6 p-6 bg-bg2 rounded-lg">
          <h3 className="font-condensed text-lg font-bold uppercase mb-3">Your Drill Plan</h3>
          <div className="text-sm leading-relaxed whitespace-pre-wrap">{result}</div>
        </div>
      )}
    </div>
  )
}
