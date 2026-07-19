'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Bell, Search, ChevronRight } from 'lucide-react';
import { api } from '@/services/api';
import { useEffect, useState } from 'react';

const BREADCRUMB_MAP: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/roadmap': 'Roadmap',
  '/mentor': 'AI Mentor',
  '/profile': 'Profile',
};

export default function TopBar() {
  const pathname = usePathname();
  const currentPage = BREADCRUMB_MAP[pathname] || 'CyberPath AI';
  const [profile, setProfile] = useState<any>(null);

  useEffect(() => {
    async function load() {
      try {
        const d = await api.getDashboardData();
        setProfile(d?.data?.profile || {});
      } catch (e) {
        setProfile({});
      }
    }
    load();
  }, []);

  return (
    <header className="fixed top-0 right-0 left-56 h-14 bg-[#09090b]/80 backdrop-blur-xl border-b border-white/[0.06] z-30 flex items-center px-6 gap-4">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm flex-1 min-w-0">
        <span className="text-zinc-500">CyberPath</span>
        <ChevronRight className="w-3.5 h-3.5 text-zinc-700 flex-shrink-0" />
        <span className="font-medium text-[#fafafa]">{currentPage}</span>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2">
        <button className="w-8 h-8 rounded-lg flex items-center justify-center text-zinc-500 hover:text-[#fafafa] hover:bg-white/[0.06] transition-colors">
          <Search className="w-4 h-4" />
        </button>
        <button className="relative w-8 h-8 rounded-lg flex items-center justify-center text-zinc-500 hover:text-[#fafafa] hover:bg-white/[0.06] transition-colors">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-blue-500" />
        </button>
        <Link href="/profile">
          <div className="w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center cursor-pointer hover:bg-blue-500/30 transition-colors">
            <span className="text-xs font-bold text-blue-400">{profile?.avatarInitials || 'U'}</span>
          </div>
        </Link>
      </div>
    </header>
  );
}
