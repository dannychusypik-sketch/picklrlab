import Link from 'next/link'

const links = [
  { label: 'Rankings', href: '/rankings' },
  { label: 'News', href: '/news' },
  { label: 'Reviews', href: '/reviews' },
  { label: 'Players', href: '/players' },
  { label: 'Tournaments', href: '/tournaments' },
  { label: 'Courts', href: '/courts' },
  { label: 'Tools', href: '/tools' },
]

export default function Nav() {
  return (
    <header className="bg-bg border-b border-bd2 sticky top-0 z-50">
      <div className="max-w-site mx-auto px-5 flex items-center justify-between h-14">
        {/* Logo */}
        <Link href="/" className="font-condensed text-2xl font-bold uppercase tracking-tight text-ink">
          Picklr<span className="text-red">Lab</span>
        </Link>

        {/* Links */}
        <nav className="hidden md:flex items-center gap-5">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="font-condensed text-sm font-semibold uppercase tracking-wide text-ink3 hover:text-ink transition-colors"
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Mobile menu button */}
        <button className="md:hidden w-8 h-8 flex flex-col items-center justify-center gap-1" aria-label="Menu">
          <span className="block w-5 h-0.5 bg-ink" />
          <span className="block w-5 h-0.5 bg-ink" />
          <span className="block w-5 h-0.5 bg-ink" />
        </button>
      </div>
    </header>
  )
}
