'use client'

import { useState } from 'react'

export default function Newsletter() {
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) return
    // TODO: integrate with newsletter API
    setSubmitted(true)
  }

  return (
    <section className="bg-navy mt-12">
      <div className="max-w-site mx-auto px-5 py-12 text-center">
        <h2 className="font-condensed text-3xl font-bold uppercase tracking-tight text-white mb-2">
          Stay in the Game
        </h2>
        <p className="text-sm text-white/70 mb-6 max-w-md mx-auto">
          Get the latest rankings, reviews, and news delivered to your inbox every week.
        </p>

        {submitted ? (
          <div className="bg-green2/20 border border-green2/40 rounded-md py-3 px-5 inline-block">
            <p className="text-sm font-semibold text-green2">
              You&apos;re subscribed! Check your inbox to confirm.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex gap-2 max-w-md mx-auto">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
              className="flex-1 px-4 py-2.5 rounded-md bg-white/10 border border-white/20 text-white text-sm placeholder:text-white/40 focus:outline-none focus:border-white/50"
            />
            <button
              type="submit"
              className="px-5 py-2.5 rounded-md bg-red text-white font-condensed text-sm font-bold uppercase tracking-wide hover:bg-red-light transition-colors"
            >
              Subscribe
            </button>
          </form>
        )}
      </div>
    </section>
  )
}
