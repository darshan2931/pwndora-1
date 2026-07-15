'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Button from '@/components/ui/Button';
import { Card, CardHeader } from '@/components/ui/Card';
import { Select, Textarea } from '@/components/ui/Input';
import Badge from '@/components/ui/Badge';
import { SUPPORTED_CAREERS } from '@/constants';
import { analyzeCareer, saveAssessment } from '@/services/api';

export default function AssessPage() {
  const router = useRouter();
  const [careerGoal, setCareerGoal] = useState('');
  const [studyHours, setStudyHours] = useState(10);
  const [manualSkills, setManualSkills] = useState('');
  const [step, setStep] = useState<'select' | 'skills' | 'loading'>('select');
  const [error, setError] = useState('');

  const handleCareerSelect = (career: string) => {
    setCareerGoal(career);
    setStep('skills');
  };

  const handleSubmit = async () => {
    if (!manualSkills.trim()) {
      setError('Please enter at least one skill.');
      return;
    }
    setStep('loading');
    setError('');

    const formData = new FormData();
    formData.append('career_goal', careerGoal);
    formData.append('study_hours', studyHours.toString());
    formData.append('manual_skills', manualSkills);

    try {
      const data = await analyzeCareer(formData);
      if (data.success) {
        const assessmentData = { ...data.data, study_hours: studyHours };
        sessionStorage.setItem('assessment', JSON.stringify(assessmentData));

        saveAssessment({
          career_goal: data.data.career_goal,
          matched_skills: data.data.matched_skills,
          missing_skills: data.data.missing_skills,
          readiness_score: data.data.career_readiness,
          roadmap: (data.data.roadmap || []).map(s => ({ ...s })),
          estimated_weeks: data.data.estimated_weeks || 0,
          ai_summary: data.data.ai_summary || '',
          study_hours: studyHours,
          projects: (data.data.recommended_projects || []).map(p => ({ ...p })),
        }).then(res => {
          if (res.success && res.data?.assessment_id) {
            sessionStorage.setItem('assessment_id', res.data.assessment_id);
          }
        }).catch(() => {});

        router.push('/dashboard');
      } else {
        setError('Analysis failed.');
        setStep('skills');
      }
    } catch {
      setError('Failed to analyze. Please try again.');
      setStep('skills');
    }
  };

  if (step === 'loading') {
    return (
      <div className="max-w-2xl mx-auto text-center py-20 fade-in">
        <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
          <svg className="w-8 h-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold mb-2 dark:text-gray-100">Analyzing Your Profile</h2>
        <p className="text-gray-600 dark:text-gray-400">Matching your skills against <strong>{careerGoal}</strong> requirements...</p>
        <div className="mt-6 w-64 mx-auto bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div className="bg-primary h-2 rounded-full animate-pulse" style={{ width: '60%' }} />
        </div>
      </div>
    );
  }

  if (step === 'skills') {
    return (
      <div className="max-w-2xl mx-auto fade-in">
        <div className="mb-6">
          <button onClick={() => setStep('select')} className="text-sm text-primary hover:underline mb-4 inline-flex items-center gap-1">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
            </svg>
            Back to career selection
          </button>
          <h1 className="page-title">Enter Your Skills</h1>
          <p className="page-subtitle">
            You selected <Badge variant="primary">{careerGoal}</Badge>. Now tell us what you know.
          </p>
        </div>

        <Card padding="lg">
          <CardHeader
            title="Your Skills"
            subtitle="Enter your cybersecurity skills, separated by commas"
          />
          <div className="mt-4">
            <Textarea
              value={manualSkills}
              onChange={e => { setManualSkills(e.target.value); setError(''); }}
              placeholder="e.g. Linux, Python, TCP/IP, SIEM, Nmap, Incident Response, AWS"
              rows={5}
            />
            {error && (
              <p className="mt-2 text-sm text-error" role="alert">{error}</p>
            )}
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
              Weekly Study Hours
            </label>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min={1}
                max={40}
                value={studyHours}
                onChange={e => setStudyHours(Number(e.target.value))}
                className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-primary"
              />
              <span className="w-16 text-center font-semibold text-primary bg-primary/10 px-3 py-1 rounded-lg text-sm">
                {studyHours}h
              </span>
            </div>
          </div>

          <div className="mt-6 flex gap-3">
            <Button variant="outline" onClick={() => setStep('select')}>Back</Button>
            <Button onClick={handleSubmit} fullWidth>Analyze My Skills</Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto fade-in">
      <div className="mb-8">
        <h1 className="page-title">Career Assessment</h1>
        <p className="page-subtitle">Choose your target career to get started.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {SUPPORTED_CAREERS.map((career) => (
          <button
            key={career.id}
            onClick={() => handleCareerSelect(career.title)}
            className={`
              text-left p-6 rounded-xl border-2 transition-all duration-200
              ${careerGoal === career.title
                ? 'border-primary bg-primary/5 shadow-md'
                : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-primary/50 hover:shadow-sm'
              }
            `}
          >
            <span className="text-3xl mb-3 block">{career.icon}</span>
            <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-1">{career.title}</h3>
            <p className="text-xs text-gray-500 dark:text-gray-400">Click to select →</p>
          </button>
        ))}
      </div>
    </div>
  );
}
