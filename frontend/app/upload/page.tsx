'use client';

import { Suspense, useState, useCallback, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Button from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Select, Textarea } from '@/components/ui/Input';
import { SUPPORTED_CAREERS } from '@/constants';
import { analyzeCareer, saveAssessment } from '@/services/api';

type UploadMode = 'file' | 'manual';

function UploadForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const preselectedCareer = searchParams.get('career') || '';

  const [careerGoal, setCareerGoal] = useState(preselectedCareer);
  const [studyHours, setStudyHours] = useState(10);
  const [manualSkills, setManualSkills] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [mode, setMode] = useState<UploadMode>('file');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
    else if (e.type === 'dragleave') setDragActive(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (droppedFile.type === 'application/pdf' || droppedFile.name.endsWith('.docx') || droppedFile.name.endsWith('.txt')) {
        setFile(droppedFile);
        setMode('file');
        setError('');
      } else {
        setError('Please upload a PDF, DOCX, or TXT file.');
      }
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
      setMode('file');
      setError('');
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!careerGoal) { setError('Please select a target career.'); return; }
    if (mode === 'file' && !file && !manualSkills) { setError('Please upload a resume or enter skills manually.'); return; }
    if (mode === 'manual' && !manualSkills.trim()) { setError('Please enter your skills.'); return; }

    setLoading(true);
    setError('');
    setProgress(0);

    const progressInterval = setInterval(() => {
      setProgress(prev => Math.min(prev + Math.random() * 15, 90));
    }, 200);

    const formData = new FormData();
    formData.append('career_goal', careerGoal);
    formData.append('study_hours', studyHours.toString());
    if (file) formData.append('resume', file);
    if (manualSkills.trim()) formData.append('manual_skills', manualSkills);

    try {
      const data = await analyzeCareer(formData);
      clearInterval(progressInterval);
      setProgress(100);

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

        setTimeout(() => router.push('/dashboard'), 400);
      } else {
        setError('Analysis failed. Please try again.');
        setProgress(0);
      }
    } catch {
      clearInterval(progressInterval);
      setError('Failed to analyze your profile. Please try again.');
      setProgress(0);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto fade-in">
      <div className="mb-8">
        <h1 className="page-title">Career Assessment</h1>
        <p className="page-subtitle mt-2">
          Upload your resume or enter your skills to get a personalized career analysis.
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <Card padding="lg" className="space-y-6 hover:shadow-lg hover:-translate-y-1 transition-all">
          <Select
            label="Target Career"
            value={careerGoal}
            onChange={e => { setCareerGoal(e.target.value); setError(''); }}
            options={SUPPORTED_CAREERS.map(c => ({ value: c.title, label: c.title }))}
            placeholder="Select a career path..."
          />

          <div>
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
                aria-label="Weekly study hours"
              />
              <span className="w-16 text-center font-semibold text-primary bg-primary/10 px-3 py-1 rounded-lg text-sm">
                {studyHours}h/wk
              </span>
            </div>
          </div>

          <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
            <button
              type="button"
              onClick={() => setMode('file')}
              className={`flex-1 py-2 rounded-md text-sm font-medium transition-all ${mode === 'file' ? 'bg-white dark:bg-gray-600 text-primary shadow-sm' : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-600'}`}
            >
              Upload Resume
            </button>
            <button
              type="button"
              onClick={() => setMode('manual')}
              className={`flex-1 py-2 rounded-md text-sm font-medium transition-all ${mode === 'manual' ? 'bg-white dark:bg-gray-600 text-primary shadow-sm' : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 hover:bg-gray-100 dark:hover:bg-gray-600'}`}
            >
              Enter Skills Manually
            </button>
          </div>

          {mode === 'file' ? (
            <div
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`
                border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all
                ${dragActive ? 'border-primary bg-primary/5' : file ? 'border-accent bg-accent/5' : 'border-gray-300 dark:border-gray-600 hover:border-primary hover:bg-gray-50 dark:hover:bg-gray-700/50'}
              `}
              role="button"
              aria-label="Upload resume file"
              tabIndex={0}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={handleFileChange}
                className="hidden"
                aria-hidden="true"
              />
              {file ? (
                <div className="space-y-2">
                  <svg className="w-10 h-10 text-accent mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                  </svg>
                  <p className="font-medium text-gray-900 dark:text-gray-100">{file.name}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{formatFileSize(file.size)}</p>
                  <button
                    type="button"
                    onClick={(e) => { e.stopPropagation(); setFile(null); }}
                    className="text-sm text-error hover:underline"
                  >
                    Remove file
                  </button>
                </div>
              ) : (
                <div className="space-y-2">
                  <svg className="w-10 h-10 text-gray-400 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                  </svg>
                  <p className="font-medium text-gray-900 dark:text-gray-100">
                    <span className="text-primary">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">PDF, DOCX, or TXT (max 10MB)</p>
                </div>
              )}
            </div>
          ) : (
            <Textarea
              label="Your Skills (comma-separated)"
              value={manualSkills}
              onChange={e => { setManualSkills(e.target.value); setError(''); }}
              placeholder="e.g. Linux, Python, TCP/IP, SIEM, Nmap, Incident Response"
              rows={4}
              hint="Enter skills you currently have. They will be matched against our knowledge base."
            />
          )}

          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-error" role="alert">
              <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
              </svg>
              {error}
            </div>
          )}

          {loading && progress > 0 && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600 dark:text-gray-400">Analyzing your profile...</span>
                <span className="font-medium text-primary">{Math.round(progress)}%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          <Button
            type="submit"
            fullWidth
            size="lg"
            loading={loading}
            disabled={!careerGoal}
          >
            {loading ? 'Analyzing...' : 'Analyze My Profile'}
          </Button>
        </Card>
      </form>
    </div>
  );
}

export default function UploadPage() {
  return (
    <Suspense fallback={<div className="max-w-2xl mx-auto"><h1 className="text-3xl font-bold mb-6">Career Assessment</h1><p>Loading...</p></div>}>
      <UploadForm />
    </Suspense>
  );
}