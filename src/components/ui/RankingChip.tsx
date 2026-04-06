interface Props {
  delta: number
}

export default function RankingChip({ delta }: Props) {
  if (delta > 0) {
    return <span className="font-body text-xs font-semibold text-green2">&#9650; {delta}</span>
  }
  if (delta < 0) {
    return <span className="font-body text-xs font-semibold text-red">&#9660; {Math.abs(delta)}</span>
  }
  return <span className="font-body text-xs font-semibold text-ink5">&mdash;</span>
}
