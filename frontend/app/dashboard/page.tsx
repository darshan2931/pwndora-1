'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Button from '@/components/ui/Button';
import { Card, CardHeader } from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Skeleton, { SkeletonDashboard } from '@/components/ui/Skeleton';
import { AssessmentData } from '@/types';
import { READINESS_THRESHOLDS, READINESS_LABELS } from '@/constants';
import { getAssessment } from '@/services/api';
import { useToast } from '@/components/ui';

function ReadinessGauge({ score }: { score: number }) {
  const radius = 70;
  const stroke = 10;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  const level = score >= READINESS_THRESHOLDS.medium ? 'high'
    : score >= READINESS_THRESHOLDS.low ? 'medium'
    : 'low';
  const label = READINESS_LABELS[level];

  const gaugeColors = {
    high: 'var(--color-accent)',
    medium: 'var(--color-warning)',
    low: 'var(--color-error)',
  };

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-44 h-44">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 160 160" aria-hidden="true">
          <circle cx="80" cy="80" r={radius} fill="none" className="stroke-gray-200 dark:stroke-gray-700" strokeWidth={stroke} />
          <circle
            cx="80" cy="80" r={radius} fill="none"
            stroke={gaugeColors[level]}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="gauge-ring"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-bold text-gray-900 dark:text-gray-100">{score}%</span>
          <span className={`text-sm font-medium ${label.color}`}>{label.text}</span>
        </div>
      </div>
    </div>
  );
}

function SkillBar({ skills, type }: { skills: string[]; type: 'matched' | 'missing' }) {
  if (!skills?.length) return <p className="text-sm text-gray-500">None</p>;
  return (
    <div className="flex flex-wrap gap-2">
      {skills.map((s) => (
        <Badge key={s} variant={type === 'matched' ? 'success' : 'danger'} size="md">
          {s}
        </Badge>
      ))}
    </div>
  );
}

export default function DashboardPage() {
  const router = useRouter();
  const { addToast } = useToast();
  const [data, setData] = useState<AssessmentData | null>(null);
  const [loading, setLoading] = useState(true);

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
        .catch(() => {
          addToast({
            title: 'Error',
            description: 'Failed to load assessment data. Please try again.',
            type: 'error'
          });
        });
    }

    setLoading(false);
  }, [addToast]);

  if (loading) {
    return (
      <div className="page-container fade-in">
        <Skeleton className="h-8 w-48 mb-6" />
        <SkeletonDashboard />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="page-container text-center py-20 fade-in">
        <div className="w-20 h-20 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-6">
          <svg className="w-10 h-10 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15a2.25 2.25 0 012.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25z" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold mb-3 text-gray-900 dark:text-gray-100">No Assessment Found</h1>
        <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
          Complete a career assessment to see your readiness score, skill gaps, and personalized recommendations.
        </p>
        <Button onClick={() => router.push('/upload')}>Start Assessment</Button>
      </div>
    );
  }

  const readiness = data.career_readiness || 0;

  return (
    <div className="page-container fade-in">
      <div className="mb-8">
        <h1 className="page-title">Career Dashboard</h1>
        <p className="page-subtitle">
          Your career assessment for <strong>{data.career_goal}</strong>
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <Card className="lg:col-span-1 flex items-center justify-center py-8">
          <ReadinessGauge score={readiness} />
        </Card>

        <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-6">
          <Card
            hover
            className="hover:shadow-lg hover:-translate-y-1 transition-all"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-accent/10 dark:bg-accent/20 rounded-xl flex items-center justify-center">
                <svg className="w-5 h-5 text-accent-dark dark:text-accent-light" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Matched Skills</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{data.matched_skills?.length || 0}</p>
              </div>
            </div>
          </Card>

          <Card
            hover
            className="hover:shadow-lg hover:-translate-y-1 transition-all"
          >
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-error/10 dark:bg-error/20 rounded-xl flex items-center justify-center">
                <svg className="w-5 h-5 text-error-dark dark:text-error-light" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                </svg>
              </div>
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Skills to Learn</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{data.missing_skills?.length || 0}</p>
              </div>
            </div>
          </Card>

          {data.estimated_weeks !== undefined && data.estimated_weeks > 0 && (
            <Card
              hover
              className="hover:shadow-lg hover:-translate-y-1 transition-all"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary/10 dark:bg-primary/20 rounded-xl flex items-center justify-center">
                  <svg className="w-5 h-5 text-primary-dark dark:text-primary-light" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Estimated Time</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{data.estimated_weeks} weeks</p>
                </div>
              </div>
            </Card>
          )}

          {data.study_hours && (
            <Card
              hover
              className="hover:shadow-lg hover:-translate-y-1 transition-all"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-secondary/10 dark:bg-secondary/20 rounded-xl flex items-center justify-center">
                  <svg className="w-5 h-5 text-secondary-dark dark:text-secondary-light" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Study Hours</p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{data.study_hours}h/week</p>
                </div>
              </div>
            </Card>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader
            title="Current Skills"
            subtitle={`${data.matched_skills?.length || 0} skills matched`}
            action={<Badge variant="success" dot>Matched</Badge>}
          />
          <div className="mt-4">
            <SkillBar skills={data.matched_skills || []} type="matched" />
          </div>
        </Card>

        <Card>
          <CardHeader
            title="Skills to Learn"
            subtitle={`${data.missing_skills?.length || 0} skills needed`}
            action={<Badge variant="danger" dot>Missing</Badge>}
          />
          <div className="mt-4">
            <SkillBar skills={data.missing_skills || []} type="missing" />
          </div>
        </Card>
      </div>

      {data.ai_summary && (
        <Card className="mb-8">
          <CardHeader
            title="AI Analysis"
            subtitle="Personalized insights about your career readiness"
          />
          <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <p className="text-gray-700 dark:text-gray-300 whitespace-pre-line leading-relaxed">{data.ai_summary}</p>
          </div>
        </Card>
      )}

      {data.recommended_projects && data.recommended_projects.length > 0 && (
        <Card className="mb-8">
          <CardHeader
            title="Recommended Projects"
            subtitle="Build these to strengthen your skill profile"
          />
          <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
            {data.recommended_projects.map((p, i) => (
              <div key={i} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                <h4 className="font-medium text-gray-900 dark:text-gray-100 text-sm">{p.title}</h4>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{p.difficulty} · {p.estimated_hours}h</p>
                <div className="flex flex-wrap gap-1 mt-2">
                  {p.skills?.slice(0, 3).map(s => (
                    <Badge key={s} variant="info" size="sm">{s}</Badge>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      <div className="flex flex-col sm:flex-row gap-3">
        <Button onClick={() => router.push('/roadmap')} size="lg">
          <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0l4.994 2.497c.317.158.69.158 1.006 0z" />
          </svg>
          View Roadmap
        </Button>
        <Button variant="outline" onClick={() => router.push('/mentor')} size="lg">
          <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H8.25m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0H12m4.125 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm0 0h-.375M21 12c0 4.556-4.03 8.25-9 8.25a9.764 9.764 0 01-2.555-.337A5.972 5.972 0 015.41 20.97a5.969 5.969 0 01-.474-.065 4.48 4.48 0 00.978-2.025c.09-.457-.133-.901-.467-1.226C3.93 16.178 3 14.189 3 12c0-4.556 4.03-8.25 9-8.25s9 3.694 9 8.25z" />
          </svg>
          Ask AI Mentor
        </Button>
        <Button variant="ghost" onClick={() => router.push('/upload')} size="lg">
          Retake Assessment
        </Button>
      </div>
    </div>
  );
}