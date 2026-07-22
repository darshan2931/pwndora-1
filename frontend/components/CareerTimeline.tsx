'use client';

import { useState, useEffect } from 'react';
import {
  Clock, Loader2, RefreshCw, AlertCircle, ArrowUpRight,
  GitBranch, BookOpen, Award, FileText, Briefcase
} from 'lucide-react';
import type { CareerTimelineEntry } from '@/types';
import { api } from '@/services/api';

const EVENT_ICONS: Record<string, typeof Clock> = {
  roadmap_skill_completed: BookOpen,
  roadmap_project_completed: GitBranch,
  roadmap_certification_completed: Award,
  github_repository_linked: GitBranch,
  github_repository_analyzed: GitBranch,
  github_profile_reanalyzed: GitBranch,
  assessment_completed: FileText,
  resume_uploaded: FileText,
  certification_added: Award,
  experience_added: Briefcase,
};

const EVENT_LABELS: Record<string, string> = {
  roadmap_skill_completed: 'Skill Completed',
  roadmap_project_completed: 'Project Completed',
  roadmap_certification_completed: 'Certification Completed',
  github_repository_linked: 'Repository Linked',
  github_repository_analyzed: 'Repository Analyzed',
  github_profile_reanalyzed: 'Profile Reanalyzed',
  assessment_completed: 'Assessment Completed',
  resume_uploaded: 'Resume Uploaded',
  certification_added: 'Certification Added',
  experience_added: 'Experience Added',
};

function TimelineEntry({ entry }: { entry: CareerTimelineEntry }) {
  const Icon = EVENT_ICONS[entry.change_type] || Clock;
  const label = EVENT_LABELS[entry.change_type] || entry.change_type.replace(/_/g, ' ');

  return (
    <div className="flex gap-3 group">
      <div className="flex flex-col items-center">
        <div className="w-8 h-8 rounded-full bg-white/[0.06] border border-white/[0.08] flex items-center justify-center flex-shrink-0">
          <Icon className="w-3.5 h-3.5 text-zinc-400" />
        </div>
        <div className="w-px flex-1 bg-white/[0.06] my-1" />
      </div>

      <div className="flex-1 pb-4">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-zinc-300">{label}</span>
          {entry.confidence_delta !== 0 && (
            <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded ${
              entry.confidence_delta > 0
                ? 'bg-emerald-500/10 text-emerald-400'
                : 'bg-red-500/10 text-red-400'
            }`}>
              {entry.confidence_delta > 0 ? '+' : ''}{entry.confidence_delta}%
            </span>
          )}
        </div>

        {entry.skill_name && (
          <div className="text-[11px] text-zinc-500 mt-0.5">
            Skill: <span className="text-zinc-400">{entry.skill_name}</span>
          </div>
        )}

        {entry.explanation && (
          <div className="text-[11px] text-zinc-500 mt-1 leading-relaxed">
            {entry.explanation}
          </div>
        )}

        {entry.ai_explanation && (
          <div className="text-[11px] text-zinc-400 mt-1 leading-relaxed italic">
            {entry.ai_explanation}
          </div>
        )}

        <div className="text-[10px] text-zinc-600 mt-1.5">
          {entry.created_at ? new Date(entry.created_at).toLocaleString() : ''}
        </div>
      </div>
    </div>
  );
}

export default function CareerTimeline({ limit = 30 }: { limit?: number }) {
  const [timeline, setTimeline] = useState<CareerTimelineEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadTimeline = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getCareerTimeline(limit);
      setTimeline(res.data.timeline || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load timeline');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadTimeline(); }, [limit]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-5 h-5 text-zinc-500 animate-spin" />
        <span className="ml-2 text-sm text-zinc-500">Loading timeline...</span>
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
        <button onClick={loadTimeline} className="mt-2 text-xs text-zinc-500 hover:text-zinc-300">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-zinc-200 flex items-center gap-2">
          <Clock className="w-4 h-4 text-blue-400" />
          Progress Timeline
        </h3>
        <button onClick={loadTimeline} className="p-1.5 rounded-md hover:bg-white/[0.06] text-zinc-500 hover:text-zinc-300">
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </div>

      {timeline.length === 0 ? (
        <div className="text-center py-8">
          <Clock className="w-8 h-8 text-zinc-700 mx-auto mb-2" />
          <p className="text-sm text-zinc-500">No activity yet</p>
          <p className="text-xs text-zinc-600 mt-1">Complete roadmap items or add evidence to see your progress timeline</p>
        </div>
      ) : (
        <div className="pl-1">
          {timeline.map((entry) => (
            <TimelineEntry key={entry.id} entry={entry} />
          ))}
        </div>
      )}
    </div>
  );
}
