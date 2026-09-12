'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { CalendarCheck, Target, TrendingUp, FolderGit2, ArrowRight, Plus } from 'lucide-react';
import { api } from '@/services/api';

const DAYS_ABBR = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

function Bar({ day, hours, goal, isToday }: { day: string; hours: number; goal: number; isToday: boolean }) {
  const pct = goal > 0 ? Math.min((hours / goal) * 100, 100) : 0;
  return (
    <div className="flex flex-col items-center gap-1.5">
      <div className="relative h-20 w-7 bg-white/[0.04] rounded-sm overflow-hidden">
        <div
          className={`absolute bottom-0 left-0 right-0 rounded-sm transition-all duration-500 ${isToday ? 'bg-blue-500' : hours > 0 ? 'bg-emerald-500/70' : ''}`}
          style={{ height: `${pct}%` }}
        />
      </div>
      <span className={`text-[10px] ${isToday ? 'text-[#fafafa] font-medium' : 'text-zinc-600'}`}>{day}</span>
      <span className="text-[10px] text-zinc-600">{hours}h</span>
    </div>
  );
}

function Stat({ icon: Icon, label, value, sub, color = 'blue' }: {
  icon: React.ComponentType<{ className?: string }>;
  label: string; value: string | number; sub?: string;
  color?: 'blue' | 'emerald' | 'amber';
}) {
  const colors = {
    blue: 'text-blue-400 bg-blue-500/10',
    emerald: 'text-emerald-400 bg-emerald-500/10',
    amber: 'text-amber-400 bg-amber-500/10',
  };
  return (
    <div className="surface p-5">
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center mb-3 ${colors[color]}`}>
        <Icon className="w-4 h-4" />
      </div>
      <div className="text-2xl font-bold text-[#fafafa] tracking-tight">{value}</div>
      <div className="text-xs text-zinc-500 mt-0.5">{label}</div>
      {sub && <div className="text-xs text-zinc-600 mt-1">{sub}</div>}
    </div>
  );
}

export default function ProgressPage() {
  const [weekly, setWeekly] = useState<any>(null);
  const [portfolio, setPortfolio] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [hoursInput, setHoursInput] = useState('');
  const [goalInput, setGoalInput] = useState('');
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState('');

  const load = async () => {
    try {
      const [w, p] = await Promise.all([api.getWeeklyProgress(), api.getPortfolio()]);
      setWeekly(w?.data || null);
      setPortfolio(p?.data?.projects || []);
    } catch (e) {
      console.error('Failed to load progress data', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleLogHours = async () => {
    const h = parseInt(hoursInput, 10);
    if (!h || h < 1) { setFeedback('Enter hours (1-80)'); return; }
    setSaving(true);
    setFeedback('');
    try {
      await api.logStudyHours(h);
      setHoursInput('');
      setFeedback('Logged!');
      await load();
    } catch (e: any) {
      setFeedback(e?.message || 'Failed to log hours');
    } finally {
      setSaving(false);
    }
  };

  const handleSetGoal = async () => {
    const g = parseInt(goalInput, 10);
    if (!g || g < 1 || g > 80) { setFeedback('Enter goal (1-80h)'); return; }
    setSaving(true);
    try {
      await api.setWeeklyGoal(g);
      setGoalInput('');
      setFeedback('Goal updated!');
      await load();
    } catch (e: any) {
      setFeedback(e?.message || 'Failed to set goal');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="p-8 text-white animate-pulse">Loading progress...</div>;

  const today = new Date().getDay();
  const todayAbbr = DAYS_ABBR[today];
  const totalHours = weekly?.total_hours || 0;
  const goalHours = weekly?.goal_hours || 10;
  const pct = weekly?.progress_pct ?? (goalHours ? Math.round((totalHours / goalHours) * 100) : 0);
  const met = weekly?.goal_met || false;

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-[#fafafa] tracking-tight">Progress Tracking</h1>
        <p className="text-sm text-zinc-500 mt-1">Log your study time, hit weekly goals, and grow your portfolio.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Stat icon={TrendingUp} label="Hours this week" value={`${totalHours}h`} sub={`Goal: ${goalHours}h`} color="blue" />
        <Stat icon={Target} label="Goal completion" value={`${pct}%`} sub={met ? 'Goal met. Nice!' : `${Math.max(0, goalHours - totalHours)}h to go`} color="amber" />
        <Stat icon={CalendarCheck} label="Active days" value={`${(weekly?.days || []).filter((d: any) => d.hours > 0).length}/7`} sub="days with logged study" color="emerald" />
        <Stat icon={FolderGit2} label="Portfolio projects" value={portfolio.length} sub="from your roadmap" />
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Weekly chart + logging */}
        <div className="surface p-5">
          <div className="flex items-center justify-between mb-5">
            <span className="text-label">This Week</span>
            <span className="text-xs text-zinc-500">{weekly?.week_start} → {weekly?.week_end}</span>
          </div>

          <div className="flex items-end justify-between gap-2 h-28">
            {(weekly?.days || []).map((d: any) => (
              <Bar key={d.day} {...d} goal={goalHours / 7} isToday={d.day === todayAbbr} />
            ))}
          </div>

          <div className="mt-5 pt-4 border-t border-white/[0.06] space-y-2">
            {feedback && <div className="text-xs text-emerald-400">{feedback}</div>}
            <div className="flex gap-2">
              <input
                type="number" min={1} max={80} value={hoursInput}
                onChange={(e) => setHoursInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleLogHours()}
                placeholder="Log today's study hours"
                className="flex-1 min-w-0 px-3 py-2 rounded-lg bg-white/[0.05] border border-white/[0.08] text-sm text-[#fafafa] placeholder:text-zinc-600 focus:outline-none focus:border-blue-500/50"
              />
              <button
                onClick={handleLogHours} disabled={saving}
                className="flex items-center gap-1 px-3 py-2 rounded-lg bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-xs font-semibold text-white transition-colors"
              >
                <Plus className="w-3.5 h-3.5" /> Log
              </button>
            </div>
            <div className="flex gap-2">
              <input
                type="number" min={1} max={80} value={goalInput}
                onChange={(e) => setGoalInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSetGoal()}
                placeholder="Set weekly goal (h)"
                className="flex-1 min-w-0 px-3 py-2 rounded-lg bg-white/[0.05] border border-white/[0.08] text-sm text-[#fafafa] placeholder:text-zinc-600 focus:outline-none focus:border-blue-500/50"
              />
              <button
                onClick={handleSetGoal} disabled={saving}
                className="flex items-center gap-1 px-3 py-2 rounded-lg bg-white/[0.06] hover:bg-white/[0.10] disabled:opacity-50 text-xs font-semibold text-zinc-300 transition-colors"
              >
                <Target className="w-3.5 h-3.5" /> Set
              </button>
            </div>
          </div>
        </div>

        {/* Portfolio */}
        <div className="surface p-5">
          <div className="flex items-center justify-between mb-5">
            <span className="text-label">Portfolio Projects</span>
            <Link href="/roadmap" className="flex items-center gap-1 text-xs text-zinc-500 hover:text-[#fafafa] transition-colors">
              Open roadmap <ArrowRight className="w-3 h-3" />
            </Link>
          </div>

          {portfolio.length === 0 ? (
            <div className="text-sm text-zinc-600 py-10 text-center">
              No projects yet. Projects from your learning roadmap will appear here.
            </div>
          ) : (
            <div className="space-y-3 max-h-[360px] overflow-y-auto pr-1">
              {portfolio.map((p: any) => (
                <div key={p.id} className="p-4 rounded-lg bg-white/[0.03] border border-white/[0.06]">
                  <div className="flex items-center justify-between gap-2">
                    <div className="text-sm font-semibold text-[#fafafa] truncate">{p.title}</div>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full shrink-0 ${
                      p.status === 'completed' ? 'bg-emerald-500/15 text-emerald-400' :
                      p.status === 'in-progress' ? 'bg-blue-500/15 text-blue-400' : 'bg-zinc-500/15 text-zinc-400'
                    }`}>
                      {p.status}
                    </span>
                  </div>
                  {p.description && <p className="text-xs text-zinc-500 mt-1 line-clamp-2">{p.description}</p>}
                  <div className="flex flex-wrap gap-1 mt-2">
                    {(p.skills || []).slice(0, 4).map((s: string) => (
                      <span key={s} className="text-[10px] px-2 py-0.5 rounded-full bg-white/[0.05] text-zinc-400">{s}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}