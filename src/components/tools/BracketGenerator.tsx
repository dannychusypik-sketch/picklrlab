'use client'

import { useState, useMemo } from 'react'

interface Match {
  round: number
  position: number
  player1: string
  player2: string
  winner?: string
}

export default function BracketGenerator() {
  const [playerInput, setPlayerInput] = useState('')
  const [players, setPlayers] = useState<string[]>([])
  const [bracket, setBracket] = useState<Match[]>([])

  function addPlayer() {
    const name = playerInput.trim()
    if (name && !players.includes(name)) {
      setPlayers([...players, name])
      setPlayerInput('')
    }
  }

  function removePlayer(name: string) {
    setPlayers(players.filter((p) => p !== name))
  }

  function generateBracket() {
    if (players.length < 2) return

    // Pad to nearest power of 2
    const size = Math.pow(2, Math.ceil(Math.log2(players.length)))
    const padded = [...players]
    while (padded.length < size) padded.push('BYE')

    // Shuffle
    const shuffled = [...padded].sort(() => Math.random() - 0.5)

    const matches: Match[] = []
    const rounds = Math.log2(size)

    // First round
    for (let i = 0; i < size / 2; i++) {
      matches.push({
        round: 1,
        position: i,
        player1: shuffled[i * 2],
        player2: shuffled[i * 2 + 1],
        winner: shuffled[i * 2 + 1] === 'BYE' ? shuffled[i * 2] : shuffled[i * 2] === 'BYE' ? shuffled[i * 2 + 1] : undefined,
      })
    }

    // Subsequent rounds (empty)
    let prevRoundCount = size / 2
    for (let round = 2; round <= rounds; round++) {
      prevRoundCount = prevRoundCount / 2
      for (let i = 0; i < prevRoundCount; i++) {
        matches.push({
          round,
          position: i,
          player1: 'TBD',
          player2: 'TBD',
        })
      }
    }

    setBracket(matches)
  }

  const rounds = useMemo(() => {
    const roundMap: Record<number, Match[]> = {}
    bracket.forEach((m) => {
      if (!roundMap[m.round]) roundMap[m.round] = []
      roundMap[m.round].push(m)
    })
    return Object.entries(roundMap)
      .sort(([a], [b]) => Number(a) - Number(b))
      .map(([round, matches]) => ({ round: Number(round), matches }))
  }, [bracket])

  const roundLabel = (round: number, total: number) => {
    if (round === total) return 'Final'
    if (round === total - 1) return 'Semi-Final'
    if (round === total - 2) return 'Quarter-Final'
    return `Round ${round}`
  }

  return (
    <div>
      {/* Player input */}
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          placeholder="Enter player name..."
          value={playerInput}
          onChange={(e) => setPlayerInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && addPlayer()}
          className="flex-1 border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue/30"
        />
        <button
          onClick={addPlayer}
          className="font-condensed text-sm font-bold uppercase tracking-wide bg-ink text-white px-4 py-2 rounded-lg hover:bg-ink2 transition"
        >
          Add
        </button>
      </div>

      {/* Player list */}
      {players.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {players.map((p) => (
            <span
              key={p}
              className="inline-flex items-center gap-1.5 bg-bg2 text-sm px-3 py-1 rounded-pill"
            >
              {p}
              <button
                onClick={() => removePlayer(p)}
                className="text-ink4 hover:text-red transition text-xs"
              >
                x
              </button>
            </span>
          ))}
        </div>
      )}

      <div className="flex items-center gap-3 mb-6">
        <span className="text-sm text-ink4">{players.length} players</span>
        <button
          onClick={generateBracket}
          disabled={players.length < 2}
          className="font-condensed text-sm font-bold uppercase tracking-wide bg-blue text-white px-5 py-2 rounded-lg hover:bg-blue-hover transition disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Generate Bracket
        </button>
      </div>

      {/* Bracket display */}
      {rounds.length > 0 && (
        <div className="overflow-x-auto pb-4">
          <div className="flex gap-6 min-w-max">
            {rounds.map(({ round, matches }) => (
              <div key={round} className="w-52">
                <h3 className="font-condensed text-xs font-bold uppercase tracking-wider text-ink4 mb-3">
                  {roundLabel(round, rounds.length)}
                </h3>
                <div className="space-y-3" style={{ paddingTop: `${(Math.pow(2, round - 1) - 1) * 28}px` }}>
                  {matches.map((m, i) => (
                    <div
                      key={i}
                      className="border border-border rounded-lg overflow-hidden"
                      style={{ marginBottom: `${(Math.pow(2, round - 1) - 1) * 56}px` }}
                    >
                      <div className={`px-3 py-1.5 text-sm border-b border-border ${m.winner === m.player1 ? 'bg-blue/10 font-bold' : ''}`}>
                        {m.player1}
                      </div>
                      <div className={`px-3 py-1.5 text-sm ${m.winner === m.player2 ? 'bg-blue/10 font-bold' : ''}`}>
                        {m.player2}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
