import Link from 'next/link'

const columns = [
  {
    title: 'Rankings',
    links: [
      { label: "Men's Singles", href: '/rankings?cat=mens_singles' },
      { label: "Women's Singles", href: '/rankings?cat=womens_singles' },
      { label: 'Mixed Doubles', href: '/rankings?cat=mixed_doubles' },
    ],
  },
  {
    title: 'Content',
    links: [
      { label: 'News', href: '/news' },
      { label: 'Reviews', href: '/reviews' },
      { label: 'Players', href: '/players' },
    ],
  },
  {
    title: 'Tools',
    links: [
      { label: 'Court Finder', href: '/courts' },
      { label: 'Paddle Compare', href: '/tools/compare' },
      { label: 'Tournaments', href: '/tournaments' },
    ],
  },
  {
    title: 'About',
    links: [
      { label: 'About Us', href: '/about' },
      { label: 'Contact', href: '/about#contact' },
      { label: 'Privacy', href: '/about#privacy' },
    ],
  },
]

export default function Footer() {
  return (
    <footer className="bg-ink text-white mt-12">
      <div className="max-w-site mx-auto px-5 py-10">
        {/* Top section */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-10">
          {columns.map((col) => (
            <div key={col.title}>
              <h4 className="font-condensed text-sm font-bold uppercase tracking-wide text-white/60 mb-3">
                {col.title}
              </h4>
              <ul className="space-y-2">
                {col.links.map((link) => (
                  <li key={link.href}>
                    <Link href={link.href} className="text-sm text-white/80 hover:text-white transition-colors">
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom */}
        <div className="border-t border-white/10 pt-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <Link href="/" className="font-condensed text-xl font-bold uppercase tracking-tight">
            Picklr<span className="text-red">Lab</span>
          </Link>
          <p className="text-xs text-white/40">
            &copy; 2026 PicklrLab. All rights reserved. The world&apos;s #1 pickleball authority.
          </p>
        </div>
      </div>
    </footer>
  )
}
