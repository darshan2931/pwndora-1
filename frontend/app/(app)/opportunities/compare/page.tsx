'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import {
  ArrowLeft, Briefcase, CheckCircle2, XCircle, AlertTriangle, BarChart3, Loader2
} from 'lucide-react';
import { api } from '@/services/api';
import type { OpportunityComparison, MissingSkill, MatchStrength } from '@/types';

export default function ComparePage() {
  const searchParams = useSearchParams();
  const idsParam = searchParams.get('ids') || '';

  const [comparisons, setComparisons] = useState<OpportunityComparison[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  useEffect(() => {
    if (idsParam) {
      const ids = idsParam.split(',').filter(Boolean);
      setSelectedIds(ids);
      loadComparisons(ids);
    }
  }, [idsParam]);

  const loadComparisons = async (ids: string[]) => {
    if (ids.length === 0) return;
    setLoading(true);
    try {
      const data = await api.compareOpportunities(ids);
      setComparisons(data.comparisons || []);
    } catch (err) {
      console.error('Failed to load comparisons:', err);
    } finally {
      setLoading(false);
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

  const getScoreBar = (score: number) => {
    const color = score >= 80 ? '#10b981' : score >= 60 ? '#3b82f6' : score >= 40 ? '#f59e0b' : '#6b7280';
    return (
      <div className="w-full h-2 bg-white/[0.06] rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-500" style={{ width: `${score}%`, backgroundColor: color }} />
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <Link href="/opportunities" className="flex items-center gap-2 text-sm text-zinc-500 hover:text-zinc-300 transition-colors mb-6">
        <ArrowLeft className="w-4 h-4" />
        Back to Opportunities
      </Link>

      <h1 className="text-2xl font-bold text-[#fafafa] flex items-center gap-3 mb-2">
        <BarChart3 className="w-6 h-6 text-blue-400" />
        Compare Opportunities
      </h1>
      <p className="text-sm text-zinc-500 mb-8">Side-by-side comparison of matched opportunities</p>

      {loading ? (
        <div className="flex items-center justify-center min-h-[40vh]">
          <div className="text-center">
            <Loader2 className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-3" />
            <p className="text-sm text-zinc-500">Loading comparison...</p>
          </div>
        </div>
      ) : comparisons.length === 0 ? (
        <div className="text-center py-16">
          <BarChart3 className="w-12 h-12 text-zinc-700 mx-auto mb-3" />
          <p className="text-sm text-zinc-500 mb-4">No opportunities to compare</p>
          <Link href="/opportunities" className="text-sm text-blue-400 hover:text-blue-300">
            Browse opportunities and calculate matches first
          </Link>
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr>
                  <th className="text-left p-3 text-xs text-zinc-500 uppercase tracking-wider w-48">Metric</th>
                  {comparisons.map((c) => (
                    <th key={c.opportunity.id} className="text-left p-3 min-w-[200px]">
                      <Link href={`/opportunities/${c.opportunity.id}`} className="block hover:bg-white/[0.02] rounded-lg p-2 -m-2 transition-colors">
                        <div className="flex items-center gap-2 mb-1">
                          <Briefcase className="w-4 h-4 text-blue-400 flex-shrink-0" />
                          <span className="text-sm font-medium text-[#fafafa]">{c.opportunity.title}</span>
                        </div>
                        <p className="text-[10px] text-zinc-500">{c.opportunity.experience_level}</p>
                      </Link>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                <tr className="border-t border-white/[0.06]">
                  <td className="p-3 text-xs text-zinc-400">Overall Score</td>
                  {comparisons.map((c) => (
                    <td key={c.opportunity.id} className="p-3">
                      {c.match ? (
                        <div>
                          <span className="text-lg font-bold text-[#fafafa]">{c.match.overall_score}%</span>
                          <div className="mt-1">{getScoreBar(c.match.overall_score)}</div>
                        </div>
                      ) : (
                        <span className="text-xs text-zinc-600">Not calculated</span>
                      )}
                    </td>
                  ))}
                </tr>
                <tr className="border-t border-white/[0.06]">
                  <td className="p-3 text-xs text-zinc-400">Category</td>
                  {comparisons.map((c) => (
                    <td key={c.opportunity.id} className="p-3">
                      {c.match ? (
                        <span className={`text-[10px] px-2 py-0.5 rounded-full border ${getCategoryColor(c.match.category)}`}>
                          {c.match.category.replace('_', ' ')}
                        </span>
                      ) : (
                        <span className="text-xs text-zinc-600">-</span>
                      )}
                    </td>
                  ))}
                </tr>
                <tr className="border-t border-white/[0.06]">
                  <td className="p-3 text-xs text-zinc-400">Skill Coverage</td>
                  {comparisons.map((c) => (
                    <td key={c.opportunity.id} className="p-3">
                      {c.match?.breakdown ? (
                        <div>
                          <span className="text-sm font-medium text-[#fafafa]">{c.match.breakdown.required_skill_coverage}%</span>
                          <div className="mt-1">{getScoreBar(c.match.breakdown.required_skill_coverage)}</div>
                        </div>
                      ) : (
                        <span className="text-xs text-zinc-600">-</span>
                      )}
                    </td>
                  ))}
                </tr>
                <tr className="border-t border-white/[0.06]">
                  <td className="p-3 text-xs text-zinc-400">Evidence Strength</td>
                  {comparisons.map((c) => (
                    <td key={c.opportunity.id} className="p-3">
                      {c.match?.breakdown ? (
                        <div>
                          <span className="text-sm font-medium text-[#fafafa]">{c.match.breakdown.evidence_strength}%</span>
                          <div className="mt-1">{getScoreBar(c.match.breakdown.evidence_strength)}</div>
                        </div>
                      ) : (
                        <span className="text-xs text-zinc-600">-</span>
                      )}
                    </td>
                  ))}
                </tr>
                <tr className="border-t border-white/[0.06]">
                  <td className="p-3 text-xs text-zinc-400">Certification Match</td>
                  {comparisons.map((c) => (
                    <td key={c.opportunity.id} className="p-3">
                      {c.match?.breakdown ? (
                        <div>
                          <span className="text-sm font-medium text-[#fafafa]">{c.match.breakdown.certification_alignment}%</span>
                          <div className="mt-1">{getScoreBar(c.match.breakdown.certification_alignment)}</div>
                        </div>
                      ) : (
                        <span className="text-xs text-zinc-600">-</span>
                      )}
                    </td>
                  ))}
                </tr>
                <tr className="border-t border-white/[0.06]">
                  <td className="p-3 text-xs text-zinc-400">Missing Skills</td>
                  {comparisons.map((c) => (
                    <td key={c.opportunity.id} className="p-3">
                      {c.match?.missing_skills ? (
                        <div className="flex flex-wrap gap-1">
                          {c.match.missing_skills.slice(0, 3).map((s: MissingSkill, i: number) => (
                            <span key={i} className="text-[10px] px-1.5 py-0.5 bg-amber-500/10 border border-amber-500/20 rounded text-amber-400">
                              {s.skill}
                            </span>
                          ))}
                          {c.match.missing_skills.length > 3 && (
                            <span className="text-[10px] text-zinc-500">+{c.match.missing_skills.length - 3}</span>
                          )}
                        </div>
                      ) : (
                        <span className="text-xs text-zinc-600">-</span>
                      )}
                    </td>
                  ))}
                </tr>
                <tr className="border-t border-white/[0.06]">
                  <td className="p-3 text-xs text-zinc-400">Strengths</td>
                  {comparisons.map((c) => (
                    <td key={c.opportunity.id} className="p-3">
                      {c.match?.strengths ? (
                        <div className="flex flex-wrap gap-1">
                          {c.match.strengths.slice(0, 3).map((s: MatchStrength, i: number) => (
                            <span key={i} className="text-[10px] px-1.5 py-0.5 bg-emerald-500/10 border border-emerald-500/20 rounded text-emerald-400">
                              {s.skill}
                            </span>
                          ))}
                          {c.match.strengths.length > 3 && (
                            <span className="text-[10px] text-zinc-500">+{c.match.strengths.length - 3}</span>
                          )}
                        </div>
                      ) : (
                        <span className="text-xs text-zinc-600">-</span>
                      )}
                    </td>
                  ))}
                </tr>
                <tr className="border-t border-white/[0.06]">
                  <td className="p-3 text-xs text-zinc-400">Total Requirements</td>
                  {comparisons.map((c) => (
                    <td key={c.opportunity.id} className="p-3">
                      <span className="text-sm text-[#fafafa]">{c.required_count} required / {c.requirements_count} total</span>
                    </td>
                  ))}
                </tr>
                <tr className="border-t border-white/[0.06]">
                  <td className="p-3"></td>
                  {comparisons.map((c) => (
                    <td key={c.opportunity.id} className="p-3">
                      <Link
                        href={`/opportunities/${c.opportunity.id}`}
                        className="text-xs text-blue-400 hover:text-blue-300"
                      >
                        View Details
                      </Link>
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
