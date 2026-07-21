'use client';

import { useState, useEffect } from 'react';
import {
  Target, ChevronDown, ChevronUp, Loader2, CheckCircle2,
  AlertTriangle, Info, ArrowRight, BarChart3, Clock
} from 'lucide-react';
import type { RoleListItem, RoleGapAnalysisData, SkillGap, NextSkillRecommendation } from '@/types';
import { api } from '@/services/api';

const GAP_STATUS_CONFIG: Record<string, { color: string; bg: string; label: string }> = {
  covered: { color: 'text-emerald-400', bg: 'bg-emerald-500/15', label: 'Covered' },
  minimal: { color: 'text-blue-400', bg: 'bg-blue-500/15', label: 'Almost' },
  partial: { color: 'text-yellow-400', bg: 'bg-yellow-500/15', label: 'Partial' },
  critical: { color: 'text-orange-400', bg: 'bg-orange-500/15', label: 'Critical' },
  missing: { color: 'text-red-400', bg: 'bg-red-500/15', label: 'Missing' },
};

const PRIORITY_CONFIG: Record<string, { color: string; bg: string }> = {
  highest: { color: 'text-red-400', bg: 'bg-red-500/15' },
  high: { color: 'text-orange-400', bg: 'bg-orange-500/15' },
  medium: { color: 'text-yellow-400', bg: 'bg-yellow-500/15' },
  low: { color: 'text-zinc-400', bg: 'bg-zinc-500/15' },
};

const READINESS_COLORS: Record<string, { color: string; bar: string }> = {
  excellent: { color: 'text-emerald-400', bar: 'bg-emerald-500' },
  good: { color: 'text-blue-400', bar: 'bg-blue-500' },
  developing: { color: 'text-yellow-400', bar: 'bg-yellow-500' },
  beginning: { color: 'text-orange-400', bar: 'bg-orange-500' },
  not_started: { color: 'text-zinc-400', bar: 'bg-zinc-500' },
};

