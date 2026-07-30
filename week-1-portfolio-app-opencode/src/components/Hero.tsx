import { profile } from '@/lib/constants'
import { HiArrowDown } from 'react-icons/hi'

export default function Hero() {
  const initials = profile.alias.split(' ').map(n => n[0]).join('')

  return (
    <section id="home" className="relative min-h-screen flex items-center justify-center hero-grid overflow-hidden">
      <div className="floating-shape w-96 h-96 bg-blue-500 top-20 -left-20" />
      <div className="floating-shape w-80 h-80 bg-purple-500 bottom-20 -right-20" />
      <div className="floating-shape w-64 h-64 bg-pink-500 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />

      <div className="relative z-10 text-center px-4 max-w-4xl mx-auto">
        <div className="mb-8 inline-block">
          <div className="w-28 h-28 md:w-36 md:h-36 rounded-full bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 p-[3px] mx-auto animate-float">
            <div className="w-full h-full rounded-full bg-[#0a0a0f] flex items-center justify-center">
              <span className="text-3xl md:text-5xl font-bold gradient-text font-mono">{initials}</span>
            </div>
          </div>
        </div>

        <div className="space-y-4 animate-fade-in">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass text-sm text-blue-400 mb-4">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            Available for opportunities
          </div>

          <h1 className="text-4xl md:text-7xl font-bold tracking-tight">
            <span className="text-white">Hi, I&apos;m </span>
            <span className="gradient-text text-shadow">{profile.alias}</span>
          </h1>

          <p className="text-xl md:text-2xl text-gray-400 font-light max-w-2xl mx-auto">
            {profile.title} crafting enterprise solutions with{' '}
            <span className="text-blue-400 font-medium">.NET</span>,{' '}
            <span className="text-purple-400 font-medium">Angular</span>, and{' '}
            <span className="text-pink-400 font-medium">Cloud</span>
          </p>

          <p className="text-gray-500 text-base max-w-xl mx-auto leading-relaxed">
            {profile.summary}
          </p>

          <div className="flex items-center justify-center gap-4 pt-4">
            <a
              href="#experience"
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 text-white font-medium text-sm hover:shadow-lg hover:shadow-blue-500/25 transition-all duration-300 hover:scale-105"
            >
              View My Journey
            </a>
            <a
              href={profile.linkedin}
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-3 rounded-xl glass text-gray-300 font-medium text-sm hover:bg-white/10 hover:text-white transition-all duration-300"
            >
              LinkedIn
            </a>
          </div>
        </div>

        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce">
          <HiArrowDown className="text-gray-500 w-5 h-5" />
        </div>
      </div>
    </section>
  )
}
