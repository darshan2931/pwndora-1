'use client';

import { CheckCircle2, Clock, Trophy, BookOpen, Zap, Target, Star, Calendar, Flame } from 'lucide-react';
import { useDashboardData } from '@/components/providers/DashboardDataProvider';
import type { Skill } from '@/types';

const ICON_MAP: Record<string, any> = {
  Flame: Flame,
  Star: Star,
  Trophy: Trophy,
};

const LEVEL_CONFIG = {
  beginner: { label: 'Beginner', color: 'badge-green' },
  intermediate: { label: 'Intermediate', color: 'badge-blue' },
  advanced: { label: 'Advanced', color: 'badge-violet' },
};

const CERT_STATUS = {
  planned: { label: 'Planned', cls: 'badge-gray' },
  'in-progress': { label: 'In Progress', cls: 'badge-yellow' },
  completed: { label: 'Completed', cls: 'badge-green' },
};

function SkillPill({ skill }: { skill: Skill }) {
  const lvl = LEVEL_CONFIG[skill.level];
  return (
    <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.03] border border-white/[0.06] hover:border-white/[0.10] transition-colors">
      <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 flex-shrink-0" />
      <span className="text-xs font-medium text-[#fafafa]">{skill.name}</span>
      <span className={`ml-auto ${lvl.color}`}>{lvl.label}</span>
    </div>
  );
}

