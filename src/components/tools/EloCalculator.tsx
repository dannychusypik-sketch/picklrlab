'use client'

import { useState, useMemo } from 'react'

function expectedScore(ratingA: number, ratingB: number): number {
  return 1 / (1 + Math.pow(10, (ratingB - ratingA) / 400))
}

function newRating(rating: number, expected: number, actual: number, kFactor: number): number {
  return Math.round(rating + kFactor * (actual - expected))
}

export default function EloCalculator() {
  const [ratingA, setRatingA] = useState(1500)
  const [ratingB, setRatingB] = useState(1500)
  const [kFactor, setKFactor] = useState(32)
  const [winner, setWinner] = useState<'A' | 'B' | null>(null)

  const expectedA = useMemo(() => expectedScore(ratingA, ratingB), [ratingA, ratingB])
  const expectedB = useMemo(() => 1 - expectedA, [expectedA])

  const results = useMemo(() => {
    if (!winner) return null
    const actualA = winner === 'A' ? 1 : 0
    const actualB = winner === 'B' ? 1 : 0
    return {
      newRatingA: newRating(ratingA, expectedA, actualA, kFactor),
      newRatingB: newRating(ratingB, expectedB, actualB, kFactor),
      changeA: newRating(ratingA, expectedA, actualA, kFactor) - ratingA,
      changeB: newRating(ratingB, expectedB, actualB, kFactor) - ratingB,
    }
  }, [ratingA, ratingB, expectedA, expectedB, kFactor, winner])

  return (
    <div className="max-w-xl">
      <div className="grid grid-cols-2 gap-6 mb-6">
        {/* Player A */}
        <div>
          <label className="font-condensed text-sm font-bold uppercase tracking-wider block mb-2">
            Player A Rating
          </label>
          <input
            type="number"
            value={ratingA}
            onChange={(e) => setRatingA(Number(e.target.value))}
            className="border border-border rounded-lg px-3 py-2 text-sm w-full focus:outline-none focus:ring-2 focus:ring-blue/30"
          />
          <p className="text-xs text-ink4 mt-1">
            Win probability: <span className="font-bold">{(expectedA * 100).toFixed(1)}%</span>
          </p>
        </div>

        {/* Player B */}
        <div>
          <label className="font-condensed text-sm font-bold uppercase tracking-wider block mb-2">
            Player B Rating
          </label>
          <input
            type="number"
            value={ratingB}
            onChange={(e) => setRatingB(Number(e.target.value))}
            className="border border-border rounded-lg px-3 py-2 text-sm w-full focus:outline-none focus:ring-2 focus:ring-blue/30"
          />
          <p className="text-xs text-ink4 mt-1">
            Win probability: <span className="font-bold">{(expectedB * 100).toFixed(1)}%</span>
          </p>
        </div>
      </div>

      {/* K-Factor */}
      <div className="mb-6">
        <label className="font-condensed text-sm font-bold uppercase tracking-wider block mb-2">
          K-Factor
        </label>
        <select
          value={kFactor}
          onChange={(e) => setKFactor(Number(e.target.value))}
          className="border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue/30"
        >
          <option value={16}>16 (Established players)</option>
          <option value={32}>32 (Standard)</option>
          <option value={40}>40 (New players)</option>
        </select>
      </div>

      {/* Winner selection */}
      <div className="mb-6">
        <label className="font-condensed text-sm font-bold uppercase tracking-wider block mb-2">
          Who Won?
        </label>
        <div className="flex gap-3">
          <button
            onClick={() => setWinner('A')}
            className={`flex-1 font-condensed text-sm font-bold uppercase tracking-wide py-2.5 rounded-lg transition ${
              winner === 'A'
                ? 'bg-blue text-white'
                : 'bg-bg2 text-ink3 hover:bg-bg3'
            }`}
          >
            Player A Wins
          </button>
          <button
            onClick={() => setWinner('B')}
            className={`flex-1 font-condensed text-sm font-bold uppercase tracking-wide py-2.5 rounded-lg transition ${
              winner === 'B'
                ? 'bg-blue text-white'
                : 'bg-bg2 text-ink3 hover:bg-bg3'
            }`}
          >
            Player B Wins
          </button>
        </div>
      </div>

      {/* Results */}
      {results && (
        <div className="bg-bg2 rounded-lg p-6">
          <h3 className="font-condensed text-lg font-bold uppercase mb-4">Rating Changes</h3>
          <div className="grid grid-cols-2 gap-6">
            <div>
              <p className="text-sm text-ink4">Player A</p>
              <p className="font-condensed text-2xl font-bold">{results.newRatingA}</p>
              <p className={`text-sm font-bold ${results.changeA >= 0 ? 'text-green2' : 'text-red'}`}>
                {results.changeA >= 0 ? '+' : ''}{results.changeA}
              </p>
            </div>
            <div>
              <p className="text-sm text-ink4">Player B</p>
              <p className="font-condensed text-2xl font-bold">{results.newRatingB}</p>
              <p className={`text-sm font-bold ${results.changeB >= 0 ? 'text-green2' : 'text-red'}`}>
                {results.changeB >= 0 ? '+' : ''}{results.changeB}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ELO explanation */}
      <div className="mt-8 p-4 border border-border rounded-lg">
        <h3 className="font-condensed text-sm font-bold uppercase tracking-wider mb-2">
          How ELO Works
        </h3>
        <p className="text-sm text-ink3 leading-relaxed">
          The ELO rating system calculates the relative skill levels of players. A higher rating indicates a stronger player. When a lower-rated player beats a higher-rated player, the rating change is larger. The K-factor determines how much ratings can change per game — higher K-factors mean bigger swings.
        </p>
      </div>
    </div>
  )
}
