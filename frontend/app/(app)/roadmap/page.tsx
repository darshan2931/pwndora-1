'use client';

import { useEffect, useState } from 'react';
import {
  CheckCircle2, Circle, Lock, PlayCircle, ExternalLink,
  ChevronDown, ChevronRight, Clock, Zap, BookOpen
} from 'lucide-react';
import { api } from '@/services/api';
import type { RoadmapNode } from '@/types';

const STATUS_CONFIG = {
  completed: { label: 'Completed', dot: 'bg-emerald-500', icon: CheckCircle2, iconCls: 'text-emerald-500', border: 'border-emerald-500/30' },
  'in-progress': { label: 'In Progress', dot: 'bg-blue-500 animate-pulse', icon: PlayCircle, iconCls: 'text-blue-500', border: 'border-blue-500/40' },
  available: { label: 'Available', dot: 'bg-zinc-500', icon: Circle, iconCls: 'text-zinc-400', border: 'border-zinc-700' },
  locked: { label: 'Locked', dot: 'bg-zinc-800', icon: Lock, iconCls: 'text-zinc-700', border: 'border-zinc-800' },
};

const TYPE_BADGE: Record<string, string> = {
  skill: 'badge-blue',
  project: 'badge-violet',
  certification: 'badge-yellow',
  milestone: 'badge-green',
};

const RESOURCE_ICON: Record<string, string> = {
  video: '▶', article: '📄', lab: '⚗️', book: '📖', course: '🎓',
};

