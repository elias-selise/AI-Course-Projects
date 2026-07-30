import { profile } from '@/lib/constants'

export default function Footer() {
  return (
    <footer className="border-t border-white/5 py-8 px-4">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <span className="text-sm font-mono gradient-text font-bold">EH.dev</span>
          <span className="text-gray-600 text-sm">|</span>
          <span className="text-gray-500 text-xs">{profile.title}</span>
        </div>
        <p className="text-gray-600 text-xs">
          &copy; {new Date().getFullYear()} {profile.alias}. Crafted with Next.js & Tailwind CSS.
        </p>
      </div>
    </footer>
  )
}
