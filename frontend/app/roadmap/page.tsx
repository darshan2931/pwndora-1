'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Button from '@/components/ui/Button';
import { Card, CardHeader } from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Skeleton from '@/components/ui/Skeleton';
import { AssessmentData, RoadmapStep, ProjectRecommendation } from '@/types';
import { getAssessment, getSkillResources } from '@/services/api';

interface ResourceLink {
  name: string;
  url: string;
  type: string;
}

const TYPE_ICONS: Record<string, string> = {
  course: 'M12 6.042a8.967 8.967 0 00-3.597.093A7.025 7.025 0 005.05 8.04a6.966 6.966 0 00-1.68 4.62c0 3.867 3.133 7 7 7s7-3.133 7-7a6.966 6.966 0 00-1.68-4.62 7.025 7.025 0 00-3.402-.894A8.967 8.967 0 0012 6.042z',
  book: 'M12 6.042a8.967 8.967 0 00-3.597.093A7.025 7.025 0 005.05 8.04a6.966 6.966 0 00-1.68 4.62c0 3.867 3.133 7 7 7s7-3.133 7-7a6.966 6.966 0 00-1.68-4.62 7.025 7.025 0 00-3.402-.894A8.967 8.967 0 0012 6.042z',
  'hands-on': 'M15.042 21.672L13.684 16.6m0 0l-2.51 2.225.569-9.47 5.227 7.917-3.286-.672zM12 2.25V4.5m5.834.166l-1.591 1.591M20.25 10.5H18M7.757 14.743l-1.59 1.59M6 10.5H3.75m4.007-4.243l-1.59-1.59',
  tool: 'M11.42 15.17l-5.1-5.1m0 0L11.42 4.97m-5.1 5.1H3.75m7.67-7.67l5.1 5.1m0 0l-5.1 5.1m5.1-5.1H20.25',
  docs: 'M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z',
  article: 'M12 7.5h1.5m-1.5 3h1.5m-7.5 3h7.5m-7.5 3h7.5m3-9h3.375c.621 0 1.125.504 1.125 1.125V18a2.25 2.25 0 01-2.25 2.25M16.5 7.5V18a2.25 2.25 0 002.25 2.25M16.5 7.5V4.875c0-.621-.504-1.125-1.125-1.125H4.125C3.504 3.75 3 4.254 3 4.875V18a2.25 2.25 0 002.25 2.25h13.5',
  search: 'M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z',
};

function ResourceIcon({ type }: { type: string }) {
  const path = TYPE_ICONS[type] || TYPE_ICONS['course'];
  return (
    <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d={path} />
    </svg>
  );
}

