'use client';

import { useState } from 'react';
import {
  Shield, ChevronDown, ChevronUp, Loader2, BarChart3,
  CheckCircle2, AlertCircle, Info, Layers
} from 'lucide-react';
import type { SkillEvidenceItem, SkillEvidenceSource } from '@/types';

const CONFIDENCE_COLORS: Record<string, { bar: string; badge: string; text: string }> = {
  high: { bar: 'bg-emerald-500', badge: 'badge-green', text: 'text-emerald-400' },
  medium: { bar: 'bg-blue-500', badge: 'badge-blue', text: 'text-blue-400' },
  low: { bar: 'bg-yellow-500', badge: 'badge-yellow', text: 'text-yellow-400' },
  minimal: { bar: 'bg-zinc-500', badge: 'badge-gray', text: 'text-zinc-400' },
};

const SOURCE_LABELS: Record<string, string> = {
  resume_claim: 'Resume Claim',
  resume_experience: 'Resume Experience',
  github_language: 'GitHub Language',
  github_topic: 'GitHub Topic',
  github_dependency: 'GitHub Dependency',
  github_readme: 'GitHub README',
  github_ai_analysis: 'GitHub AI Analysis',
  assessment_matched: 'Assessment Match',
  assessment_completed: 'Assessment Complete',
  project_completed: 'Project Complete',
  certification_earned: 'Certification Earned',
};

function ConfidenceBar({ confidence, level }: { confidence: number; level: string }) {
  const colors = CONFIDENCE_COLORS[level] || CONFIDENCE_COLORS.minimal;
  const pct = Math.round(confidence * 100);

  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 h-1.5 rounded-full bg-white/[0.06] overflow-hidden">
        <div
          className={`h-full rounded-full ${colors.bar} transition-all duration-500`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className={`text-xs font-medium ${colors.text} min-w-[36px] text-right`}>
        {pct}%
      </span>
    </div>
  );
}

function EvidenceSourceRow({ source }: { source: SkillEvidenceSource }) {
  const label = SOURCE_LABELS[source.source] || source.source;
  const effPct = Math.round(source.effective_confidence * 100);

  return (
    <div className="flex items-center gap-3 py-1.5">
      <span className="badge-gray text-[10px] min-w-[120px]">{label}</span>
      <div className="flex-1 flex items-center gap-2">
        <div className="flex-1 h-1 rounded-full bg-white/[0.04] overflow-hidden">
          <div
            className="h-full rounded-full bg-white/20"
            style={{ width: `${effPct}%` }}
          />
        </div>
        <span className="text-[10px] text-zinc-500 min-w-[32px] text-right">{effPct}%</span>
      </div>
      {source.repository && (
        <span className="text-[10px] text-zinc-600 truncate max-w-[100px]">{source.repository}</span>
      )}
    </div>
  );
}

function SkillEvidenceCard({ skill }: { skill: SkillEvidenceItem }) {
  const [expanded, setExpanded] = useState(false);
  const colors = CONFIDENCE_COLORS[skill.confidence_level] || CONFIDENCE_COLORS.minimal;

  return (
    <div className="p-3.5 rounded-lg bg-white/[0.03] border border-white/[0.06]">
      <div className="flex items-center gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-[#fafafa] truncate">{skill.skill_name}</span>
            <span className={`text-[10px] ${colors.badge}`}>{skill.confidence_level}</span>
          </div>
          <div className="text-[10px] text-zinc-600 mt-0.5">{skill.category}</div>
        </div>
        <div className="w-28">
          <ConfidenceBar confidence={skill.confidence} level={skill.confidence_level} />
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-[10px] text-zinc-500">{skill.evidence_count} sources</span>
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1 rounded hover:bg-white/[0.06] transition-colors"
          >
            {expanded ? (
              <ChevronUp className="w-3 h-3 text-zinc-500" />
            ) : (
              <ChevronDown className="w-3 h-3 text-zinc-500" />
            )}
          </button>
        </div>
      </div>

      {expanded && skill.sources && skill.sources.length > 0 && (
        <div className="mt-3 pt-3 border-t border-white/[0.04] space-y-1">
          <div className="text-[10px] text-zinc-500 uppercase tracking-wider mb-2">Evidence Breakdown</div>
          {skill.sources.map((src, i) => (
            <EvidenceSourceRow key={i} source={src} />
          ))}
        </div>
      )}
    </div>
  );
}

