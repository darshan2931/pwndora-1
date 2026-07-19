import Link from 'next/link';

// Simple marketing navbar
function MarketingNav() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/[0.06] bg-[#09090b]/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-14 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-semibold text-sm text-[#fafafa]">
          <div className="w-6 h-6 rounded-md bg-blue-500 flex items-center justify-center">
            <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          CyberPath AI
        </Link>
        <div className="flex items-center gap-6">
          <Link href="/dashboard" className="text-sm text-zinc-400 hover:text-[#fafafa] transition-colors">Dashboard</Link>
          <Link href="/roadmap" className="text-sm text-zinc-400 hover:text-[#fafafa] transition-colors hidden sm:block">Roadmap</Link>
          <Link href="/mentor" className="text-sm text-zinc-400 hover:text-[#fafafa] transition-colors hidden sm:block">Mentor</Link>
          <Link href="/onboarding" className="px-3 py-1.5 rounded-lg bg-white text-zinc-900 text-sm font-medium hover:bg-zinc-100 transition-colors">
            Get Started
          </Link>
        </div>
      </div>
    </nav>
  );
}

export default function MarketingLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[#09090b] text-[#fafafa]">
      <MarketingNav />
      {children}
    </div>
  );
}
