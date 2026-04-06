interface SportBannerProps {
  label: string
  color: string
}

export default function SportBanner({ label, color }: SportBannerProps) {
  return (
    <div className="py-3 mt-8" style={{ backgroundColor: color }}>
      <div className="max-w-site mx-auto px-5">
        <h2 className="font-condensed text-lg font-bold uppercase tracking-wide text-white">
          {label}
        </h2>
      </div>
    </div>
  )
}