export function SkillEvidenceSection({
  evidenceData,
  analyzing,
  onAnalyze,
  error,
}: {
  evidenceData: { evidence: SkillEvidenceItem[]; total_skills: number; high_confidence: number; medium_confidence: number; low_confidence: number; minimal_confidence: number; average_confidence: number; analysis_status: string } | null;
  analyzing: boolean;
  onAnalyze: () => void;
  error: string | null;
}) {
  const [filter, setFilter] = useState<string>('all');

  if (!evidenceData && !analyzing) return null;

  const isCompleted = evidenceData?.analysis_status === 'completed';
  const hasEvidence = evidenceData && evidenceData.evidence && evidenceData.evidence.length > 0;

  const filteredEvidence = hasEvidence
    ? filter === 'all'
      ? evidenceData!.evidence
      : evidenceData!.evidence.filter(e => e.confidence_level === filter)
    : [];

  return (
    <div className="space-y-4">
      <div className="surface p-5">
        <div className="flex items-center gap-2 mb-4">
          <Shield className="w-4 h-4 text-emerald-400" />
          <h3 className="text-section-title">Skill Evidence Confidence</h3>
          {isCompleted && (
            <span className="ml-auto badge-green">
              {evidenceData!.total_skills} skills analyzed
            </span>
          )}
        </div>

        {!isCompleted && !analyzing && (
          <button
            onClick={onAnalyze}
            disabled={analyzing}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-500/15 text-emerald-400 hover:bg-emerald-500/25 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Layers className="w-4 h-4" />
            <span className="text-sm">Analyze Skill Evidence</span>
          </button>
        )}

        {analyzing && (
          <div className="flex items-center gap-2 px-4 py-2">
            <Loader2 className="w-4 h-4 text-emerald-400 animate-spin" />
            <span className="text-sm text-zinc-400">Aggregating evidence from all sources...</span>
          </div>
        )}

        {isCompleted && hasEvidence && (
          <>
            <div className="grid grid-cols-4 gap-3 mb-4">
              {[
                { label: 'High', count: evidenceData!.high_confidence, color: 'text-emerald-400' },
                { label: 'Medium', count: evidenceData!.medium_confidence, color: 'text-blue-400' },
                { label: 'Low', count: evidenceData!.low_confidence, color: 'text-yellow-400' },
                { label: 'Minimal', count: evidenceData!.minimal_confidence, color: 'text-zinc-400' },
              ].map(item => (
                <div key={item.label} className="p-2.5 rounded-lg bg-white/[0.03] border border-white/[0.06] text-center">
                  <div className={`text-lg font-bold ${item.color}`}>{item.count}</div>
                  <div className="text-[10px] text-zinc-500 uppercase tracking-wider">{item.label}</div>
                </div>
              ))}
            </div>

            <div className="flex items-center gap-2 mb-4">
              <span className="text-xs text-zinc-500">Average confidence:</span>
              <span className="text-xs font-medium text-[#fafafa]">{evidenceData!.average_confidence}%</span>
            </div>

            <div className="flex items-center gap-1.5 mb-4 flex-wrap">
              {['all', 'high', 'medium', 'low', 'minimal'].map(f => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-2.5 py-1 rounded-lg text-[10px] uppercase tracking-wider transition-colors ${
                    filter === f
                      ? 'bg-white/[0.10] text-[#fafafa]'
                      : 'bg-white/[0.03] text-zinc-500 hover:bg-white/[0.06]'
                  }`}
                >
                  {f === 'all' ? 'All' : f}
                </button>
              ))}
            </div>
          </>
        )}
      </div>

      {error && (
        <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
          <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
          <span className="text-sm text-red-400">{error}</span>
        </div>
      )}

      {isCompleted && hasEvidence && (
        <div className="space-y-2">
          {filteredEvidence.map(skill => (
            <SkillEvidenceCard key={skill.skill_id} skill={skill} />
          ))}
          {filteredEvidence.length === 0 && (
            <div className="text-center py-6">
              <span className="text-sm text-zinc-500">No skills in this confidence level.</span>
            </div>
          )}
        </div>
      )}

      {isCompleted && !hasEvidence && (
        <div className="text-center py-6">
          <BarChart3 className="w-8 h-8 text-zinc-700 mx-auto mb-2" />
          <div className="text-sm text-zinc-500">No skill evidence found</div>
          <div className="text-xs text-zinc-600 mt-1">Upload a resume or analyze GitHub to generate evidence</div>
        </div>
      )}

      {isCompleted && (
        <div className="flex items-start gap-2 p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
          <Info className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
          <div className="text-xs text-emerald-400/80 leading-relaxed">
            Confidence scores are computed deterministically using evidence from resume claims, GitHub observations, and assessments.
            Each source has a weight and maximum cap. Multiple sources use diminishing returns to avoid over-counting.
          </div>
        </div>
      )}
    </div>
  );
}