function RoleCard({ role, selected, onSelect }: { role: RoleListItem; selected: boolean; onSelect: () => void }) {
  return (
    <button
      onClick={onSelect}
      className={`w-full text-left p-4 rounded-lg border transition-all ${
        selected
          ? 'bg-blue-500/10 border-blue-500/30 ring-1 ring-blue-500/20'
          : 'bg-white/[0.03] border-white/[0.06] hover:bg-white/[0.05] hover:border-white/[0.10]'
      }`}
    >
      <div className="flex items-center gap-3">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
          selected ? 'bg-blue-500/20' : 'bg-white/[0.06]'
        }`}>
          <Target className={`w-4 h-4 ${selected ? 'text-blue-400' : 'text-zinc-500'}`} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-semibold text-[#fafafa] truncate">{role.role_name}</div>
          <div className="text-[10px] text-zinc-500 mt-0.5 line-clamp-1">{role.description}</div>
        </div>
        <div className="text-right flex-shrink-0">
          <div className="text-xs text-zinc-400">{role.required_skills_count} skills</div>
          {role.estimated_duration && (
            <div className="text-[10px] text-zinc-600 flex items-center gap-1 justify-end mt-0.5">
              <Clock className="w-2.5 h-2.5" />
              {role.estimated_duration}
            </div>
          )}
        </div>
      </div>
    </button>
  );
}

function SkillGapRow({ gap }: { gap: SkillGap }) {
  const statusConf = GAP_STATUS_CONFIG[gap.gap_status] || GAP_STATUS_CONFIG.missing;
  const pct = Math.round(gap.confidence * 100);
  const minPct = Math.round(gap.minimum_confidence * 100);

  return (
    <div className="p-3 rounded-lg bg-white/[0.03] border border-white/[0.06]">
      <div className="flex items-center gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-[#fafafa] truncate">{gap.skill_name}</span>
            <span className={`text-[10px] px-1.5 py-0.5 rounded ${statusConf.bg} ${statusConf.color}`}>
              {statusConf.label}
            </span>
            {gap.is_required && (
              <span className="text-[10px] text-zinc-600">Required</span>
            )}
          </div>
          <div className="text-[10px] text-zinc-600 mt-0.5">{gap.category}</div>
        </div>
        <div className="w-36 flex-shrink-0">
          <div className="flex items-center gap-1.5 mb-1">
            <div className="flex-1 h-1.5 rounded-full bg-white/[0.06] overflow-hidden relative">
              <div
                className="absolute h-full rounded-full bg-white/20"
                style={{ width: `${minPct}%` }}
              />
              <div
                className={`h-full rounded-full ${statusConf.color.replace('text-', 'bg-')}`}
                style={{ width: `${pct}%` }}
              />
            </div>
            <span className="text-[10px] text-zinc-500 min-w-[60px] text-right">
              {pct}% / {minPct}%
            </span>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <span className={`text-[10px] px-1.5 py-0.5 rounded ${
            PRIORITY_CONFIG[gap.priority_level]?.bg || 'bg-zinc-500/15'
          } ${PRIORITY_CONFIG[gap.priority_level]?.color || 'text-zinc-400'}`}>
            {gap.priority_level}
          </span>
        </div>
      </div>
      {gap.blocked_by && gap.blocked_by.length > 0 && (
        <div className="mt-2 text-[10px] text-orange-400/80">
          Blocked by: {gap.blocked_by.join(', ')}
        </div>
      )}
    </div>
  );
}

function NextSkillCard({ skill }: { skill: NextSkillRecommendation }) {
  return (
    <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
      <div className="flex items-center gap-2 mb-2">
        <ArrowRight className="w-4 h-4 text-blue-400" />
        <span className="text-sm font-semibold text-blue-400">Recommended Next Skill</span>
      </div>
      <div className="text-lg font-bold text-[#fafafa]">{skill.skill_name}</div>
      <div className="text-xs text-zinc-400 mt-1">{skill.category}</div>
      <div className="flex items-center gap-4 mt-3">
        <div>
          <div className="text-[10px] text-zinc-500 uppercase">Current</div>
          <div className="text-sm font-medium text-[#fafafa]">{Math.round(skill.confidence * 100)}%</div>
        </div>
        <ArrowRight className="w-3 h-3 text-zinc-600" />
        <div>
          <div className="text-[10px] text-zinc-500 uppercase">Gap Size</div>
          <div className="text-sm font-medium text-yellow-400">{Math.round(skill.gap_size * 100)}%</div>
        </div>
        {skill.estimated_hours && (
          <div>
            <div className="text-[10px] text-zinc-500 uppercase">Est. Hours</div>
            <div className="text-sm font-medium text-[#fafafa]">{skill.estimated_hours}h</div>
          </div>
        )}
        <div>
          <div className="text-[10px] text-zinc-500 uppercase">Prerequisites</div>
          <div className={`text-sm font-medium ${skill.prerequisites_met ? 'text-emerald-400' : 'text-orange-400'}`}>
            {skill.prerequisites_met ? 'Met' : 'Not met'}
          </div>
        </div>
      </div>
      {skill.recommendation_reason && (
        <div className="mt-3 text-xs text-zinc-400 leading-relaxed">{skill.recommendation_reason}</div>
      )}
    </div>
  );
}

export function TargetRoleSection() {
  const [roles, setRoles] = useState<RoleListItem[]>([]);
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<RoleGapAnalysisData | null>(null);
  const [loading, setLoading] = useState(false);
  const [rolesLoading, setRolesLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAllGaps, setShowAllGaps] = useState(false);

  useEffect(() => {
    loadRoles();
    loadExistingAnalysis();
  }, []);

  const loadRoles = async () => {
    try {
      const res = await api.getCareerRoles();
      if (res.success && res.data?.roles) {
        setRoles(res.data.roles);
      }
    } catch (e) {
      console.error('Failed to load roles:', e);
    } finally {
      setRolesLoading(false);
    }
  };

  const loadExistingAnalysis = async () => {
    try {
      const res = await api.getGapAnalysis();
      if (res.success && res.data) {
        setAnalysis(res.data);
        setSelectedRole(res.data.role_id);
      }
    } catch (e) {
      console.error('Failed to load analysis:', e);
    }
  };

  const handleSelectAndAnalyze = async (roleId: string) => {
    setSelectedRole(roleId);
    setLoading(true);
    setError(null);

    try {
      await api.selectTargetRole(roleId);
      const res = await api.runGapAnalysis(roleId);
      if (res.success && res.data) {
        setAnalysis(res.data);
      } else {
        setError(res.message || 'Analysis failed');
      }
    } catch (e: any) {
      setError(e.message || 'Failed to run analysis');
    } finally {
      setLoading(false);
    }
  };

  const readConf = READINESS_COLORS[analysis?.readiness_level || 'not_started'] || READINESS_COLORS.not_started;
  const readinessPct = analysis ? Math.round(analysis.readiness_score * 100) : 0;

  return (
    <div className="space-y-4">
      <div className="surface p-5">
        <div className="flex items-center gap-2 mb-4">
          <Target className="w-4 h-4 text-blue-400" />
          <h3 className="text-section-title">Target Role Intelligence</h3>
          {analysis && (
            <span className="ml-auto badge-blue">
              {analysis.role_name}
            </span>
          )}
        </div>

        {rolesLoading ? (
          <div className="flex items-center gap-2 py-4">
            <Loader2 className="w-4 h-4 text-zinc-400 animate-spin" />
            <span className="text-sm text-zinc-400">Loading roles...</span>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="text-xs text-zinc-500 mb-2">Select your target career role:</div>
            {roles.map(role => (
              <RoleCard
                key={role.role_id}
                role={role}
                selected={selectedRole === role.role_id}
                onSelect={() => handleSelectAndAnalyze(role.role_id)}
              />
            ))}
          </div>
        )}
      </div>

      {loading && (
        <div className="surface p-5">
          <div className="flex items-center gap-2">
            <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
            <span className="text-sm text-zinc-400">Analyzing skill gaps for your target role...</span>
          </div>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
          <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0" />
          <span className="text-sm text-red-400">{error}</span>
        </div>
      )}

      {analysis && !loading && (
        <>
          <div className="surface p-5">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="w-4 h-4 text-emerald-400" />
              <h3 className="text-section-title">Readiness Assessment</h3>
            </div>

            <div className="flex items-center gap-6 mb-4">
              <div className="text-center">
                <div className={`text-3xl font-bold ${readConf.color}`}>{readinessPct}%</div>
                <div className="text-[10px] text-zinc-500 uppercase tracking-wider mt-1">Readiness</div>
              </div>
              <div className="flex-1">
                <div className="h-3 rounded-full bg-white/[0.06] overflow-hidden">
                  <div
                    className={`h-full rounded-full ${readConf.bar} transition-all duration-700`}
                    style={{ width: `${readinessPct}%` }}
                  />
                </div>
                <div className="flex justify-between mt-1">
                  <span className="text-[10px] text-zinc-600">0%</span>
                  <span className={`text-[10px] ${readConf.color}`}>{analysis.readiness_level}</span>
                  <span className="text-[10px] text-zinc-600">100%</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-center">
                <div className="text-lg font-bold text-emerald-400">{analysis.covered_count}</div>
                <div className="text-[10px] text-zinc-500 uppercase">Covered</div>
              </div>
              <div className="p-2.5 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-center">
                <div className="text-lg font-bold text-yellow-400">{analysis.partial_count}</div>
                <div className="text-[10px] text-zinc-500 uppercase">Partial</div>
              </div>
              <div className="p-2.5 rounded-lg bg-red-500/10 border border-red-500/20 text-center">
                <div className="text-lg font-bold text-red-400">{analysis.missing_count}</div>
                <div className="text-[10px] text-zinc-500 uppercase">Missing</div>
              </div>
            </div>

            {analysis.ai_explanation && (
              <div className="mt-4 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
                <div className="flex items-center gap-2 mb-1">
                  <Info className="w-3.5 h-3.5 text-blue-400" />
                  <span className="text-xs font-medium text-blue-400">AI Analysis</span>
                </div>
                <div className="text-xs text-zinc-400 leading-relaxed">{analysis.ai_explanation}</div>
              </div>
            )}
          </div>

          {analysis.recommended_next_skill && (
            <NextSkillCard skill={analysis.recommended_next_skill} />
          )}

          <div className="surface p-5">
            <div className="flex items-center gap-2 mb-4">
              <AlertTriangle className="w-4 h-4 text-orange-400" />
              <h3 className="text-section-title">Skill Gaps by Priority</h3>
              <span className="ml-auto text-xs text-zinc-500">
                {analysis.skill_gaps.length} skills analyzed
              </span>
            </div>

            <div className="space-y-2">
              {(showAllGaps ? analysis.skill_gaps : analysis.skill_gaps.slice(0, 10)).map(gap => (
                <SkillGapRow key={gap.skill_id} gap={gap} />
              ))}
            </div>

            {analysis.skill_gaps.length > 10 && (
              <button
                onClick={() => setShowAllGaps(!showAllGaps)}
                className="mt-3 flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 transition-colors"
              >
                {showAllGaps ? (
                  <>
                    <ChevronUp className="w-3 h-3" />
                    Show less
                  </>
                ) : (
                  <>
                    <ChevronDown className="w-3 h-3" />
                    Show all {analysis.skill_gaps.length} skills
                  </>
                )}
              </button>
            )}
          </div>

          {analysis.learning_path && analysis.learning_path.length > 0 && (
            <div className="surface p-5">
              <div className="flex items-center gap-2 mb-4">
                <Clock className="w-4 h-4 text-purple-400" />
                <h3 className="text-section-title">Recommended Learning Path</h3>
              </div>
              <div className="space-y-1.5">
                {analysis.learning_path.slice(0, 8).map((step: any, i: number) => (
                  <div key={i} className="flex items-center gap-3 py-1.5">
                    <div className="w-5 h-5 rounded-full bg-white/[0.06] flex items-center justify-center text-[10px] text-zinc-500 flex-shrink-0">
                      {step.order || i + 1}
                    </div>
                    <div className="flex-1 min-w-0">
                      <span className="text-sm text-[#fafafa]">{step.skill_name || step.skill_id}</span>
                      <span className="text-[10px] text-zinc-600 ml-2">{step.category}</span>
                    </div>
                    {step.estimated_hours > 0 && (
                      <span className="text-[10px] text-zinc-500">{step.estimated_hours}h</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      <div className="flex items-start gap-2 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
        <Info className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
        <div className="text-xs text-blue-400/80 leading-relaxed">
          Gap analysis compares your skill evidence confidence against role requirements.
          Priority scores factor in gap size, skill importance, prerequisite impact, and cross-role relevance.
        </div>
      </div>
    </div>
  );
}
