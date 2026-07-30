import { profile } from '@/lib/constants'

export default function Skills() {
  return (
    <section id="skills" className="relative py-28 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-sm uppercase tracking-widest text-pink-400 font-mono mb-3">Expertise</h2>
          <h3 className="text-3xl md:text-5xl font-bold text-white">
            Tech <span className="gradient-text">Stack</span>
          </h3>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {profile.skills.map((skill) => (
            <div
              key={skill.name}
              className="glass rounded-2xl p-5 text-center glass-hover transition-all duration-300 group"
            >
              <div className="relative w-16 h-16 mx-auto mb-4">
                <svg className="w-16 h-16 -rotate-90" viewBox="0 0 64 64">
                  <circle
                    cx="32" cy="32" r="28"
                    fill="none"
                    stroke="rgba(255,255,255,0.05)"
                    strokeWidth="4"
                  />
                  <circle
                    cx="32" cy="32" r="28"
                    fill="none"
                    stroke="url(#grad)"
                    strokeWidth="4"
                    strokeLinecap="round"
                    strokeDasharray={`${(skill.level / 100) * 176} 176`}
                    className="transition-all duration-1000"
                  />
                  <defs>
                    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#3b82f6" />
                      <stop offset="100%" stopColor="#8b5cf6" />
                    </linearGradient>
                  </defs>
                </svg>
                <span className="absolute inset-0 flex items-center justify-center text-sm font-bold text-white font-mono">
                  {skill.level}%
                </span>
              </div>
              <h4 className="text-sm font-medium text-gray-300 group-hover:text-white transition-colors">
                {skill.name}
              </h4>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