export default function ProfilePage() {
  const { data, loading } = useDashboardData();

  if (loading) return <div className="p-8 text-white animate-pulse">Loading profile...</div>;

  if (!data?.profile) return (
    <div className="p-8 text-center">
      <div className="text-red-400 mb-2">Failed to load profile</div>
    </div>
  );

  const p = data.profile;
  const completedRoadmap = (data.roadmap || []).filter((n: any) => n.status === 'completed').length;

  return (
    <div className="max-w-5xl mx-auto animate-fade-in space-y-6">
      {/* Header */}
      <div className="surface p-6">
        <div className="flex items-start gap-5">
          <div className="w-16 h-16 rounded-2xl bg-blue-500/20 border border-blue-500/30 flex items-center justify-center flex-shrink-0">
            <span className="text-xl font-black text-blue-400">{p.avatarInitials}</span>
          </div>
          <div className="flex-1 min-w-0">
            <h1 className="text-xl font-bold text-[#fafafa]">{p.name}</h1>
            <p className="text-sm text-zinc-400 mt-0.5">{p.email}</p>
            <div className="flex items-center gap-2 mt-2 flex-wrap">
              <span className="badge-blue">{p.targetRole}</span>
              <span className="badge-gray">{p.targetRoleCategory}</span>
              <span className={`${p.experience === 'Beginner' ? 'badge-green' : p.experience === 'Intermediate' ? 'badge-blue' : 'badge-violet'}`}>
                {p.experience}
              </span>
            </div>
          </div>
          <div className="text-right flex-shrink-0">
            <div className="text-3xl font-black text-[#fafafa]">{p.readiness}%</div>
            <div className="text-xs text-zinc-500">Career Ready</div>
            <div className="progress-bar w-24 mt-2 ml-auto">
              <div className="progress-bar-fill" style={{ width: `${p.readiness}%` }} />
            </div>
          </div>
        </div>
      </div>

      {/* ── Stats row ───────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: 'Study Streak', value: `${p.currentStreak}d`, icon: Zap, color: 'text-amber-400', bg: 'bg-amber-500/10' },
          { label: 'Total Hours', value: `${p.totalStudyHours}h`, icon: Clock, color: 'text-blue-400', bg: 'bg-blue-500/10' },
          { label: 'Achievements', value: p.achievements?.length || 0, icon: Trophy, color: 'text-violet-400', bg: 'bg-violet-500/10' },
          { label: 'Modules Done', value: completedRoadmap, icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
        ].map(s => {
          const Icon = s.icon;
          return (
            <div key={s.label} className="surface p-5">
              <div className={`w-8 h-8 rounded-lg ${s.bg} flex items-center justify-center mb-3`}>
                <Icon className={`w-4 h-4 ${s.color}`} />
              </div>
              <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
              <div className="text-xs text-zinc-500 mt-0.5">{s.label}</div>
            </div>
          );
        })}
      </div>

      {/* ── Skills & Missing ────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="surface p-5">
          <div className="flex items-center gap-2 mb-4">
            <Star className="w-4 h-4 text-emerald-400" />
            <h2 className="text-section-title">Known Skills</h2>
            <span className="ml-auto badge-gray">{p.knownSkills?.length || 0}</span>
          </div>
          <div className="space-y-1.5">
            {p.knownSkills?.map((s: any) => <SkillPill key={s.id} skill={s} />)}
          </div>
        </div>

        <div className="surface p-5">
          <div className="flex items-center gap-2 mb-4">
            <Target className="w-4 h-4 text-amber-400" />
            <h2 className="text-section-title">Skills to Learn</h2>
            <span className="ml-auto badge-gray">{p.missingSkills?.length || 0}</span>
          </div>
          <div className="space-y-1.5">
            {p.missingSkills?.map((s: any) => (
              <div key={s.id} className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.03] border border-white/[0.06]">
                <div className="w-1.5 h-1.5 rounded-full bg-amber-400 flex-shrink-0" />
                <span className="text-xs font-medium text-[#fafafa]">{s.name}</span>
                <span className="ml-auto badge-gray text-zinc-600">{s.category}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Projects ────────────────────────────────────────────────────── */}
      <div className="surface p-5">
        <div className="flex items-center gap-2 mb-4">
          <BookOpen className="w-4 h-4 text-blue-400" />
          <h2 className="text-section-title">Projects</h2>
          <span className="ml-auto badge-gray">{p.projects?.length || 0}</span>
        </div>
        <div className="space-y-3">
          {p.projects?.map((proj: any) => (
            <div key={proj.id} className="flex items-start gap-4 p-4 rounded-lg bg-white/[0.03] border border-white/[0.06] hover:border-white/[0.10] transition-colors">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${proj.completed ? 'bg-emerald-500/20' : 'bg-zinc-800'}`}>
                {proj.completed
                  ? <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  : <Clock className="w-4 h-4 text-zinc-500" />}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-semibold text-[#fafafa]">{proj.title}</span>
                  {proj.completed && <span className="badge-green">Completed</span>}
                </div>
                <p className="text-xs text-zinc-400 mt-1 leading-relaxed">{proj.description}</p>
                <div className="flex items-center gap-2 mt-2 flex-wrap">
                  {(proj.skills || []).map((s: string) => <span key={s} className="badge-gray">{s}</span>)}
                  <span className="text-xs text-zinc-600 ml-1">{proj.estimatedHours}h</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ── Certifications & Achievements ───────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="surface p-5">
          <div className="flex items-center gap-2 mb-4">
            <Trophy className="w-4 h-4 text-amber-400" />
            <h2 className="text-section-title">Certifications</h2>
          </div>
          <div className="space-y-3">
            {p.certifications?.map((c: any) => {
              const s = CERT_STATUS[c.status as keyof typeof CERT_STATUS] || CERT_STATUS.planned;
              return (
                <div key={c.id} className="flex items-center gap-3 p-3 rounded-lg bg-white/[0.03] border border-white/[0.06]">
                  <div className="text-lg flex-shrink-0">🏆</div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold text-[#fafafa]">{c.name}</div>
                    <div className="text-xs text-zinc-500">{c.issuer}</div>
                  </div>
                  <span className={s.cls}>{s.label}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="surface p-5">
          <div className="flex items-center gap-2 mb-4">
            <Star className="w-4 h-4 text-violet-400" />
            <h2 className="text-section-title">Achievements</h2>
          </div>
          <div className="space-y-3">
            {p.achievements?.map((a: any) => {
              const Icon = ICON_MAP[a.icon] || Trophy;
              return (
                <div key={a.id} className="flex items-center gap-3 p-3 rounded-lg bg-white/[0.03] border border-white/[0.06]">
                  <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center flex-shrink-0">
                    <Icon className="w-4 h-4 text-amber-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold text-[#fafafa]">{a.title}</div>
                    <div className="text-xs text-zinc-500">{a.description}</div>
                  </div>
                  <div className="flex items-center gap-1 text-[10px] text-zinc-600 flex-shrink-0">
                    <Calendar className="w-3 h-3" />
                    {new Date(a.unlockedAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* ── Learning Preferences ────────────────────────────────────────── */}
      <div className="surface p-5">
        <h2 className="text-section-title mb-4">Learning Preferences</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {[
            { id: 'videos', label: 'Videos', icon: '▶', active: p.learningPreferences?.includes('videos') },
            { id: 'reading', label: 'Reading', icon: '📖', active: p.learningPreferences?.includes('reading') },
            { id: 'labs', label: 'Hands-on Labs', icon: '⚗️', active: p.learningPreferences?.includes('labs') },
            { id: 'projects', label: 'Projects', icon: '🛠', active: p.learningPreferences?.includes('projects') },
          ].map(pref => (
            <div key={pref.id} className={`flex items-center gap-2.5 p-3 rounded-lg border transition-colors ${pref.active ? 'bg-blue-500/10 border-blue-500/30' : 'bg-white/[0.03] border-white/[0.06]'}`}>
              <span className="text-base">{pref.icon}</span>
              <span className={`text-xs font-medium ${pref.active ? 'text-blue-400' : 'text-zinc-500'}`}>{pref.label}</span>
              {pref.active && <CheckCircle2 className="w-3.5 h-3.5 text-blue-400 ml-auto" />}
            </div>
          ))}
        </div>
        <div className="mt-4 pt-4 border-t border-white/[0.06] flex items-center gap-4 text-sm">
          <span className="text-zinc-500">Study goal:</span>
          <span className="text-[#fafafa] font-medium">{p.weeklyStudyHours} hours / week</span>
          <span className="text-zinc-500">Level:</span>
          <span className="text-[#fafafa] font-medium">{p.experience}</span>
        </div>
      </div>
    </div>
  );
}
