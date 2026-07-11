import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'CyberPath AI',
  description: 'AI-powered Cybersecurity Career Intelligence Platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900">
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
            <a href="/" className="text-xl font-bold text-primary">CyberPath AI</a>
            <div className="flex gap-6 text-sm">
              <a href="/explore" className="hover:text-primary">Explore Careers</a>
              <a href="/upload" className="hover:text-primary">Upload Resume</a>
              <a href="/dashboard" className="hover:text-primary">Dashboard</a>
              <a href="/roadmap" className="hover:text-primary">Roadmap</a>
              <a href="/mentor" className="hover:text-primary">AI Mentor</a>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
