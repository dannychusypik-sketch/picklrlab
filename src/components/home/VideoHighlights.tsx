import SectionHeader from '@/components/ui/SectionHeader'

const videos = [
  { id: '1', title: 'Ben Johns Incredible ATP Winner', meta: 'Desert Ridge Open', duration: '0:45' },
  { id: '2', title: 'ALW Perfect Third Shot Drop', meta: 'PPA Tour', duration: '0:32' },
  { id: '3', title: 'Staksrud Erne Compilation', meta: 'Highlights', duration: '2:15' },
  { id: '4', title: 'Best Rally of the Week', meta: 'Weekly Top Plays', duration: '1:08' },
  { id: '5', title: 'McGuffin Power Drive Montage', meta: 'PPA Tour', duration: '1:45' },
  { id: '6', title: 'Top 5 Dinks of March 2026', meta: 'Monthly Best', duration: '3:22' },
]

export default function VideoHighlights() {
  return (
    <div className="mt-8">
      <div className="max-w-site mx-auto px-5">
        <SectionHeader title="RECENT HIGHLIGHTS" href="/highlights" linkText="View All" />
      </div>
      <div className="flex gap-2.5 overflow-x-auto scrollbar-hide px-5 max-w-site mx-auto py-3.5">
        {videos.map((video) => (
          <div
            key={video.id}
            className="w-[168px] flex-shrink-0 rounded-md overflow-hidden bg-bg hover:shadow-lg transition-shadow cursor-pointer"
          >
            {/* Thumbnail */}
            <div className="w-full h-[300px] bg-ink2 flex items-center justify-center relative">
              {/* Play button */}
              <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center text-white text-xl hover:scale-110 transition-transform">
                &#9654;
              </div>
              {/* Duration */}
              <span className="absolute bottom-2 right-2 bg-black/70 text-white text-2xs px-1.5 py-0.5 rounded">
                {video.duration}
              </span>
            </div>
            {/* Info */}
            <div className="p-2.5">
              <p className="font-body text-sm font-bold leading-snug">{video.title}</p>
              <p className="text-xs text-ink4 mt-1">{video.meta}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
