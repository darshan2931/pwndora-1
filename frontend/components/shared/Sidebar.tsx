'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard, Map, Bot, User, ChevronRight,
  Shield, Zap, BookOpen, Trophy, Settings, FileText
} from 'lucide-react';
import { api } from '@/services/api';
import { useDashboardData } from '@/components/providers/DashboardDataProvider';

const NAV = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/roadmap', label: 'Roadmap', icon: Map },
  { href: '/mentor', label: 'AI Mentor', icon: Bot },
  { href: '/resume', label: 'Resume', icon: FileText },
  { href: '/profile', label: 'Profile', icon: User },
];

const SECONDARY = [
  { href: '/onboarding', label: 'Re-run Setup', icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { data } = useDashboardData();
  const profile = data?.profile || {};

  return (
    <aside className="fixed left-0 top-0 h-full w-56 bg-[#111113] border-r border-white/[0.06] flex flex-col z-40">
      {/* Logo */}
      <div className="px-4 py-5 border-b border-white/[0.06]">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-7 h-7 rounded-md bg-blue-500 flex items-center justify-center flex-shrink-0">
            <Shield className="w-4 h-4 text-white" />
          </div>
          <span className="font-semibold text-sm text-[#fafafa] tracking-tight">CyberPath AI</span>
        </Link>
      </div>

      {/* Profile chip */}
      <div className="px-3 pt-4 pb-2">
        <div className="flex items-center gap-2.5 px-2 py-2 rounded-lg bg-white/[0.04] border border-white/[0.06]">
          <div className="w-7 h-7 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center flex-shrink-0">
            <span className="text-xs font-bold text-blue-400">{profile?.avatarInitials || 'U'}</span>
          </div>
          <div className="min-w-0">
            <p className="text-xs font-medium text-[#fafafa] truncate">{profile?.name || 'Loading...'}</p>
            <p className="text-[10px] text-zinc-500 truncate">{profile?.targetRole || ''}</p>
          </div>
          <ChevronRight className="w-3 h-3 text-zinc-600 ml-auto flex-shrink-0" />
        </div>
      </div>

      {/* Readiness bar */}
      <div className="px-3 pb-4">
        <div className="px-2">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] text-zinc-500">Career Readiness</span>
            <span className="text-[10px] font-bold text-blue-400">{profile?.readiness || 0}%</span>
          </div>
          <div className="progress-bar">
            <div className="progress-bar-fill" style={{ width: `${profile?.readiness || 0}%` }} />
          </div>
        </div>
      </div>

      {/* Main nav */}
      <nav className="flex-1 px-3 space-y-0.5 overflow-y-auto no-scrollbar">
        <p className="text-label px-2 mb-2">Navigation</p>
        {NAV.map(item => {
          const Icon = item.icon;
          const active = pathname === item.href || pathname.startsWith(item.href + '/');
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`sidebar-link ${active ? 'sidebar-link-active' : ''}`}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {item.label}
              {item.href === '/mentor' && (
                <span className="ml-auto w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              )}
            </Link>
          );
        })}

        <div className="pt-4">
          <p className="text-label px-2 mb-2">Quick Stats</p>
          <div className="px-2 space-y-3">
            <div className="flex items-center gap-2">
              <Zap className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
              <span className="text-xs text-zinc-400">{profile?.currentStreak || 0} day streak</span>
            </div>
            <div className="flex items-center gap-2">
              <BookOpen className="w-3.5 h-3.5 text-blue-400 flex-shrink-0" />
              <span className="text-xs text-zinc-400">{profile?.totalStudyHours || 0}h studied</span>
            </div>
            <div className="flex items-center gap-2">
              <Trophy className="w-3.5 h-3.5 text-violet-400 flex-shrink-0" />
              <span className="text-xs text-zinc-400">{profile?.achievements?.length || 0} achievements</span>
            </div>
          </div>
        </div>
      </nav>

      {/* Bottom */}
      <div className="px-3 py-4 border-t border-white/[0.06] space-y-0.5">
        {SECONDARY.map(item => {
          const Icon = item.icon;
          return (
            <Link key={item.href} href={item.href} className="sidebar-link">
              <Icon className="w-4 h-4 flex-shrink-0" />
              {item.label}
            </Link>
          );
        })}
        <Link href="/" className="sidebar-link">
          <Shield className="w-4 h-4 flex-shrink-0" />
          Home
        </Link>
        <button onClick={() => api.logout()} className="sidebar-link w-full text-left text-red-400 hover:text-red-300">
          <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
          Log out
        </button>
      </div>
    </aside>
  );
}
