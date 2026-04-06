'use client'

import { useState } from 'react'

export default function ContactForm() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
  const [submitted, setSubmitted] = useState(false)

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    // In production, this would POST to an API endpoint
    setSubmitted(true)
  }

  if (submitted) {
    return (
      <div className="max-w-lg p-6 bg-bg2 rounded-lg text-center">
        <h3 className="font-condensed text-lg font-bold uppercase mb-2">Message Sent</h3>
        <p className="text-sm text-ink3">Thank you for reaching out. We will get back to you soon.</p>
        <button
          onClick={() => { setSubmitted(false); setName(''); setEmail(''); setMessage('') }}
          className="text-blue text-sm font-semibold mt-3 hover:underline"
        >
          Send another message
        </button>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-lg space-y-4">
      <div>
        <label className="font-condensed text-xs font-bold uppercase tracking-wider block mb-1">
          Name
        </label>
        <input
          type="text"
          required
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue/30"
        />
      </div>
      <div>
        <label className="font-condensed text-xs font-bold uppercase tracking-wider block mb-1">
          Email
        </label>
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue/30"
        />
      </div>
      <div>
        <label className="font-condensed text-xs font-bold uppercase tracking-wider block mb-1">
          Message
        </label>
        <textarea
          required
          rows={5}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          className="w-full border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue/30 resize-none"
        />
      </div>
      <button
        type="submit"
        className="font-condensed text-sm font-bold uppercase tracking-wide bg-blue text-white px-6 py-2.5 rounded-lg hover:bg-blue-hover transition"
      >
        Send Message
      </button>
    </form>
  )
}
