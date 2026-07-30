import { profile } from '@/lib/constants'
import { HiMail, HiAcademicCap } from 'react-icons/hi'
import { FaLinkedin, FaGithub } from 'react-icons/fa'

export default function Contact() {
  return (
    <section id="contact" className="relative py-28 px-4">
      <div className="max-w-4xl mx-auto text-center">
        <div className="text-center mb-16">
          <h2 className="text-sm uppercase tracking-widest text-blue-400 font-mono mb-3">Contact</h2>
          <h3 className="text-3xl md:text-5xl font-bold text-white">
            Let&apos;s <span className="gradient-text">Connect</span>
          </h3>
        </div>

        <div className="glass rounded-2xl p-8 md:p-12 max-w-2xl mx-auto">
          <p className="text-gray-400 mb-8">
            Whether you have a project idea, a job opportunity, or just want to connect — I&apos;m always open to a conversation.
          </p>

          <div className="flex flex-col gap-4 mb-8">
            <a
              href={`mailto:${profile.email}`}
              className="flex items-center justify-center gap-3 px-6 py-4 rounded-xl bg-gradient-to-r from-blue-500 to-purple-600 text-white font-medium hover:shadow-lg hover:shadow-blue-500/25 transition-all duration-300"
            >
              <HiMail className="w-5 h-5" />
              {profile.email}
            </a>
          </div>

          <div className="flex items-center justify-center gap-4">
            <a
              href={profile.linkedin}
              target="_blank"
              rel="noopener noreferrer"
              className="p-3 rounded-xl glass text-gray-400 hover:text-blue-400 hover:bg-white/5 transition-all duration-300"
            >
              <FaLinkedin className="w-6 h-6" />
            </a>
            <a
              href={`https://github.com/${profile.alias.toLowerCase().replace(/\s+/g, '')}`}
              target="_blank"
              rel="noopener noreferrer"
              className="p-3 rounded-xl glass text-gray-400 hover:text-white hover:bg-white/5 transition-all duration-300"
            >
              <FaGithub className="w-6 h-6" />
            </a>
            <a
              href={`mailto:${profile.email}`}
              className="p-3 rounded-xl glass text-gray-400 hover:text-pink-400 hover:bg-white/5 transition-all duration-300"
            >
              <HiMail className="w-6 h-6" />
            </a>
          </div>

          <div className="mt-8 pt-8 border-t border-white/5">
            <div className="flex items-center justify-center gap-2 text-gray-500 text-sm">
              <HiAcademicCap className="w-4 h-4" />
              <span>{profile.education[0].degree} — {profile.education[0].school}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
