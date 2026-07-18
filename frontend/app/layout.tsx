import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import ErrorBoundary from '@/components/ui/ErrorBoundary';
import { ThemeProvider } from '@/components/ThemeProvider';
import { ToastProvider } from '@/components/ui/toast/toast-provider';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

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
    <html lang="en" className={inter.className} suppressHydrationWarning>
      <body>
        <ThemeProvider>
          <ToastProvider>
              <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:top-2 focus:left-2 focus:bg-primary focus:text-white focus:px-4 focus:py-2 focus:rounded-lg">
                Skip to content
              </a>
              <Navbar />
              <main id="main-content" className="min-h-[calc(100vh-8rem)]">
                <ErrorBoundary>
                  {children}
                </ErrorBoundary>
              </main>
              <Footer />
          </ToastProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
