'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Briefcase, MapPin, Building2, ChevronRight, Target, TrendingUp, Search } from 'lucide-react';
import { api } from '@/services/api';
import type { CareerOpportunity, SavedOpportunityMatch } from '@/types';

export default function OpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<CareerOpportunity[]>([]);
  const [matches, setMatches] = useState<SavedOpportunityMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [calculating, setCalculating] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'all' | 'matched'>('all');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [oppData, matchData] = await Promise.all([
        api.getOpportunities(),
        api.getUserMatches().catch(() => ({ matches: [] })),
      ]);
      setOpportunities(oppData.opportunities || []);
      setMatches(matchData.matches || []);
    } catch (err) {
      console.error('Failed to load opportunities:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateAllMatches = async () => {
    setCalculating(true);
    try {
      await api.getRecommendedOpportunities();
      const matchData = await api.getUserMatches();
      setMatches(matchData.matches || []);
      setActiveTab('matched');
    } catch (err) {
      console.error('Failed to calculate matches:', err);
    } finally {
      setCalculating(false);
    }
  };

  const getMatchForOpp = (oppId: string) => {
    return matches.find(m => m.opportunity_id === oppId);
  };

  const filteredOpps = opportunities.filter(opp =>
    opp.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (opp.organization || '').toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'highly_eligible': return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
      case 'strong_contender': return 'text-blue-400 bg-blue-500/10 border-blue-500/20';
      case 'developing_candidate': return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
      default: return 'text-zinc-400 bg-zinc-500/10 border-zinc-500/20';
    }
  };

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'highly_eligible': return 'Highly Eligible';
      case 'strong_contender': return 'Strong Contender';
      case 'developing_candidate': return 'Developing';
      default: return 'Early Gap';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-sm text-zinc-500">Loading opportunities...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-[#fafafa] flex items-center gap-3">
            <Briefcase className="w-6 h-6 text-blue-400" />
            Career Opportunities
          </h1>
          <p className="text-sm text-zinc-500 mt-1">
            Match your skills against curated cybersecurity roles
          </p>
        </div>
        <button
          onClick={calculateAllMatches}
          disabled={calculating}
          className="px-4 py-2 bg-blue-500 hover:bg-blue-600 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors flex items-center gap-2"
        >
          {calculating ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Calculating...
            </>
          ) : (
            <>
              <Target className="w-4 h-4" />
              Calculate All Matches
            </>
          )}
        </button>
      </div>

      <div className="flex items-center gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search opportunities..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-white/[0.04] border border-white/[0.08] rounded-lg text-sm text-[#fafafa] placeholder:text-zinc-600 focus:outline-none focus:border-blue-500/50"
          />
        </div>
        <div className="flex bg-white/[0.04] border border-white/[0.08] rounded-lg p-0.5">
          <button
            onClick={() => setActiveTab('all')}
            className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
              activeTab === 'all' ? 'bg-white/[0.08] text-[#fafafa]' : 'text-zinc-500 hover:text-zinc-400'
            }`}
          >
            All ({filteredOpps.length})
          </button>
          <button
            onClick={() => setActiveTab('matched')}
            className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
              activeTab === 'matched' ? 'bg-white/[0.08] text-[#fafafa]' : 'text-zinc-500 hover:text-zinc-400'
            }`}
          >
            Matched ({matches.length})
          </button>
        </div>
      </div>

      {activeTab === 'matched' && matches.length > 0 && (
        <div className="mb-6">
          <h2 className="text-sm font-medium text-zinc-400 mb-3 flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            Top Matches
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {matches.slice(0, 4).map((match) => (
              <Link
                key={match.opportunity_id}
                href={`/opportunities/${match.opportunity_id}`}
                className="p-4 bg-white/[0.03] border border-white/[0.06] rounded-xl hover:bg-white/[0.05] transition-all group"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="min-w-0 flex-1">
                    <h3 className="text-sm font-medium text-[#fafafa] truncate group-hover:text-blue-400 transition-colors">
                      {match.opportunity_title}
                    </h3>
                    <p className="text-xs text-zinc-500">{match.organization}</p>
                  </div>
                  <div className="flex items-center gap-2 ml-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full border ${getCategoryColor(match.category)}`}>
                      {getCategoryLabel(match.category)}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-4 mt-3">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-[10px] text-zinc-600">Match Score</span>
                      <span className="text-xs font-bold text-[#fafafa]">{match.overall_score}%</span>
                    </div>
                    <div className="w-full h-1.5 bg-white/[0.06] rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{
                          width: `${match.overall_score}%`,
                          backgroundColor: match.overall_score >= 80 ? '#10b981' :
                            match.overall_score >= 60 ? '#3b82f6' :
                            match.overall_score >= 40 ? '#f59e0b' : '#6b7280'
                        }}
                      />
                    </div>
                  </div>
                </div>
                {match.recommendation && (
                  <p className="text-[11px] text-zinc-500 mt-2 line-clamp-2">{match.recommendation}</p>
                )}
              </Link>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-2">
        {(activeTab === 'matched' ? filteredOpps.filter(o => getMatchForOpp(o.id)) : filteredOpps).map((opp) => {
          const match = getMatchForOpp(opp.id);
          return (
            <Link
              key={opp.id}
              href={`/opportunities/${opp.id}`}
              className="block p-4 bg-white/[0.03] border border-white/[0.06] rounded-xl hover:bg-white/[0.05] transition-all group"
            >
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center flex-shrink-0">
                  <Briefcase className="w-5 h-5 text-blue-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-medium text-[#fafafa] group-hover:text-blue-400 transition-colors">
                      {opp.title}
                    </h3>
                    {match && (
                      <span className={`text-[10px] px-1.5 py-0.5 rounded-full border ${getCategoryColor(match.category)}`}>
                        {match.overall_score}%
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-3 mt-1 text-xs text-zinc-500">
                    {opp.organization && (
                      <span className="flex items-center gap-1">
                        <Building2 className="w-3 h-3" />
                        {opp.organization}
                      </span>
                    )}
                    {opp.location && (
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {opp.location}
                      </span>
                    )}
                    {opp.experience_level && (
                      <span className="px-1.5 py-0.5 bg-white/[0.04] rounded text-[10px] text-zinc-500">
                        {opp.experience_level}
                      </span>
                    )}
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-zinc-600 group-hover:text-zinc-400 transition-colors" />
              </div>
            </Link>
          );
        })}
      </div>

      {filteredOpps.length === 0 && (
        <div className="text-center py-12">
          <Briefcase className="w-12 h-12 text-zinc-700 mx-auto mb-3" />
          <p className="text-sm text-zinc-500">No opportunities found</p>
        </div>
      )}
    </div>
  );
}