function ResourceLinks({ resources, loading }: { resources: ResourceLink[]; loading: boolean }) {
  if (loading) {
    return (
      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400 mb-3">
          <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Loading free resources...
        </div>
        <div className="space-y-2">
          {[1, 2, 3].map(i => (
            <Skeleton key={i} className="h-10 w-full" />
          ))}
        </div>
      </div>
    );
  }

  if (resources.length === 0) return null;

  return (
    <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
      <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
        </svg>
        Free Learning Resources
      </h4>
      <div className="space-y-2">
        {resources.map((r) => (
          <a
            key={r.url}
            href={r.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-3 p-2.5 rounded-lg bg-gray-50 dark:bg-gray-800/80 border border-gray-200 dark:border-gray-700 hover:border-primary/40 dark:hover:border-primary/40 hover:bg-primary/5 dark:hover:bg-primary/5 transition-all group"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-center w-8 h-8 rounded-md bg-primary/10 dark:bg-primary/20 text-primary flex-shrink-0">
              <ResourceIcon type={r.type} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 dark:text-gray-100 group-hover:text-primary truncate">
                {r.name}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{r.type}</p>
            </div>
            <svg className="w-4 h-4 text-gray-400 dark:text-gray-500 group-hover:text-primary flex-shrink-0 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
            </svg>
          </a>
        ))}
      </div>
    </div>
  );
}

export default function RoadmapPage() {
  const router = useRouter();
  const [data, setData] = useState<AssessmentData | null>(null);
  const [loading, setLoading] = useState(true);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());
  const [expandedStep, setExpandedStep] = useState<number | null>(null);
  const [expandedProject, setExpandedProject] = useState<number | null>(null);
  const [resources, setResources] = useState<Record<number | string, ResourceLink[]>>({});
  const [loadingResources, setLoadingResources] = useState<Record<number | string, boolean>>({});

  useEffect(() => {
    const assessmentId = sessionStorage.getItem('assessment_id');
    const stored = sessionStorage.getItem('assessment');

    if (stored) {
      try { setData(JSON.parse(stored)); } catch { /* ignore */ }
    }

    if (assessmentId) {
      getAssessment(assessmentId)
        .then(res => {
          if (res.success && res.data) {
            setData(prev => ({
              ...(prev || {}),
              career_goal: res.data.career_goal as string,
              career_readiness: res.data.career_readiness as number,
              matched_skills: res.data.matched_skills as string[],
              missing_skills: res.data.missing_skills as string[],
              estimated_weeks: res.data.estimated_weeks as number,
              study_hours: res.data.study_hours as number,
              roadmap: res.data.roadmap as AssessmentData['roadmap'],
            } as AssessmentData));
          }
        })
        .catch(() => {});
    }

    const saved = sessionStorage.getItem('completedSteps');
    if (saved) {
      try { setCompletedSteps(new Set(JSON.parse(saved))); } catch { /* ignore */ }
    }
    setLoading(false);
  }, []);

  const fetchResources = useCallback(async (stepNum: number, skillName: string) => {
    if (resources[stepNum]) return;
    setLoadingResources(prev => ({ ...prev, [stepNum]: true }));
    try {
      const res = await getSkillResources(skillName);
      setResources(prev => ({ ...prev, [stepNum]: res.data || [] }));
    } catch {
      setResources(prev => ({ ...prev, [stepNum]: [] }));
    } finally {
      setLoadingResources(prev => ({ ...prev, [stepNum]: false }));
    }
  }, [resources]);

  const fetchProjectResources = useCallback(async (projectIdx: number, skills: string[]) => {
    const key = `project-${projectIdx}`;
    if (resources[key]) return;
    setLoadingResources(prev => ({ ...prev, [key]: true }));
    try {
      const allResources: ResourceLink[] = [];
      for (const skill of skills.slice(0, 3)) {
        const res = await getSkillResources(skill);
        if (res.data) allResources.push(...res.data);
      }
      const seen = new Set<string>();
      const unique = allResources.filter(r => {
        if (seen.has(r.url)) return false;
        seen.add(r.url);
        return true;
      });
      setResources(prev => ({ ...prev, [key]: unique }));
    } catch {
      setResources(prev => ({ ...prev, [key]: [] }));
    } finally {
      setLoadingResources(prev => ({ ...prev, [key]: false }));
    }
  }, [resources]);

  const toggleStep = (step: number) => {
    setCompletedSteps(prev => {
      const next = new Set(prev);
      if (next.has(step)) next.delete(step);
      else next.add(step);
      sessionStorage.setItem('completedSteps', JSON.stringify([...next]));
      return next;
    });
  };

  const handleCardClick = (stepNum: number, skillName: string) => {
    if (expandedStep === stepNum) {
      setExpandedStep(null);
    } else {
      setExpandedStep(stepNum);
      fetchResources(stepNum, skillName);
    }
  };

  if (loading) {
    return (
      <div className="page-container fade-in">
        <Skeleton className="h-8 w-64 mb-6" />
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 space-y-3">
              <div className="flex gap-4">
                <Skeleton variant="circular" width="40px" height="40px" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-5 w-1/3" />
                  <Skeleton className="h-4 w-2/3" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="page-container text-center py-20 fade-in">
        <div className="w-20 h-20 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg className="w-10 h-10 text-gray-400 dark:text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c-.317.159-.69.159-1.006 0l4.994 2.497c.317.158.69.158 1.006 0z" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold mb-3 dark:text-gray-100">No Roadmap Available</h1>
        <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
          Complete an assessment to generate your personalized learning roadmap.
        </p>
        <Button onClick={() => router.push('/upload')}>Start Assessment</Button>
      </div>
    );
  }

  const roadmap = data.roadmap || [];
  const projects = data.recommended_projects || [];
  const totalSteps = roadmap.length;
  const doneSteps = [...completedSteps].filter(s => s <= totalSteps).length;
  const progressPercent = totalSteps > 0 ? Math.round((doneSteps / totalSteps) * 100) : 0;

  return (
    <div className="page-container fade-in">
      <div className="mb-8">
        <h1 className="page-title">Learning Roadmap</h1>
        <p className="page-subtitle">
          Your personalized path to becoming a <strong>{data.career_goal}</strong>
        </p>
      </div>

      <Card className="mb-8">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-gray-900 dark:text-gray-100">Overall Progress</h3>
          <span className="text-sm font-medium text-primary">{doneSteps}/{totalSteps} steps · {progressPercent}%</span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
          <div
            className="bg-primary h-3 rounded-full transition-all duration-500"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
        {data.estimated_weeks && data.estimated_weeks > 0 && (
          <p className="mt-3 text-sm text-gray-500 dark:text-gray-400">
            Estimated completion: <strong>{data.estimated_weeks} weeks</strong> at your current pace
          </p>
        )}
      </Card>

      <div className="relative">
        <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700" aria-hidden="true" />

        <div className="space-y-4">
          {roadmap.map((step: RoadmapStep, i: number) => {
            const stepNum = step.step || i + 1;
            const isCompleted = completedSteps.has(stepNum);
            const isExpanded = expandedStep === stepNum;

            return (
              <div key={i} className="relative flex gap-4 slide-up" style={{ animationDelay: `${i * 50}ms` }}>
                <button
                  onClick={() => toggleStep(stepNum)}
                  className={`
                    relative z-10 flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm
                    transition-all duration-200 border-2
                    ${isCompleted
                      ? 'bg-accent text-white border-accent'
                      : 'bg-white dark:bg-gray-800 text-primary border-primary hover:bg-primary hover:text-white'}
                  `}
                  aria-label={isCompleted ? `Mark step ${stepNum} as incomplete` : `Mark step ${stepNum} as complete`}
                  aria-pressed={isCompleted}
                >
                  {isCompleted ? (
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                  ) : stepNum}
                </button>

                <div
                  className={`flex-1 cursor-pointer transition-all duration-200`}
                  onClick={() => handleCardClick(stepNum, step.skill)}
                >
                  <Card
                    hover
                    className={`transition-all duration-200 ${isCompleted ? 'opacity-60' : ''} ${isExpanded ? 'ring-2 ring-primary/30 dark:ring-primary/40' : ''}`}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className={`font-semibold text-lg ${isCompleted ? 'line-through text-gray-500 dark:text-gray-400' : 'text-gray-900 dark:text-gray-100'}`}>
                            {step.skill}
                          </h3>
                          {isCompleted && <Badge variant="success" size="sm">Done</Badge>}
                          <svg
                            className={`w-4 h-4 text-gray-400 dark:text-gray-500 transition-transform duration-200 flex-shrink-0 ml-auto ${isExpanded ? 'rotate-180' : ''}`}
                            fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                          </svg>
                        </div>
                        {step.category && (
                          <Badge variant="info" size="sm" className="mb-2">{step.category}</Badge>
                        )}
                        <div className="flex flex-wrap items-center gap-3 text-sm text-gray-500 dark:text-gray-400 mt-1">
                          <span className="flex items-center gap-1">
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            {step.estimated_hours}h estimated
                          </span>
                          {step.prerequisites && step.prerequisites.length > 0 && (
                            <span className="flex items-center gap-1">
                              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244" />
                              </svg>
                              Requires: {step.prerequisites.join(', ')}
                            </span>
                          )}
                        </div>

                        <ResourceLinks
                          resources={resources[stepNum] || []}
                          loading={loadingResources[stepNum] || false}
                        />
                      </div>
                    </div>
                  </Card>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {projects.length > 0 && (
        <div className="mt-12">
          <h2 className="text-2xl font-bold mb-6 dark:text-gray-100">Recommended Projects</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects.map((p: ProjectRecommendation, i: number) => {
              const isExpanded = expandedProject === i;
              const projectKey = `project-${i}`;
              return (
                <div key={i} className="slide-up" style={{ animationDelay: `${i * 60}ms` } as React.CSSProperties}>
                  <Card
                    hover
                    className={`cursor-pointer transition-all duration-200 ${isExpanded ? 'ring-2 ring-primary/30 dark:ring-primary/40' : ''}`}
                    onClick={() => {
                      if (expandedProject === i) {
                        setExpandedProject(null);
                      } else {
                        setExpandedProject(i);
                        fetchProjectResources(i, p.skills || []);
                      }
                    }}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-semibold text-gray-900 dark:text-gray-100">{p.title}</h4>
                      <div className="flex items-center gap-2">
                        <Badge
                          variant={p.difficulty === 'easy' || p.difficulty === 'beginner' ? 'success' : p.difficulty === 'medium' || p.difficulty === 'intermediate' ? 'warning' : 'danger'}
                          size="sm"
                        >
                          {p.difficulty}
                        </Badge>
                        <svg
                          className={`w-4 h-4 text-gray-400 dark:text-gray-500 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}
                          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                        </svg>
                      </div>
                    </div>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                      {p.estimated_hours}h estimated
                      {p.reason && <span className="ml-2">· {p.reason}</span>}
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {p.skills?.map(s => (
                        <Badge key={s} variant="info" size="sm">{s}</Badge>
                      ))}
                    </div>

                    <ResourceLinks
                      resources={resources[projectKey] || []}
                      loading={loadingResources[projectKey] || false}
                    />
                  </Card>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <div className="mt-8 flex flex-col sm:flex-row gap-3">
        <Button onClick={() => router.push('/dashboard')} variant="outline">
          Back to Dashboard
        </Button>
        <Button onClick={() => router.push('/mentor')}>
          Ask AI Mentor About Steps
        </Button>
      </div>
    </div>
  );
}
