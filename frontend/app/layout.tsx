import type { Metadata } from 'next';
import Navbar from '@/components/Navbar';
import ErrorBoundary from '@/components/ui/ErrorBoundary';
import { ThemeProvider } from '@/components/ThemeProvider';
import './globals.css';

export const metadata: Metadata = {
  title: 'CyberPath AI - Cybersecurity Career Intelligence',
  description: 'AI-powered platform for personalized cybersecurity career guidance, skill assessment, and learning roadmaps.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider>
          <Navbar />
          <main className="min-h-[calc(100vh-4rem)]">
            <ErrorBoundary>
              {children}
            </ErrorBoundary>
          </main>
        </ThemeProvider>
      </body>
    </html>
  );
}
