'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Button from '@/components/ui/Button';
import { Card, CardHeader } from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Skeleton from '@/components/ui/Skeleton';
import { AssessmentData, RoadmapStep, ProjectRecommendation } from '@/types';

export default function RoadmapPage() {
  const router = useRouter();
  const [data, setData] = useState<AssessmentData | null>(null);
  const [loading, setLoading] = useState(true);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());

  useEffect(() => {
    const stored = sessionStorage.getItem('assessment');
    if (stored) {
      try { setData(JSON.parse(stored)); } catch { /* ignore */ }
    }
    const saved = sessionStorage.getItem('completedSteps');
    if (saved) {
      try { setCompletedSteps(new Set(JSON.parse(saved))); } catch { /* ignore */ }
    }
    setLoading(false);
  }, []);

  const toggleStep = (step: number) => {
    setCompletedSteps(prev => {
      const next = new Set(prev);
      if (next.has(step)) next.delete(step);
      else next.add(step);
      sessionStorage.setItem('completedSteps', JSON.stringify([...next]));
      return next;
    });
  };

  if (loading) {
    return (
      <div className="page-container fade-in">
        <Skeleton className="h-8 w-64 mb-6" />
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className="bg-white p-6 rounded-xl border border-gray-200 space-y-3">
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
        <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg className="w-10 h-10 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0z" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold mb-3">No Roadmap Available</h1>
        <p className="text-gray-600 mb-6 max-w-md mx-auto">
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
          <h3 className="font-semibold text-gray-900">Overall Progress</h3>
          <span className="text-sm font-medium text-primary">{doneSteps}/{totalSteps} steps · {progressPercent}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-primary h-3 rounded-full transition-all duration-500"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
        {data.estimated_weeks && data.estimated_weeks > 0 && (
          <p className="mt-3 text-sm text-gray-500">
            Estimated completion: <strong>{data.estimated_weeks} weeks</strong> at your current pace
          </p>
        )}
      </Card>

      <div className="relative">
        <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-gray-200" aria-hidden="true" />

        <div className="space-y-4">
          {roadmap.map((step: RoadmapStep, i: number) => {
            const stepNum = step.step || i + 1;
            const isCompleted = completedSteps.has(stepNum);

            return (
              <div key={i} className="relative flex gap-4 slide-up" style={{ animationDelay: `${i * 50}ms` }}>
                <button
                  onClick={() => toggleStep(stepNum)}
                  className={`
                    relative z-10 flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm
                    transition-all duration-200 border-2
                    ${isCompleted
                      ? 'bg-accent text-white border-accent'
                      : 'bg-white text-primary border-primary hover:bg-primary hover:text-white'
                    }
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

                <Card
                  hover
                  className={`flex-1 transition-all duration-200 ${isCompleted ? 'opacity-60' : ''}`}
                >
                  <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className={`font-semibold text-lg ${isCompleted ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                          {step.skill}
                        </h3>
                        {isCompleted && <Badge variant="success" size="sm">Done</Badge>}
                      </div>
                      {step.category && (
                        <Badge variant="info" size="sm" className="mb-2">{step.category}</Badge>
                      )}
                      <div className="flex flex-wrap items-center gap-3 text-sm text-gray-500 mt-1">
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
                      {step.resources && step.resources.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 mt-3">
                          {step.resources.map(r => (
                            <span key={r} className="bg-blue-50 text-blue-700 px-2 py-0.5 rounded text-xs font-medium">{r}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </Card>
              </div>
            );
          })}
        </div>
      </div>

      {projects.length > 0 && (
        <div className="mt-12">
          <h2 className="text-2xl font-bold mb-6">Recommended Projects</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects.map((p: ProjectRecommendation, i: number) => (
              <Card key={i} hover className="slide-up" style={{ animationDelay: `${i * 60}ms` } as React.CSSProperties}>
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-semibold text-gray-900">{p.title}</h4>
                  <Badge
                    variant={p.difficulty === 'easy' || p.difficulty === 'beginner' ? 'success' : p.difficulty === 'medium' || p.difficulty === 'intermediate' ? 'warning' : 'danger'}
                    size="sm"
                  >
                    {p.difficulty}
                  </Badge>
                </div>
                <p className="text-sm text-gray-500 mb-3">
                  {p.estimated_hours}h estimated
                  {p.reason && <span className="ml-2">· {p.reason}</span>}
                </p>
                <div className="flex flex-wrap gap-1.5">
                  {p.skills?.map(s => (
                    <Badge key={s} variant="info" size="sm">{s}</Badge>
                  ))}
                </div>
              </Card>
            ))}
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
