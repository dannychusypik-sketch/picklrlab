import type { Metadata } from 'next'
import Nav from '@/components/layout/Nav'
import Footer from '@/components/layout/Footer'
import ContactForm from '@/components/about/ContactForm'

export const metadata: Metadata = {
  title: 'About',
}

const tiers = [
  {
    name: 'Starter',
    price: '$500/mo',
    features: ['Banner ads on news pages', 'Logo in footer', '10k impressions/mo'],
  },
  {
    name: 'Pro',
    price: '$1,500/mo',
    features: ['Banner + sidebar ads', 'Sponsored article (1/mo)', 'Logo in footer', '50k impressions/mo', 'Social media mention'],
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    features: ['All Pro features', 'Homepage takeover', 'Custom integrations', 'Dedicated account manager', 'Event sponsorship'],
  },
]

export default function AboutPage() {
  return (
    <>
      <Nav />
      <main className="max-w-site mx-auto px-5 py-6">
        {/* Mission */}
        <section className="mb-12">
          <h1 className="font-condensed text-3xl font-bold uppercase border-b-2 border-ink pb-2.5">
            About PicklrLab
          </h1>
          <div className="max-w-[720px] mt-6">
            <h2 className="font-condensed text-xl font-bold uppercase mb-3">Our Mission</h2>
            <p className="text-base text-ink2 leading-relaxed mb-4">
              PicklrLab is the world&apos;s leading pickleball authority, delivering comprehensive coverage of professional pickleball through rankings, reviews, news, and tools. Our mission is to grow the sport globally by providing the most accurate, unbiased, and insightful content available.
            </p>
            <p className="text-base text-ink2 leading-relaxed">
              Founded by passionate pickleball players, we combine data-driven analysis with on-the-ground reporting to deliver content that serves everyone from casual players to touring professionals.
            </p>
          </div>
        </section>

        {/* Methodology */}
        <section className="mb-12">
          <h2 className="font-condensed text-xl font-bold uppercase border-b-2 border-ink pb-2.5 mb-6">
            Our Methodology
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-5 bg-bg2 rounded-lg">
              <h3 className="font-condensed text-md font-bold uppercase mb-2">Rankings</h3>
              <p className="text-sm text-ink3 leading-relaxed">
                Our world rankings use a points-based system incorporating tournament results, head-to-head records, and performance metrics. Rankings are updated quarterly.
              </p>
            </div>
            <div className="p-5 bg-bg2 rounded-lg">
              <h3 className="font-condensed text-md font-bold uppercase mb-2">Reviews</h3>
              <p className="text-sm text-ink3 leading-relaxed">
                Every paddle review involves 20+ hours of on-court testing by multiple testers. We measure spin rate, power, control, and feel using standardized protocols.
              </p>
            </div>
            <div className="p-5 bg-bg2 rounded-lg">
              <h3 className="font-condensed text-md font-bold uppercase mb-2">Reporting</h3>
              <p className="text-sm text-ink3 leading-relaxed">
                Our editorial team covers events on-site and maintains relationships with players, coaches, and tournament organizers for first-hand reporting.
              </p>
            </div>
          </div>
        </section>

        {/* Contact form */}
        <section className="mb-12">
          <h2 className="font-condensed text-xl font-bold uppercase border-b-2 border-ink pb-2.5 mb-6">
            Contact Us
          </h2>
          <ContactForm />
        </section>

        {/* Advertise tiers */}
        <section className="mb-12">
          <h2 className="font-condensed text-xl font-bold uppercase border-b-2 border-ink pb-2.5 mb-6">
            Advertise With Us
          </h2>
          <p className="text-sm text-ink3 mb-6 max-w-[720px]">
            Reach the most engaged pickleball audience on the internet. Our readers are active players who make purchasing decisions based on our reviews and recommendations.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {tiers.map((tier) => (
              <div
                key={tier.name}
                className="border border-border rounded-lg p-6 hover:shadow-md transition-shadow"
              >
                <h3 className="font-condensed text-lg font-bold uppercase">{tier.name}</h3>
                <p className="font-condensed text-2xl font-bold text-blue mt-1">{tier.price}</p>
                <ul className="mt-4 space-y-2">
                  {tier.features.map((f) => (
                    <li key={f} className="text-sm text-ink3 flex items-start gap-2">
                      <span className="text-green2 mt-0.5 shrink-0">&#10003;</span>
                      {f}
                    </li>
                  ))}
                </ul>
                <button className="w-full mt-6 font-condensed text-sm font-bold uppercase tracking-wide bg-ink text-white py-2.5 rounded-lg hover:bg-ink2 transition">
                  Get Started
                </button>
              </div>
            ))}
          </div>
        </section>
      </main>
      <Footer />
    </>
  )
}
