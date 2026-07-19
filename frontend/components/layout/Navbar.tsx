import React from 'react';
import Link from 'next/link';

export const Navbar: React.FC = () => {
  return (
    <nav className="sticky top-0 z-50 w-full border-b border-[var(--border)] bg-[var(--background)]/80 backdrop-blur">
      <div className="flex h-16 items-center px-6">
        <Link href="/" className="flex items-center space-x-2">
          <span className="text-xl font-bold text-[var(--foreground)] tracking-tight">CyberPath <span className="text-[var(--primary)]">AI</span></span>
        </Link>
        <div className="ml-auto flex items-center space-x-4">
          <Link href="/login" className="text-sm font-medium text-[var(--muted-foreground)] hover:text-[var(--foreground)]">
            Log in
          </Link>
          <Link href="/register" className="text-sm font-medium bg-[var(--primary)] text-[var(--primary-foreground)] hover:bg-[var(--primary)]/90 px-4 py-2 rounded-md transition-colors">
            Get Started
          </Link>
        </div>
      </div>
    </nav>
  );
};
