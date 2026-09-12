'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Award, Clock, DollarSign, Calendar, RefreshCw, ExternalLink,
  CheckCircle2, Circle, TrendingUp, Sparkles, Loader2
} from 'lucide-react';
import { api } from '@/services/api';
import { useDashboardData } from '@/components/providers/DashboardDataProvider';

const DIFFICULTY_BADGE: Record<string, string> = {
  beginner: 'badge-green',
  intermediate: 'badge-yellow',
  advanced: 'badge-red',
};

function SummaryCard({ icon: Icon, label, value, sub, accent }: { icon: any; label: string; value: string; sub?: string; accent: string }) {
  return (
    <div className="surface border border-white/[0.06] p-4 rounded-xl">
      <div className="flex items-center gap-2">
        <Icon className={`w-3.5 h-3.5 ${accent}`} />
        <span className="text-[11px] uppercase tracking-wider text-zinc-500">{label}</span>
      </div>
      <p className="text-xl font-bold text-[#fafafa] mt-2">{value}</p>
      {sub && <p className="text-xs text-zinc-500 mt-0.5">{sub}</p>}
    </div>
  );
}

export default function CertificationsPage() {
  const router = useRouter();
  const { data, loading: profileLoading } = useDashboardData();
  const profile = data?.profile || {};

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [weeklyHours, setWeeklyHours] = useState<number>(10);
  const [plan, setPlan] = useState<any>(null);
  const [input, setInput] = useState('');

  const loadPlan = async (hours: number) => {
    setLoading(true);
    setError('');
    try {
      const res = await api.planCertifications(hours);
      if (res?.success) {
        setPlan(res.data);
      } else {
        setError(res?.error?.message || 'Failed to load certification plan');
      }
    } catch (e: any) {
      setError(e?.message || 'Failed to load certification plan');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const weekly = Number(profile.weeklyStudyHours) || 10;
    setWeeklyHours(weekly);
    setInput(String(weekly));
    if (!profileLoading) {
      loadPlan(weekly);
    }
  }, [profileLoading, data?.profile?.weeklyStudyHours]);

  const applyWeekly = () => {
    const h = Number(input);
    if (!isNaN(h) && h > 0 && h <= 80) {
      setWeeklyHours(h);
      loadPlan(h);
    }
  };

  if (profileLoading || loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
      </div>
    );
  }

  if (!plan) {
    return (
      <div className="p-6 max-w-6xl mx-auto">
        <div className="surface border border-white/[0.06] p-8 rounded-xl text-center">
          <Award className="w-10 h-10 text-yellow-500 mx-auto mb-3" />
          <h1 className="text-lg font-semibold text-[#fafafa] mb-2">Certification Planner</h1>
          <p className="text-sm text-zinc-500 mb-4">
            {error || 'Complete onboarding to get a personalized certification plan.'}
          </p>
          <button onClick={() => router.push('/onboarding')} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium transition-colors">
            Go to Onboarding
          </button>
        </div>
      </div>
    );
  }

  const summary = plan.summary || {};

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-[#fafafa] flex items-center gap-2.5">
          <Award className="w-6 h-6 text-yellow-500" />
          Certification Planner
        </h1>
        <p className="text-sm text-zinc-500 mt-1">
          Personalized cert timeline & cost estimate for <span className="text-blue-400 font-medium">{plan.career}</span>
        </p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <SummaryCard icon={Award} label="Certifications" value={String(summary.total_certifications || 0)} sub="Planned sequence" accent="text-yellow-500" />
        <SummaryCard icon={Calendar} label="Timeline" value={`${summary.total_weeks || 0} wks`} sub={`≈ ${summary.total_months || 0} months`} accent="text-blue-400" />
        <SummaryCard icon={DollarSign} label="Total Cost" value={`$${Math.round(summary.total_cost || 0).toLocaleString()}`} sub="Exam + training + renewal" accent="text-emerald-400" />
        <SummaryCard icon={Clock} label="Study Pace" value={`${summary.weekly_study_hours || 0} h/wk`} sub="Your weekly commitment" accent="text-violet-400" />
      </div>

      {/* Weekly hours control */}
      <div className="surface border border-white/[0.06] p-4 rounded-xl flex flex-wrap items-center gap-3">
        <Clock className="w-4 h-4 text-blue-400" />
        <span className="text-sm text-zinc-400">Study hours per week:</span>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && applyWeekly()}
          type="number"
          min={1}
          max={80}
          className="bg-white/[0.04] border border-white/[0.08] rounded-lg px-3 py-1.5 text-sm text-[#fafafa] w-20 focus:outline-none focus:border-blue-500/50"
        />
        <button onClick={applyWeekly} className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-white/[0.06] hover:bg-white/[0.10] text-zinc-300 text-sm font-medium border border-white/[0.08] transition-colors">
          <RefreshCw className="w-3.5 h-3.5" /> Recalculate
        </button>
      </div>

      {/* Detailed timeline */}
      <div className="space-y-2">
        <p className="text-label">Recommended Sequence</p>
        {(plan.certifications || []).map((cert: any) => (
          <div key={cert.name} className="surface border border-white/[0.06] rounded-xl overflow-hidden">
            <div className="p-4 flex items-center gap-4">
              <div className={`w-9 h-9 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${cert.recommended ? 'border-blue-500/40 bg-blue-500/10' : 'border-white/[0.08] bg-[#09090b]'}`}>
                {cert.recommended
                  ? <Sparkles className="w-4 h-4 text-blue-500" />
                  : <CheckCircle2 className="w-4 h-4 text-zinc-600" />}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-semibold text-[#fafafa]">{cert.name}</span>
                  <span className={DIFFICULTY_BADGE[cert.difficulty] || 'badge-gray'}>
                    {cert.difficulty}
                  </span>
                  {cert.recommended && <span className="badge-blue">Core</span>}
                </div>
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1.5 text-xs text-zinc-500">
                  <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{cert.weeks} weeks ({cert.study_hours}h)</span>
                  <span className="flex items-center gap-1"><Calendar className="w-3 h-3" />Weeks {cert.start_week}–{cert.end_week}</span>
                  <span className="flex items-center gap-1"><DollarSign className="w-3 h-3" />${Math.round(cert.cost.total).toLocaleString()}</span>
                  {!!cert.validity_years && <span className="text-zinc-600">{cert.validity_years}yr validity</span>}
                </div>
                {(cert.prerequisites || []).length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {(cert.prerequisites).map((p: string) => (
                      <span key={p} className="badge-gray">Prereq: {p}</span>
                    ))}
                  </div>
                )}
              </div>
              {cert.url && cert.url !== '#' && (
                <a
                  href={cert.url}
                  target="_blank"
                  rel="noreferrer"
                  className="p-2 rounded-lg bg-white/[0.03] hover:bg-white/[0.08] border border-white/[0.06] transition-colors"
                  onClick={e => e.stopPropagation()}
                >
                  <ExternalLink className="w-4 h-4 text-zinc-400" />
                </a>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Cost breakdown */}
      <div className="surface border border-white/[0.06] p-5 rounded-xl">
        <p className="text-sm font-semibold text-[#fafafa] mb-4 flex items-center gap-2">
          <DollarSign className="w-4 h-4 text-emerald-400" /> Cost Breakdown
        </p>
        <div className="space-y-2.5">
          {(plan.certifications || []).map((cert: any) => (
            <div key={cert.name} className="flex items-center gap-3 text-sm">
              <span className="flex-1 text-zinc-400 truncate">{cert.name}</span>
              <span className="text-zinc-600 w-24 text-right">${Math.round(cert.cost.exam_cost || 0).toLocaleString()} exam</span>
              <span className="text-zinc-600 w-24 text-right">${Math.round(cert.cost.training_cost || 0).toLocaleString()} training</span>
              <span className="text-emerald-400 w-24 text-right font-medium">${Math.round(cert.cost.total || 0).toLocaleString()}</span>
            </div>
          ))}
          <div className="border-t border-white/[0.06] pt-2.5 flex items-center gap-3 text-sm font-semibold">
            <span className="flex-1 text-[#fafafa]">Estimated Total</span>
            <span className="w-24 text-right text-zinc-500"></span>
            <span className="w-24 text-right text-zinc-500"></span>
            <span className="text-emerald-400 w-24 text-right">${Math.round(summary.total_cost || 0).toLocaleString()}</span>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 text-xs text-zinc-500">
        <span className="flex items-center gap-1.5"><Sparkles className="w-3.5 h-3.5 text-blue-500" /> Direct recommendation</span>
        <span className="flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-zinc-600" /> Prerequisite-first order</span>
      </div>
    </div>
  );
}