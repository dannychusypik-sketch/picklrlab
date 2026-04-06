import { countryFlag } from '@/lib/formatters'

interface Props {
  code: string
}

export default function CountryBadge({ code }: Props) {
  return (
    <span className="inline-flex items-center gap-1 text-xs text-ink4">
      <span>{countryFlag(code)}</span>
      <span>{code.toUpperCase()}</span>
    </span>
  )
}
