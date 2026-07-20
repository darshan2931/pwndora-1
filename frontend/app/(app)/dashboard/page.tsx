'use client';

import Link from 'next/link';
import {
  Target, Zap, BookOpen, Bot, Map, Trophy,
  ArrowRight, Clock, TrendingUp, CheckCircle2,
  Circle, Flame, Star
} from 'lucide-react';
import { api } from '@/services/api';
import { useEffect, useState } from 'react';

// ─── Sub-components ───────────────────────────────────────────────────────────

function StatCard({ label, value, sub, icon: Icon, color = 'blue' }: {
  label: string; value: string | number; sub?: string;
  icon: React.ComponentType<{ className?: string }>;
  color?: 'blue' | 'emerald' | 'amber' | 'violet';
}) {
  const colors = {
    blue: 'text-blue-400 bg-blue-500/10',
    emerald: 'text-emerald-400 bg-emerald-500/10',
    amber: 'text-amber-400 bg-amber-500/10',
    violet: 'text-violet-400 bg-violet-500/10',
  };
  return (
    <div className="surface p-5">
      <div className="flex items-start justify-between mb-3">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${colors[color]}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className="text-2xl font-bold text-[#fafafa] tracking-tight">{value}</div>
      <div className="text-xs text-zinc-500 mt-0.5">{label}</div>
      {sub && <div className="text-xs text-zinc-600 mt-1">{sub}</div>}
    </div>
  );
}

const DAYS_ABBR = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const todayAbbr = DAYS_ABBR[new Date().getDay()];

function WeeklyBar({ hours, goal, day }: { hours: number; goal: number; day: string }) {
  const pct = Math.min((hours / goal) * 100, 100);
  const isToday = day === todayAbbr;
  return (
    <div className="flex flex-col items-center gap-1.5">
      <div className="relative h-16 w-6 bg-white/[0.04] rounded-sm overflow-hidden">
        <div
          className={`absolute bottom-0 left-0 right-0 rounded-sm transition-all duration-700 ${isToday ? 'bg-blue-500' : hours > 0 ? 'bg-zinc-600' : ''}`}
          style={{ height: `${pct}%` }}
        />
      </div>
      <span className={`text-[10px] ${isToday ? 'text-[#fafafa] font-medium' : 'text-zinc-600'}`}>{day}</span>
    </div>
  );
}

