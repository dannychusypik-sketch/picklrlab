import type { Article, Paddle, Player, Tournament } from '@/lib/types'

function JsonLdScript({ data }: { data: Record<string, unknown> }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  )
}

export function ArticleSchema({ article }: { article: Article }) {
  return (
    <JsonLdScript
      data={{
        '@context': 'https://schema.org',
        '@type': 'Article',
        headline: article.title,
        description: article.excerpt,
        author: { '@type': 'Organization', name: article.author || 'PicklrLab' },
        publisher: {
          '@type': 'Organization',
          name: 'PicklrLab',
          url: 'https://picklrlab.com',
        },
        datePublished: article.published_at,
        mainEntityOfPage: `https://picklrlab.com/news/${article.slug}`,
      }}
    />
  )
}

export function ProductSchema({ paddle }: { paddle: Paddle }) {
  return (
    <JsonLdScript
      data={{
        '@context': 'https://schema.org',
        '@type': 'Product',
        name: `${paddle.brand} ${paddle.name}`,
        description: paddle.verdict,
        brand: { '@type': 'Brand', name: paddle.brand },
        ...(paddle.price_usd && {
          offers: {
            '@type': 'Offer',
            price: paddle.price_usd,
            priceCurrency: 'USD',
            availability: 'https://schema.org/InStock',
          },
        }),
        ...(paddle.score_overall && {
          aggregateRating: {
            '@type': 'AggregateRating',
            ratingValue: paddle.score_overall,
            bestRating: 10,
            worstRating: 0,
            ratingCount: 1,
          },
        }),
      }}
    />
  )
}

export function PersonSchema({ player }: { player: Player }) {
  return (
    <JsonLdScript
      data={{
        '@context': 'https://schema.org',
        '@type': 'Person',
        name: player.name,
        description: player.bio,
        nationality: { '@type': 'Country', name: player.country },
        url: `https://picklrlab.com/players/${player.slug}`,
        ...(player.sponsor && { sponsor: { '@type': 'Organization', name: player.sponsor } }),
      }}
    />
  )
}

export function EventSchema({ tournament }: { tournament: Tournament }) {
  return (
    <JsonLdScript
      data={{
        '@context': 'https://schema.org',
        '@type': 'SportsEvent',
        name: tournament.name,
        description: tournament.description,
        location: {
          '@type': 'Place',
          name: tournament.location,
          address: { '@type': 'PostalAddress', addressCountry: tournament.country },
        },
        startDate: tournament.start_date,
        endDate: tournament.end_date,
        url: `https://picklrlab.com/tournaments/${tournament.slug}`,
      }}
    />
  )
}

export function FAQSchema({ questions }: { questions: { q: string; a: string }[] }) {
  return (
    <JsonLdScript
      data={{
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        mainEntity: questions.map(({ q, a }) => ({
          '@type': 'Question',
          name: q,
          acceptedAnswer: { '@type': 'Answer', text: a },
        })),
      }}
    />
  )
}

export function BreadcrumbSchema({ items }: { items: { name: string; url: string }[] }) {
  return (
    <JsonLdScript
      data={{
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        itemListElement: items.map((item, i) => ({
          '@type': 'ListItem',
          position: i + 1,
          name: item.name,
          item: item.url,
        })),
      }}
    />
  )
}

export function SportsOrgSchema() {
  return (
    <JsonLdScript
      data={{
        '@context': 'https://schema.org',
        '@type': 'SportsOrganization',
        name: 'PicklrLab',
        url: 'https://picklrlab.com',
        description: "The world's #1 pickleball authority. Rankings, lab-tested reviews, and AI-powered tools.",
        sport: 'Pickleball',
        foundingDate: '2025',
      }}
    />
  )
}

export function WebsiteSchema() {
  return (
    <JsonLdScript
      data={{
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        name: 'PicklrLab',
        description: "The World's #1 Pickleball Authority",
        url: 'https://picklrlab.com',
        publisher: { '@type': 'Organization', name: 'PicklrLab' },
      }}
    />
  )
}
