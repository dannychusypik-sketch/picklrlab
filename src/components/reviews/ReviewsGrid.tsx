'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import type { Paddle } from '@/lib/types'

type SortOption = 'score' | 'price_low' | 'price_high' | 'name'

export default function ReviewsGrid({ paddles }: { paddles: Paddle[] }) {
  const [brandFilter, setBrandFilter] = useState('')
  const [scoreRange, setScoreRange] = useState<[number, number]>([0, 100])
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 500])
  const [sort, setSort] = useState<SortOption>('score')

  const brands = useMemo(() => {
    const set = new Set(paddles.map((p) => p.brand))
    return Array.from(set).sort()
  }, [paddles])

  const filtered = useMemo(() => {
    let result = [...paddles]
    if (brandFilter) result = result.filter((p) => p.brand === brandFilter)
    result = result.filter(
      (p) =>
        (p.score_overall ?? 0) >= scoreRange[0] &&
        (p.score_overall ?? 0) <= scoreRange[1],
    )
    result = result.filter(
      (p) =>
        (p.price_usd ?? 0) >= priceRange[0] &&
        (p.price_usd ?? 0) <= priceRange[1],
    )
    switch (sort) {
      case 'score':
        result.sort((a, b) => (b.score_overall ?? 0) - (a.score_overall ?? 0))
        break
      case 'price_low':
        result.sort((a, b) => (a.price_usd ?? 0) - (b.price_usd ?? 0))
        break
      case 'price_high':
        result.sort((a, b) => (b.price_usd ?? 0) - (a.price_usd ?? 0))
        break
      case 'name':
        result.sort((a, b) => a.name.localeCompare(b.name))
        break
    }
    return result
  }, [paddles, brandFilter, scoreRange, priceRange, sort])

  return (
    <div>
      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3 mb-6">
        <select
          value={brandFilter}
          onChange={(e) => setBrandFilter(e.target.value)}
          className="border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue/30"
        >
          <option value="">All Brands</option>
          {brands.map((b) => (
            <option key={b} value={b}>{b}</option>
          ))}
        </select>

        <div className="flex items-center gap-1 text-xs text-ink4">
          <span>Score:</span>
          <input
            type="number"
            min={0}
            max={100}
            value={scoreRange[0]}
            onChange={(e) => setScoreRange([Number(e.target.value), scoreRange[1]])}
            className="w-14 border border-border rounded px-2 py-1 text-xs"
          />
          <span>-</span>
          <input
            type="number"
            min={0}
            max={100}
            value={scoreRange[1]}
            onChange={(e) => setScoreRange([scoreRange[0], Number(e.target.value)])}
            className="w-14 border border-border rounded px-2 py-1 text-xs"
          />
        </div>

        <div className="flex items-center gap-1 text-xs text-ink4">
          <span>Price: $</span>
          <input
            type="number"
            min={0}
            max={500}
            value={priceRange[0]}
            onChange={(e) => setPriceRange([Number(e.target.value), priceRange[1]])}
            className="w-16 border border-border rounded px-2 py-1 text-xs"
          />
          <span>- $</span>
          <input
            type="number"
            min={0}
            max={500}
            value={priceRange[1]}
            onChange={(e) => setPriceRange([priceRange[0], Number(e.target.value)])}
            className="w-16 border border-border rounded px-2 py-1 text-xs"
          />
        </div>

        <select
          value={sort}
          onChange={(e) => setSort(e.target.value as SortOption)}
          className="border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue/30 ml-auto"
        >
          <option value="score">Highest Score</option>
          <option value="price_low">Price: Low to High</option>
          <option value="price_high">Price: High to Low</option>
          <option value="name">Name A-Z</option>
        </select>
      </div>

      {/* 2-col grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map((paddle) => (
          <Link
            key={paddle.id}
            href={`/reviews/${paddle.slug}`}
            className="flex gap-4 p-4 border border-border rounded-lg hover:shadow-md transition-shadow duration-fast bg-white"
          >
            {/* Score badge */}
            <div className="w-16 h-16 shrink-0 rounded-lg bg-gradient-to-br from-navy to-blue flex items-center justify-center">
              <span className="font-condensed text-2xl font-bold text-white">
                {paddle.score_overall ?? '-'}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <span className="font-condensed text-2xs font-bold uppercase tracking-wider text-blue">
                {paddle.brand}
              </span>
              <h3 className="font-condensed text-lg font-bold uppercase leading-tight mt-0.5">
                {paddle.name}
              </h3>
              <p className="text-xs text-ink4 mt-1 line-clamp-2">{paddle.verdict}</p>
              <div className="flex items-center gap-3 mt-2">
                {paddle.price_usd && (
                  <span className="text-sm font-bold">${paddle.price_usd}</span>
                )}
                <div className="flex gap-2 text-2xs text-ink4">
                  <span>PWR {paddle.score_power}</span>
                  <span>CTL {paddle.score_control}</span>
                  <span>SPN {paddle.score_spin}</span>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {filtered.length === 0 && (
        <p className="text-ink4 text-sm py-8 text-center">No paddles match your filters.</p>
      )}
    </div>
  )
}
