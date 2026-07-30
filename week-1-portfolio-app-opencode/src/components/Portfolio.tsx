import { HiFolderOpen } from 'react-icons/hi'

const projects = [
  {
    title: 'CI/CD Pipeline Automation',
    desc: 'Azure DevOps pipelines reducing deployment time by 40% for .NET and Angular applications.',
    tags: ['Azure DevOps', '.NET', 'Angular'],
  },
  {
    title: 'Real-Time Notification System',
    desc: 'SignalR-based real-time notifications improving message delivery speed by 35%.',
    tags: ['SignalR', '.NET Core', 'JavaScript'],
  },
  {
    title: 'GDS & MFS API Integration',
    desc: 'Global Distribution System and Mobile Financial Services APIs for real-time travel booking.',
    tags: ['REST APIs', 'SOAP', 'Integration'],
  },
  {
    title: 'SWIFT MT to MX Migration',
    desc: 'Core banking platform SWIFT message format migration ensuring ISO20022 compliance.',
    tags: ['SWIFT', 'Banking', 'Migration'],
  },
]

export default function Portfolio() {
  return (
    <section id="portfolio" className="relative py-28 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-sm uppercase tracking-widest text-blue-400 font-mono mb-3">Portfolio</h2>
          <h3 className="text-3xl md:text-5xl font-bold text-white">
            Featured <span className="gradient-text">Projects</span>
          </h3>
          <p className="text-gray-500 mt-4 max-w-xl mx-auto">
            Selected projects demonstrating enterprise-scale solutions and technical leadership.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {projects.map((project) => (
            <div
              key={project.title}
              className="glass rounded-2xl p-6 glass-hover transition-all duration-300 group cursor-pointer"
            >
              <div className="flex items-start gap-4">
                <div className="p-3 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-600/20 text-blue-400 group-hover:scale-110 transition-transform">
                  <HiFolderOpen className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <h4 className="text-lg font-bold text-white mb-2 group-hover:text-blue-400 transition-colors">
                    {project.title}
                  </h4>
                  <p className="text-sm text-gray-400 leading-relaxed mb-4">
                    {project.desc}
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {project.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2.5 py-1 rounded-lg bg-white/5 text-xs text-gray-500 border border-white/5"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
