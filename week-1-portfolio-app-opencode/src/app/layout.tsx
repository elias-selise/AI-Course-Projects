import type { Metadata } from 'next'
import './globals.css'
import Navbar from '@/components/Navbar'
import ChatBot from '@/components/ChatBot'

export const metadata: Metadata = {
  title: 'Elias Hridoy | Senior Software Engineer',
  description: 'Professional portfolio of Md. Elias Kanchon - Senior Software Engineer specializing in .NET, Angular, and Azure DevOps',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className="min-h-screen">
        <Navbar />
        {children}
        <ChatBot />
      </body>
    </html>
  )
}