function NodeCard({ node, index, totalNodes, onToggle }: { node: RoadmapNode; index: number; totalNodes: number; onToggle: (index: number) => void }) {
  const [open, setOpen] = useState(node.status === 'in-progress');
  const cfg = STATUS_CONFIG[node.status as keyof typeof STATUS_CONFIG] || STATUS_CONFIG.available;
  const Icon = cfg.icon;
  const locked = node.status === 'locked';

  return (
    <div className={`relative ${locked ? 'opacity-50' : ''}`}>
      {/* Connector line */}
      {index < totalNodes - 1 && (
        <div className={`absolute left-[19px] top-full w-px h-4 ${node.status === 'completed' ? 'bg-emerald-500/40' : 'bg-zinc-800'}`} />
      )}

      <div
        className={`surface border ${cfg.border} transition-all duration-200 ${!locked ? 'hover:border-white/[0.12] cursor-pointer' : ''} ${node.status === 'in-progress' ? 'bg-[#111318]' : ''}`}
        onClick={() => !locked && setOpen(o => !o)}
      >
        <div className="p-4 flex items-center gap-4">
          {/* Status icon */}
          <div className={`w-9 h-9 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${cfg.border} bg-[#09090b]`}>
            <Icon className={`w-4 h-4 ${cfg.iconCls}`} />
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-sm font-semibold text-[#fafafa]">{node.title}</span>
              <span className={TYPE_BADGE[node.type] || 'badge-gray'}>{node.type}</span>
              {node.status === 'in-progress' && <span className="badge-blue">Current</span>}
            </div>
            <div className="flex items-center gap-3 mt-1">
              <span className="text-xs text-zinc-500 flex items-center gap-1">
                <Clock className="w-3 h-3" />{node.estimatedHours || 1}h
              </span>
              <span className="text-xs text-zinc-500 flex items-center gap-1">
                <Zap className="w-3 h-3" />{node.difficulty || 'Beginner'}
              </span>
              {node.completedAt && (
                <span className="text-xs text-emerald-500">✓ {new Date(node.completedAt).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
              )}
            </div>
          </div>

          {/* Toggle */}
          {!locked && (
            <div className="text-zinc-600">
              {open ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </div>
          )}
        </div>

        {/* Expanded */}
        {open && !locked && (
          <div className="px-4 pb-4 border-t border-white/[0.06] pt-4 space-y-4">
            <p className="text-sm text-zinc-400 leading-relaxed">{node.description}</p>

            {(node.skills || []).length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {node.skills.map(s => (
                  <span key={s} className="badge-gray">{s}</span>
                ))}
              </div>
            )}

            {(node.resources || []).length > 0 && (
              <div>
                <p className="text-xs font-medium text-zinc-500 mb-2 flex items-center gap-1.5">
                  <BookOpen className="w-3.5 h-3.5" /> Resources
                </p>
                <div className="space-y-1.5">
                  {(node.resources || []).map(r => (
                    <a
                      key={r.id} href={r.url}
                      className="flex items-center gap-3 p-2.5 rounded-lg bg-white/[0.03] hover:bg-white/[0.06] border border-white/[0.06] transition-colors group"
                      onClick={e => e.stopPropagation()}
                    >
                      <span className="text-sm">{RESOURCE_ICON[r.type]}</span>
                      <div className="flex-1 min-w-0">
                        <span className="text-xs font-medium text-zinc-300 group-hover:text-[#fafafa] transition-colors">{r.title}</span>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="text-[10px] text-zinc-600 capitalize">{r.type}</span>
                          {r.free && <span className="text-[10px] text-emerald-500">Free</span>}
                        </div>
                      </div>
                      <ExternalLink className="w-3.5 h-3.5 text-zinc-700 group-hover:text-zinc-400 transition-colors" />
                    </a>
                  ))}
                </div>
              </div>
            )}

            {node.status === 'in-progress' && (
              <button 
                onClick={() => onToggle(index)}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-500 hover:bg-blue-600 text-white text-sm font-medium transition-colors"
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                Mark Complete
              </button>
            )}
            {node.status === 'available' && (
              <button 
                onClick={() => onToggle(index)}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/[0.06] hover:bg-white/[0.10] text-zinc-300 text-sm font-medium border border-white/[0.08] transition-colors"
              >
                <PlayCircle className="w-3.5 h-3.5" />
                Start Module
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default function RoadmapPage() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const d = await api.getDashboardData();
        setData(d.data);
      } catch (e) {
        console.error(e);
      }
    }
    loadData();
  }, []);

  const handleToggle = async (index: number) => {
    if (!data || !data.roadmap) return;
    
    const assessmentId = data.profile?.id;
    if (!assessmentId) return;
    
    // Optimistic UI update
    const newRoadmap = [...data.roadmap];
    const node = newRoadmap[index];
    if (node.status === 'available') {
      node.status = 'in-progress';
    } else if (node.status === 'in-progress') {
      node.status = 'completed';
      node.completedAt = new Date().toISOString();
      // Unlock next available node if any
      if (index + 1 < newRoadmap.length && newRoadmap[index + 1].status === 'locked') {
        newRoadmap[index + 1].status = 'available';
      }
    }
    
    setData({ ...data, roadmap: newRoadmap });

    try {
      await api.toggleRoadmapStep(assessmentId, index);
    } catch (e) {
      console.error('Failed to toggle', e);
      // Revert on failure by reloading
      const d = await api.getDashboardData();
      setData(d.data);
    }
  };

  if (!data || !data.roadmap) return <div className="p-8 text-white animate-pulse">Loading roadmap...</div>;

  const roadmap = data.roadmap || [];
  const profile = data.profile || {};
  const completed = roadmap.filter((n: any) => n.status === 'completed').length;
  const inProgress = roadmap.filter((n: any) => n.status === 'in-progress').length;
  const total = roadmap.length;
  const pct = total ? Math.round((completed / total) * 100) : 0;

  return (
    <div className="max-w-3xl mx-auto animate-fade-in">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-[#fafafa] tracking-tight mb-1">Your Roadmap</h1>
        <p className="text-sm text-zinc-500">
          {profile.targetRole || 'Your'} path — {completed} of {total} modules complete
        </p>
      </div>

      {/* Progress overview */}
      <div className="surface p-5 mb-6">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-semibold text-[#fafafa]">Overall Progress</span>
          <span className="text-sm font-bold text-blue-400">{pct}%</span>
        </div>
        <div className="progress-bar mb-4">
          <div className="progress-bar-fill" style={{ width: `${pct}%` }} />
        </div>
        <div className="grid grid-cols-3 gap-4">
          {[
            { label: 'Completed', value: completed, color: 'text-emerald-400' },
            { label: 'In Progress', value: inProgress, color: 'text-blue-400' },
            { label: 'Remaining', value: total - completed - inProgress, color: 'text-zinc-400' },
          ].map(s => (
            <div key={s.label} className="text-center">
              <div className={`text-xl font-bold ${s.color}`}>{s.value}</div>
              <div className="text-xs text-zinc-600">{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Filter tabs */}
      <div className="flex items-center gap-2 mb-5">
        {['All', 'Skills', 'Projects', 'Certifications'].map(f => (
          <button key={f} className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${f === 'All' ? 'bg-white/[0.08] text-[#fafafa]' : 'text-zinc-500 hover:text-zinc-300 hover:bg-white/[0.04]'}`}>
            {f}
          </button>
        ))}
      </div>

      {/* Timeline */}
      <div className="space-y-4">
        {roadmap.map((node: any, i: number) => (
          <NodeCard key={node.id} node={node} index={i} totalNodes={roadmap.length} onToggle={handleToggle} />
        ))}
      </div>
    </div>
  );
}
