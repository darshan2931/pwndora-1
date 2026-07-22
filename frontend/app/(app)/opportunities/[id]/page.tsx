'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import {
  Briefcase, MapPin, Building2, ArrowLeft, Target, CheckCircle2,
  AlertTriangle, TrendingUp, Loader2, Sparkles
} from 'lucide-react';
import { api } from '@/services/api';

export default function OpportunityDetailPage() {
  const params = useParams();
  const router = useRouter();
  const opportunityId = params.id as string;

  const [opportunity, setOpportunity] = useState<any>(null);
  const [requirements, setRequirements] = useState<any[]>([]);
  const [match, setMatch] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);
  const [explaining, setExplaining] = useState(false);
  const [explanation, setExplanation] = useState<string | null>(null);

  useEffect(() => {
    loadOpportunity();
  }, [opportunityId]);

  const loadOpportunity = async () => {
    try {
      const data = await api.getOpportunity(opportunityId);
      setOpportunity(data.opportunity);
      setRequirements(data.requirements || []);
    } catch (err) {
      console.error('Failed to load opportunity:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateMatch = async () => {
    setCalculating(true);
    try {
      const data = await api.matchOpportunity(opportunityId);
      setMatch(data.match);
    } catch (err) {
      console.error('Failed to calculate match:', err);
    } finally {
      setCalculating(false);
    }
  };

  const getExplanation = async () => {
    setExplaining(true);
    try {
      const data = await api.explainOpportunity(opportunityId);
      setExplanation(data.explanation);
    } catch (err) {
      console.error('Failed to get explanation:', err);
    } finally {
      setExplaining(false);
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'highly_eligible': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      case 'strong_contender': return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
      case 'developing_candidate': return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
      default: return 'text-zinc-400 bg-zinc-500/10 border-zinc-500/20';
    }
  };

  const getImportanceColor = (importance: string) => {
    switch (importance) {
      case 'critical': return 'text-red-400 bg-red-500/10 border-red-500/20';
      case 'high': return 'text-orange-400 bg-orange-500/10 border-orange-500/20';
      case 'important': return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
      case 'medium': return 'text-zinc-400 bg-zinc-500/10 border-zinc-500/20';
      default: return 'text-zinc-500 bg-zinc-500/10 border-zinc-500/20';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-zinc-500">Loading opportunity...</p>
        </div>
      </div>
    );
  }

  if (!opportunity) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-8">
        <p className="text-zinc-500">Opportunity not found</p>
      </div>
    );
  }

  const requiredSkills = requirements.filter((r: any) => r.requirement_type === 'required');
  const preferredSkills = requirements.filter((r: any) => r.requirement_type === 'preferred');
  const certs = requirements.filter((r: any) => r.requirement_type === 'certification');

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      <button
        onClick={() => router.back()}
        className="flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-300 transition-colors mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Opportunities
      </button>

      <div className="flex items-start justify-between mb-8">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center flex-shrink-0">
            <Briefcase className="w-6 h-6 text-blue-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-[#fafafa]">{opportunity.title}</h1>
            <div className="flex items-center gap-3 mt-1 text-sm text-zinc-500">
              {opportunity.organization && (
                <span className="flex items-center gap-1">
                  <Building2 className="w-4 h-4" />
                  {opportunity.organization}
                </span>
              )}
              {opportunity.location && (
                <span className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  {opportunity.location}
                </span>
              )}
              {opportunity.experience_level && (
                <span className="px-2 py-0.5 bg-white/[0.04] rounded text-xs text-zinc-500">
                  {opportunity.experience_level}
                </span>
              )}
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {!match && (
            <button
              onClick={calculateMatch}
              disabled={calculating}
              className="px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
            >
              {calculating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Target className="w-4 h-4" />}
              Calculate Match
            </button>
          )}
          {match && (
            <button
              onClick={getExplanation}
              disabled={explaining}
              className="px-4 py-2 bg-violet-500 hover:bg-violet-600 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
            >
              {explaining ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              AI Explanation
            </button>
          )}
        </div>
      </div>

      {opportunity.description && (
        <div className="p-4 bg-white/[0.03] border border-white/[0.06] rounded-xl mb-6">
          <p className="text-sm text-zinc-400 leading-relaxed">{opportunity.description}</p>
        </div>
      )}

      {match && (
        <div className="p-6 bg-white/[0.03] border border-white/[0.06] rounded-xl mb-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-[#fafafa] flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-blue-400" />
              Match Analysis
            </h2>
            <div className="flex items-center gap-3">
              <span className={`text-sm px-3 py-1 rounded-full border ${getCategoryColor(match.category)}`}>
                {match.category?.replace('_', ' ')}
              </span>
              <span className="text-3xl font-bold text-[#fafafa]">{match.overall_score}%</span>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
            {match.breakdown && Object.entries(match.breakdown).map(([key, value]: [string, any]) => (
              <div key={key} className="p-3 bg-white/[0.02] rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] text-zinc-500 uppercase tracking-wider">
                    {key.replace(/_/g, ' ')}
                  </span>
                  <span className="text-sm font-bold text-[#fafafa]">{value}%</span>
                </div>
                <div className="w-full h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${value}%`,
                      backgroundColor: value >= 80 ? '#10b981' : value >= 60 ? '#3b82f6' : value >= 40 ? '#f59e0b' : '#6b7280'
                    }}
                  />
                </div>
              </div>
            ))}
          </div>

          {match.strengths && match.strengths.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-medium text-zinc-400 mb-3 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Your Strengths
              </h3>
              <div className="flex flex-wrap gap-2">
                {match.strengths.map((s: any, i: number) => (
                  <div key={i} className="px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-xs text-emerald-400">
                    {s.skill} ({s.max_confidence}%)
                  </div>
                ))}
              </div>
            </div>
          )}

          {match.missing_skills && match.missing_skills.length > 0 && (
            <div className="mb-6">
              <h3 className="text-sm font-medium text-zinc-400 mb-3 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                Skills to Develop
              </h3>
              <div className="flex flex-wrap gap-2">
                {match.missing_skills.map((s: any, i: number) => (
                  <div key={i} className="px-3 py-1.5 bg-amber-500/10 border border-amber-500/20 rounded-lg text-xs text-amber-400">
                    {s.skill} ({s.importance})
                  </div>
                ))}
              </div>
            </div>
          )}

          {match.recommendation && (
            <div className="p-3 bg-blue-500/5 border border-blue-500/10 rounded-lg">
              <p className="text-sm text-blue-400">{match.recommendation}</p>
            </div>
          )}
        </div>
      )}

      {explanation && (
        <div className="p-6 bg-violet-500/5 border border-violet-500/10 rounded-xl mb-6">
          <h2 className="text-lg font-semibold text-[#fafafa] flex items-center gap-2 mb-4">
            <Sparkles className="w-5 h-5 text-violet-400" />
            AI Explanation
          </h2>
          <div className="text-sm text-zinc-300 leading-relaxed whitespace-pre-wrap">
            {explanation}
          </div>
        </div>
      )}

      <div className="p-6 bg-white/[0.03] border border-white/[0.06] rounded-xl">
        <h2 className="text-lg font-semibold text-[#fafafa] mb-4">Requirements</h2>

        {requiredSkills.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-medium text-zinc-400 mb-3">Required Skills</h3>
            <div className="space-y-2">
              {requiredSkills.map((r: any, i: number) => (
                <div key={i} className="flex items-center justify-between p-3 bg-white/[0.02] rounded-lg">
                  <span className="text-sm text-[#fafafa]">{r.skill_name}</span>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full border ${getImportanceColor(r.importance)}`}>
                    {r.importance}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {preferredSkills.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-medium text-zinc-400 mb-3">Preferred Skills</h3>
            <div className="space-y-2">
              {preferredSkills.map((r: any, i: number) => (
                <div key={i} className="flex items-center justify-between p-3 bg-white/[0.02] rounded-lg">
                  <span className="text-sm text-[#fafafa]">{r.skill_name}</span>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full border ${getImportanceColor(r.importance)}`}>
                    {r.importance}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {certs.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-zinc-400 mb-3">Certifications</h3>
            <div className="space-y-2">
              {certs.map((r: any, i: number) => (
                <div key={i} className="flex items-center justify-between p-3 bg-white/[0.02] rounded-lg">
                  <span className="text-sm text-[#fafafa]">{r.skill_name}</span>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full border ${getImportanceColor(r.importance)}`}>
                    {r.importance}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
