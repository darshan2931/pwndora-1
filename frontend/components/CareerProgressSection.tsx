'use client';

import { useState, useEffect } from 'react';
import {
  TrendingUp, BarChart3, Loader2, RefreshCw, Zap,
  CheckCircle2, Clock, AlertCircle
} from 'lucide-react';
import type { CareerProgressSummary, CareerTimelineEntry } from '@/types';
import { api } from '@/services/api';

function StatCard({ label, value, sublabel, color }: {
  label: string;
  value: string | number;
  sublabel?: string;
  color?: string;
}) {
  return (
    <div className="p-3.5 rounded-lg bg-white/[0.03] border border-white/[0.06]">
      <div className="text-[10px] uppercase tracking-wider text-zinc-500 mb-1">{label}</div>
      <div className={`text-xl font-bold ${color || 'text-zinc-100'}`}>{value}</div>
      {sublabel && <div className="text-[10px] text-zinc-600 mt-0.5">{sublabel}</div>}
    </div>
  );
}

function ConfidenceBar({ label, count, total, color }: {
  label: string;
  count: number;
  total: number;
  color: string;
}) {
  const pct = total > 0 ? Math.round((count / total) * 100) : 0;
  return (
    <div className="flex items-center gap-2">
      <span className="text-[10px] text-zinc-500 min-w-[50px]">{label}</span>
      <div className="flex-1 h-1.5 rounded-full bg-white/[0.06] overflow-hidden">
        <div className={`h-full rounded-full ${color} transition-all duration-500`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[10px] text-zinc-400 min-w-[30px] text-right">{count}</span>
    </div>
  );
}

export default function CareerProgressSection() {
  const [progress, setProgress] = useState<CareerProgressSummary | null>(null);
  const [timeline, setTimeline] = useState<CareerTimelineEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [progressRes, timelineRes] = await Promise.all([
        api.getCareerProgress(),
        api.getCareerTimeline(10),
      ]);
      setProgress(progressRes.data);
      setTimeline(timelineRes.data.timeline || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load progress');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-5 h-5 text-zinc-500 animate-spin" />
        <span className="ml-2 text-sm text-zinc-500">Loading progress...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/20">
        <div className="flex items-center gap-2 text-red-400 text-sm">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
        <button onClick={loadData} className="mt-2 text-xs text-zinc-500 hover:text-zinc-300">
          Retry
        </button>
      </div>
    );
  }

  if (!progress) return null;

  const { skills, readiness, events } = progress;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-zinc-200 flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-emerald-400" />
          Career Progress
        </h3>
        <button onClick={loadData} className="p-1.5 rounded-md hover:bg-white/[0.06] text-zinc-500 hover:text-zinc-300">
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <StatCard label="Readiness" value={`${readiness.score}%`} sublabel={readiness.level} color="text-emerald-400" />
        <StatCard label="Avg Confidence" value={`${skills.average_confidence}%`} sublabel={`${skills.total} skills`} color="text-blue-400" />
        <StatCard label="High Confidence" value={skills.high} sublabel="80%+" color="text-emerald-400" />
        <StatCard label="Events Processed" value={events.processed} sublabel={`${events.pending} pending`} color="text-zinc-300" />
      </div>

      <div className="p-3.5 rounded-lg bg-white/[0.03] border border-white/[0.06]">
        <div className="text-[10px] uppercase tracking-wider text-zinc-500 mb-3">Skill Confidence Distribution</div>
        <div className="space-y-2">
          <ConfidenceBar label="High" count={skills.high} total={skills.total} color="bg-emerald-500" />
          <ConfidenceBar label="Medium" count={skills.medium} total={skills.total} color="bg-blue-500" />
          <ConfidenceBar label="Low" count={skills.low} total={skills.total} color="bg-yellow-500" />
          <ConfidenceBar label="Minimal" count={skills.minimal} total={skills.total} color="bg-zinc-500" />
        </div>
      </div>

      {timeline.length > 0 && (
        <div className="p-3.5 rounded-lg bg-white/[0.03] border border-white/[0.06]">
          <div className="text-[10px] uppercase tracking-wider text-zinc-500 mb-3">Recent Activity</div>
          <div className="space-y-2">
            {timeline.slice(0, 5).map((entry) => (
              <div key={entry.id} className="flex items-start gap-2 py-1.5">
                <div className={`mt-0.5 w-1.5 h-1.5 rounded-full flex-shrink-0 ${
                  entry.confidence_delta > 0 ? 'bg-emerald-400' :
                  entry.confidence_delta < 0 ? 'bg-red-400' : 'bg-zinc-500'
                }`} />
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-zinc-300 truncate">
                    {entry.skill_name || entry.change_type.replace(/_/g, ' ')}
                  </div>
                  <div className="text-[10px] text-zinc-600">
                    {entry.confidence_delta !== 0 && (
                      <span className={entry.confidence_delta > 0 ? 'text-emerald-500' : 'text-red-500'}>
                        {entry.confidence_delta > 0 ? '+' : ''}{entry.confidence_delta}%
                      </span>
                    )}
                    {entry.ai_explanation && (
                      <span className="ml-2 text-zinc-500">— {entry.ai_explanation.slice(0, 60)}</span>
                    )}
                  </div>
                </div>
                <span className="text-[10px] text-zinc-600 flex-shrink-0">
                  {entry.created_at ? new Date(entry.created_at).toLocaleDateString() : ''}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {progress.roadmap_versions.length > 0 && (
        <div className="p-3.5 rounded-lg bg-white/[0.03] border border-white/[0.06]">
          <div className="text-[10px] uppercase tracking-wider text-zinc-500 mb-3">Roadmap Versions</div>
          <div className="space-y-1.5">
            {progress.roadmap_versions.map((v) => (
              <div key={v.id} className="flex items-center gap-2 text-xs">
                <span className="text-zinc-400">v{v.version_number}</span>
                <span className="text-zinc-600">—</span>
                <span className="text-zinc-500 truncate flex-1">{v.generation_reason}</span>
                <span className="text-zinc-600">{v.nodes_count} nodes</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
