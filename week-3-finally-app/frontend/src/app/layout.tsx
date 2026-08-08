import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'FinAlly Terminal',
  description: 'AI-Powered Market Data & Trading Workstation',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-terminal-bg text-gray-100 min-h-screen font-mono antialiased">
        {children}
      </body>
    </html>
  );
}
