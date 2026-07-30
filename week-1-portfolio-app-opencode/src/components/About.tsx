import { profile } from '@/lib/constants'
import { HiAcademicCap, HiBriefcase, HiLocationMarker } from 'react-icons/hi'

export default function About() {
  return (
    <section id="about" className="relative py-28 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-sm uppercase tracking-widest text-blue-400 font-mono mb-3">About Me</h2>
          <h3 className="text-3xl md:text-5xl font-bold text-white">
            Beyond the <span className="gradient-text">Code</span>
          </h3>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-12">
          {[
            { icon: HiBriefcase, label: 'Experience', value: '6+ Years', color: 'blue' },
            { icon: HiAcademicCap, label: 'Education', value: 'B.Sc in CSE', color: 'purple' },
            { icon: HiLocationMarker, label: 'Location', value: 'Chattogram, BD', color: 'pink' },
          ].map((stat) => (
            <div
              key={stat.label}
              className="glass rounded-2xl p-6 text-center glass-hover transition-all duration-300"
            >
              <stat.icon className={`w-8 h-8 mx-auto mb-3 text-${stat.color}-400`} />
              <div className="text-2xl font-bold text-white mb-1">{stat.value}</div>
              <div className="text-sm text-gray-500">{stat.label}</div>
            </div>
          ))}
        </div>

        <div className="glass rounded-2xl p-8 md:p-10">
          <p className="text-gray-300 text-lg leading-relaxed mb-6">
            {profile.summary}
          </p>
          <p className="text-gray-400 leading-relaxed">
            Currently, I work as a <span className="text-blue-400">Senior Software Engineer at SELISE Group</span>,
            where I build scalable solutions and lead technical initiatives. My tech stack includes
            C#, .NET Core, Angular, MSSQL, Azure DevOps, Docker, SignalR, and more.
            I&apos;m passionate about solving real-world problems and writing clean, maintainable code.
          </p>
          <div className="mt-6 flex flex-wrap gap-2">
            {profile.languages.map((lang) => (
              <span key={lang} className="px-3 py-1 rounded-full bg-white/5 text-xs text-gray-400 border border-white/5">
                {lang}
              </span>
            ))}
            {profile.certifications.map((cert) => (
              <span key={cert} className="px-3 py-1 rounded-full bg-blue-500/10 text-xs text-blue-400 border border-blue-500/20">
                {cert}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