function RoadmapPreview({ roadmap }: { roadmap: any[] }) {
  const nodes = (roadmap || []).slice(0, 5);
  return (
    <div className="flex items-center gap-1">
      {nodes.map((node, i) => (
        <div key={node.id} className="flex items-center gap-1">
          <div className={`flex items-center justify-center w-6 h-6 rounded-full border transition-colors
            ${node.status === 'completed' ? 'bg-emerald-500 border-emerald-500' :
              node.status === 'in-progress' ? 'bg-blue-500 border-blue-500' :
              node.status === 'available' ? 'border-zinc-600 bg-[#111113]' :
              'border-zinc-800 bg-[#111113]'}`}
            title={node.title}
          >
            {node.status === 'completed' ? (
              <CheckCircle2 className="w-3 h-3 text-white" />
            ) : node.status === 'in-progress' ? (
              <div className="w-2 h-2 rounded-full bg-white animate-pulse" />
            ) : (
              <Circle className="w-3 h-3 text-zinc-700" />
            )}
          </div>
          {i < nodes.length - 1 && (
            <div className={`h-px w-4 ${node.status === 'completed' ? 'bg-emerald-500/50' : 'bg-zinc-800'}`} />
          )}
        </div>
      ))}
      <span className="ml-2 text-xs text-zinc-500">+{Math.max(0, (roadmap?.length || 0) - 5)} more</span>
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const d = await api.getDashboardData();
        setData(d.data);
      } catch (e: any) {
        console.error(e);
        setError(e?.message || 'Failed to load dashboard data');
      }
    }
    loadData();
  }, []);

  if (error) return (
    <div className="p-8 text-center">
      <div className="text-red-400 mb-2">Failed to load dashboard</div>
      <div className="text-zinc-500 text-sm mb-4">{error}</div>
      <button onClick={() => window.location.reload()} className="px-4 py-2 rounded-lg bg-blue-500/20 text-blue-400 text-sm hover:bg-blue-500/30 transition-colors">
        Retry
      </button>
    </div>
  );

  if (!data || !data.profile) return <div className="p-8 text-white animate-pulse">Loading dashboard...</div>;

  const { profile, roadmap, mentorContext, weeklyProgress, dailyMission } = data;
  
  const mission = dailyMission || { 
    node: { title: 'Complete Setup', description: 'Finish your onboarding to get your first mission.', difficulty: 'Beginner', resources: [] },
    estimatedMinutes: 15
  };
  const completed = roadmap?.filter((n: any) => n.status === 'completed').length || 0;
  const inProgress = roadmap?.filter((n: any) => n.status === 'in-progress').length || 0;
  const total = roadmap?.length || 0;

  const weeklyHoursStudied = (weeklyProgress || []).reduce((s: number, d: any) => s + (d.hours || 0), 0);
  const weeklyGoal = profile.weeklyStudyHours || 10;
  const weeklyPct = weeklyGoal ? Math.round((weeklyHoursStudied / weeklyGoal) * 100) : 0;

  const greeting = (() => {
    const h = new Date().getHours();
    if (h < 12) return 'Good morning';
    if (h < 17) return 'Good afternoon';
    return 'Good evening';
  })();

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">

      {/* ── Welcome Banner ─────────────────────────────────────────────────── */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[#fafafa] tracking-tight">
            {greeting}, {profile.email?.split('@')[0] || profile.name || 'User'}
          </h1>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-blue-400 font-medium">{profile.targetRole || 'Penetration Tester'}</span>
            <span className="text-zinc-500">•</span>
            <span className="text-emerald-400 font-medium">{profile.experience || 'Beginner'}</span>
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20">
          <Flame className="w-3.5 h-3.5 text-amber-400" />
          <span className="text-xs font-semibold text-amber-400">{profile.currentStreak} day streak</span>
        </div>
      </div>

      {/* ── Stats ──────────────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Career Readiness" value={`${profile.readiness}%`} icon={Target} color="blue" sub="Looking good!" />
        <StatCard label="Study Streak" value={`${profile.currentStreak} days`} icon={Zap} color="amber" sub={`Best: ${profile.longestStreak} days`} />
        <StatCard label="Hours Studied" value={`${profile.totalStudyHours}h`} icon={BookOpen} color="emerald" sub="This month" />
        <StatCard label="Achievements" value={profile.achievements?.length || 0} icon={Trophy} color="violet" sub={`${profile.knownSkills?.length || 0} skills confirmed`} />
      </div>

      {/* ── Main grid ──────────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">

        {/* Today's Mission */}
        <div className="lg:col-span-2 surface p-6">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
              <span className="text-label">Today&apos;s Mission</span>
            </div>
            <span className="badge-blue">Active</span>
          </div>

          <div className="mb-4">
            <h2 className="text-xl font-bold text-[#fafafa] mb-1">{mission.node.title}</h2>
            <p className="text-sm text-zinc-400 leading-relaxed">{mission.node.description}</p>
          </div>

          <div className="flex items-center gap-4 text-sm text-zinc-500 mb-6">
            <div className="flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5" />
              <span>{mission.estimatedMinutes} min</span>
            </div>
            <div className="flex items-center gap-1.5">
              <TrendingUp className="w-3.5 h-3.5" />
              <span>{mission.node.difficulty}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Star className="w-3.5 h-3.5" />
              <span>{mission.node.resources?.length || 0} resources</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/roadmap"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium transition-colors"
            >
              Continue Learning
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
            <Link
              href="/mentor"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/[0.06] hover:bg-white/[0.10] text-zinc-300 text-sm font-medium transition-colors border border-white/[0.06]"
            >
              <Bot className="w-3.5 h-3.5" />
              Ask Mentor
            </Link>
          </div>
        </div>

        {/* AI Mentor Card */}
        <div className="surface p-5 flex flex-col">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center">
              <Bot className="w-4 h-4 text-blue-400" />
            </div>
            <div>
              <div className="text-sm font-medium text-[#fafafa]">AI Mentor</div>
              <div className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                <span className="text-xs text-zinc-500">Online</span>
              </div>
            </div>
          </div>

          <div className="flex-1 rounded-lg bg-white/[0.03] border border-white/[0.06] p-4 text-sm text-zinc-300 leading-relaxed mb-4">
            You completed <span className="text-[#fafafa] font-medium">Networking Fundamentals</span> yesterday. 
            Today&apos;s goal is <span className="text-blue-400 font-medium">HTTP Authentication</span> — 
            estimated 40 minutes. Ready when you are.
          </div>

          <Link
            href="/mentor"
            className="flex items-center justify-center gap-2 w-full py-2.5 rounded-lg border border-white/[0.08] hover:bg-white/[0.04] text-sm font-medium text-zinc-300 transition-colors"
          >
            Open Mentor
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* ── Roadmap & Weekly ───────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">

        {/* Roadmap Progress */}
        <div className="lg:col-span-2 surface p-6">
          <div className="flex items-center justify-between mb-5">
            <span className="text-label">Roadmap Progress</span>
            <Link href="/roadmap" className="flex items-center gap-1 text-xs text-zinc-500 hover:text-[#fafafa] transition-colors">
              View all <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-semibold text-[#fafafa]">{completed} / {total} modules complete</span>
            <span className="text-sm text-zinc-500">{Math.round((completed / total) * 100)}%</span>
          </div>
          <div className="progress-bar mb-6">
            <div className="progress-bar-fill" style={{ width: `${total ? Math.round((completed / total) * 100) : 0}%` }} />
          </div>

          <RoadmapPreview roadmap={roadmap} />

          <div className="mt-5 pt-5 border-t border-white/[0.06] grid grid-cols-3 gap-4">
            {[
              { label: 'Completed', value: completed, color: 'text-emerald-400' },
              { label: 'In Progress', value: inProgress, color: 'text-blue-400' },
              { label: 'Remaining', value: total - completed - inProgress, color: 'text-zinc-500' },
            ].map(s => (
              <div key={s.label} className="text-center">
                <div className={`text-lg font-bold ${s.color}`}>{s.value}</div>
                <div className="text-xs text-zinc-600">{s.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Weekly Study */}
        <div className="surface p-5">
          <div className="flex items-center justify-between mb-5">
            <span className="text-label">This Week</span>
            <span className="text-xs text-zinc-500">Goal: {weeklyGoal}h</span>
          </div>
          <div className="flex items-end justify-between gap-1 h-24">
            {(weeklyProgress || []).map((d: any) => (
              <WeeklyBar key={d.day} {...d} />
            ))}
          </div>
          <div className="mt-4 pt-4 border-t border-white/[0.06] flex items-center justify-between">
            <div>
              <div className="text-lg font-bold text-[#fafafa]">{weeklyHoursStudied}h</div>
              <div className="text-xs text-zinc-500">studied this week</div>
            </div>
            <div className="text-right">
              <div className="text-sm font-semibold text-amber-400">{weeklyPct}%</div>
              <div className="text-xs text-zinc-500">of weekly goal</div>
            </div>
          </div>
        </div>
      </div>

      {/* ── Achievements ───────────────────────────────────────────────────── */}
      <div className="surface p-6">
        <div className="flex items-center justify-between mb-5">
          <span className="text-label">Recent Achievements</span>
          <Link href="/profile" className="flex items-center gap-1 text-xs text-zinc-500 hover:text-[#fafafa] transition-colors">
            View all <ArrowRight className="w-3 h-3" />
          </Link>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {profile.achievements?.map((a: any) => (
            <div key={a.id} className="flex items-center gap-3 p-3 rounded-lg bg-white/[0.03] border border-white/[0.06] hover:border-white/[0.10] transition-colors">
              <span className="text-xl">{a.icon}</span>
              <div className="min-w-0">
                <div className="text-xs font-semibold text-[#fafafa] truncate">{a.title}</div>
                <div className="text-[10px] text-zinc-600 truncate">{a.description}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Quick Actions ──────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Continue Learning', href: '/roadmap', icon: Map, desc: 'Pick up where you left off' },
          { label: 'Open Mentor', href: '/mentor', icon: Bot, desc: 'Ask your AI mentor anything' },
          { label: 'View Roadmap', href: '/roadmap', icon: Target, desc: `${total - completed} modules ahead` },
          { label: 'Your Profile', href: '/profile', icon: Trophy, desc: `${profile.readiness}% career ready` },
        ].map(action => {
          const Icon = action.icon;
          return (
            <Link
              key={action.label}
              href={action.href}
              className="group surface p-4 hover:border-white/[0.12] hover:bg-white/[0.03] transition-all duration-150"
            >
              <Icon className="w-5 h-5 text-zinc-500 group-hover:text-blue-400 transition-colors mb-3" />
              <div className="text-sm font-medium text-[#fafafa]">{action.label}</div>
              <div className="text-xs text-zinc-500 mt-0.5">{action.desc}</div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
