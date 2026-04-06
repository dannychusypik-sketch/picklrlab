import Link from 'next/link'

interface SectionHeaderProps {
  title: string
  href?: string
  linkText?: string
}

export default function SectionHeader({ title, href, linkText }: SectionHeaderProps) {
  return (
    <div className="flex items-center justify-between py-4 border-b border-bd2">
      <h2 className="font-condensed text-xl font-bold uppercase tracking-tight text-ink">
        {title}
      </h2>
      {href && linkText && (
        <Link
          href={href}
          className="font-body text-xs font-semibold text-blue hover:text-blue-hover uppercase tracking-wide"
        >
          {linkText}
        </Link>
      )}
    </div>
  )
}
