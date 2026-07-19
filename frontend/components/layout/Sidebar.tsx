"use client";

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: '📊' },
  { href: '/roadmap', label: 'Roadmap', icon: '🗺️' },
  { href: '/mentor', label: 'AI Mentor', icon: '🤖' },
  { href: '/projects', label: 'Projects', icon: '💻' },
  { href: '/settings', label: 'Settings', icon: '⚙️' },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-[var(--border)] bg-[var(--background)] min-h-[calc(100vh-4rem)]">
      <nav className="flex flex-col gap-2 p-4">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`
                flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors
                ${isActive 
                  ? 'bg-[var(--accent)] text-[var(--accent-foreground)]' 
                  : 'text-[var(--muted-foreground)] hover:bg-[var(--accent)]/50 hover:text-[var(--foreground)]'}
              `}
            >
              <span>{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
};
