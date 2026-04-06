const items = [
  'PPA Desert Ridge Open — LIVE NOW',
  "Ben Johns leads Men's Singles Final",
  'MLP Season 4 kicks off April 10 in Dallas',
  'New Joola Gen 3 paddles available now',
  'Vietnam Open announced for May 2026',
]

export default function Ticker() {
  return (
    <div className="bg-ink text-white overflow-hidden whitespace-nowrap">
      <div className="animate-ticker inline-block py-1.5">
        {items.map((item, i) => (
          <span key={i} className="font-condensed text-xs uppercase tracking-wider mx-8">
            {item}
            <span className="text-red ml-8">&bull;</span>
          </span>
        ))}
      </div>
    </div>
  )
}
