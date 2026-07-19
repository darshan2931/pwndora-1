import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'CyberPath AI — Cybersecurity Career Copilot',
  description: 'The AI-powered career operating system for cybersecurity professionals.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className="bg-[#09090b] text-[#fafafa] antialiased">
        {children}
      </body>
    </html>
  );
}
