import { profile } from '@/lib/constants'
import { HiBriefcase } from 'react-icons/hi'

export default function Experience() {
  return (
    <section id="experience" className="relative py-28 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-sm uppercase tracking-widest text-purple-400 font-mono mb-3">Career Journey</h2>
          <h3 className="text-3xl md:text-5xl font-bold text-white">
            Where I&apos;ve <span className="gradient-text">Been</span>
          </h3>
        </div>

        <div className="relative">
          <div className="absolute left-0 md:left-1/2 top-0 bottom-0 w-px timeline-line -translate-x-1/2" />

          <div className="space-y-12">
            {profile.experience.map((exp, idx) => (
              <div key={idx} className={`relative flex flex-col md:flex-row gap-6 ${idx % 2 === 0 ? 'md:flex-row' : 'md:flex-row-reverse'}`}>
                <div className={`flex-1 ${idx % 2 === 0 ? 'md:text-right md:pr-12' : 'md:text-left md:pl-12'}`}>
                  <div className="glass rounded-2xl p-6 glass-hover transition-all duration-300">
                    <div className="flex items-center gap-2 mb-2 md:justify-end">
                      <HiBriefcase className={`w-4 h-4 ${idx === 0 ? 'text-blue-400' : 'text-purple-400'}`} />
                      <span className="text-xs font-mono text-gray-500">{exp.period}</span>
                    </div>
                    <h4 className={`text-lg font-bold text-white mb-1 ${idx % 2 === 0 ? 'md:text-right' : ''}`}>
                      {exp.role}
                    </h4>
                    <p className={`text-sm ${idx === 0 ? 'text-blue-400' : 'text-purple-400'} font-medium mb-1 ${idx % 2 === 0 ? 'md:text-right' : ''}`}>
                      {exp.company}
                    </p>
                    <p className={`text-xs text-gray-600 mb-3 ${idx % 2 === 0 ? 'md:text-right' : ''}`}>
                      {exp.location}
                    </p>
                    {exp.highlights.length > 0 && (
                      <ul className={`space-y-2 ${idx % 2 === 0 ? 'md:text-right' : ''}`}>
                        {exp.highlights.map((h, i) => (
                          <li key={i} className="text-sm text-gray-400 leading-relaxed">
                            {h}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>

                <div className="absolute left-0 md:left-1/2 w-4 h-4 -translate-x-1/2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full border-4 border-[#0a0a0f] z-10" />

                <div className="flex-1 hidden md:block" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
