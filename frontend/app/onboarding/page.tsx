'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/services/api';

// ─── Types ────────────────────────────────────────────────────────────────────

interface Skill {
  id: string;
  name: string;
  confirmed: boolean;
}

interface OnboardingState {
  name: string;
  targetRole: string;
  file: File | null;
  detectedSkills: Skill[];
  missingSkills: string[];
  studyHours: string;
  learningPrefs: string[];
  experience: string;
  readinessScore: number;
  roadmap: any[];
  estimatedWeeks: number;
}

// ─── Data ─────────────────────────────────────────────────────────────────────

const CAREER_GOALS = [
  {
    id: 'pentest',
    category: 'Offensive Security',
    title: 'Penetration Tester',
    icon: '🎯',
    color: 'from-red-500/20 to-orange-500/10',
    border: 'border-red-500/30 hover:border-red-500/60',
    badge: 'text-red-400 bg-red-500/10',
    certs: ['eJPT', 'OSCP', 'CEH'],
    desc: 'Find vulnerabilities before attackers do',
  },
  {
    id: 'soc',
    category: 'Defensive Security',
    title: 'SOC Analyst',
    icon: '🛡️',
    color: 'from-blue-500/20 to-cyan-500/10',
    border: 'border-blue-500/30 hover:border-blue-500/60',
    badge: 'text-blue-400 bg-blue-500/10',
    certs: ['CompTIA Security+', 'CySA+', 'GCIH'],
    desc: 'Monitor, detect, and respond to threats',
  },
  {
    id: 'cloud',
    category: 'Cloud Security',
    title: 'Cloud Security Engineer',
    icon: '☁️',
    color: 'from-violet-500/20 to-purple-500/10',
    border: 'border-violet-500/30 hover:border-violet-500/60',
    badge: 'text-violet-400 bg-violet-500/10',
    certs: ['AWS SAA', 'CCSP', 'AZ-500'],
    desc: 'Secure AWS, Azure & GCP infrastructure',
  },
  {
    id: 'dfir',
    category: 'Digital Forensics',
    title: 'DFIR Specialist',
    icon: '🔬',
    color: 'from-yellow-500/20 to-amber-500/10',
    border: 'border-yellow-500/30 hover:border-yellow-500/60',
    badge: 'text-yellow-400 bg-yellow-500/10',
    certs: ['GCFE', 'GCFA', 'EnCE'],
    desc: 'Investigate breaches and recover evidence',
  },
  {
    id: 'appsec',
    category: 'Application Security',
    title: 'AppSec Engineer',
    icon: '⚡',
    color: 'from-emerald-500/20 to-green-500/10',
    border: 'border-emerald-500/30 hover:border-emerald-500/60',
    badge: 'text-emerald-400 bg-emerald-500/10',
    certs: ['GWEB', 'CSSLP', 'OSWE'],
    desc: 'Secure software from code to production',
  },
  {
    id: 'grc',
    category: 'Governance & Compliance',
    title: 'GRC Analyst',
    icon: '📋',
    color: 'from-gray-500/20 to-slate-500/10',
    border: 'border-gray-500/30 hover:border-gray-500/60',
    badge: 'text-gray-400 bg-gray-500/10',
    certs: ['CISM', 'CISA', 'CRISC'],
    desc: 'Manage risk, policy & regulatory compliance',
  },
];

const STUDY_OPTIONS = [
  { id: 'lt5', label: 'Less than 5 hrs', sub: 'Casual learner' },
  { id: '5-10', label: '5–10 hrs', sub: 'Steady pace' },
  { id: '10-20', label: '10–20 hrs', sub: 'Committed' },
  { id: '20+', label: '20+ hrs', sub: 'Full throttle' },
];

const LEARNING_PREFS = [
  { id: 'video', label: 'Videos', icon: '▶' },
  { id: 'reading', label: 'Reading', icon: '📖' },
  { id: 'labs', label: 'Hands-on Labs', icon: '⚗️' },
  { id: 'projects', label: 'Projects', icon: '🛠' },
];

const EXPERIENCE_LEVELS = [
  { id: 'beginner', label: 'Beginner', desc: 'New to cybersecurity' },
  { id: 'intermediate', label: 'Intermediate', desc: 'Some IT or security background' },
  { id: 'advanced', label: 'Advanced', desc: 'Working in the field' },
];

const GENERATION_STAGES = [
  'Analyzing detected skills...',
  'Mapping career requirements...',
  'Calculating readiness score...',
  'Building your roadmap...',
  'Preparing your AI Mentor...',
  'Almost ready...',
];

// ─── Step Progress Indicator ──────────────────────────────────────────────────

const STEPS = ['Welcome', 'Goal', 'Resume', 'Review', 'Preferences', 'Generating', 'Done'];

function StepBar({ current }: { current: number }) {
  return (
    <div className="flex items-center justify-center gap-1.5 mb-10">
      {STEPS.map((label, i) => (
        <div key={label} className="flex items-center gap-1.5">
          <div className={`flex items-center justify-center rounded-full text-xs font-bold transition-all duration-300
            ${i < current ? 'w-6 h-6 bg-emerald-500 text-white' :
              i === current ? 'w-6 h-6 bg-blue-500 text-white ring-2 ring-blue-500/30' :
              'w-5 h-5 bg-white/5 text-gray-600 text-[10px]'}`}
          >
            {i < current ? (
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
              </svg>
            ) : i + 1}
          </div>
          {i < STEPS.length - 1 && (
            <div className={`h-px w-6 rounded transition-all duration-500 ${i < current ? 'bg-emerald-500' : 'bg-white/10'}`} />
          )}
        </div>
      ))}
    </div>
  );
}

// ─── Screens ──────────────────────────────────────────────────────────────────

function WelcomeScreen({ name, onNameChange, onNext }: {
  name: string;
  onNameChange: (v: string) => void;
  onNext: () => void;
}) {
  return (
    <div className="max-w-lg mx-auto text-center fade-in">
      <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-violet-500 flex items-center justify-center mx-auto mb-8 shadow-lg shadow-blue-500/25">
        <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
      </div>

      <h1 className="text-4xl font-extrabold text-white mb-3 tracking-tight">Welcome to Pwndora</h1>
      <p className="text-gray-400 mb-8 leading-relaxed">
        Let&apos;s build your cybersecurity profile.<br />
        This takes about 2 minutes.
      </p>

      <div className="grid grid-cols-2 gap-3 mb-10 text-left">
        {[
          { icon: '📊', label: 'Career Readiness Score' },
          { icon: '🗺️', label: 'Personalized Roadmap' },
          { icon: '🤖', label: 'AI Mentor (context-aware)' },
          { icon: '🎯', label: 'Daily Learning Missions' },
        ].map(item => (
          <div key={item.label} className="flex items-center gap-3 p-4 rounded-xl border border-white/5 bg-white/3">
            <span className="text-xl">{item.icon}</span>
            <span className="text-sm text-gray-300 font-medium">{item.label}</span>
          </div>
        ))}
      </div>

      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-400 mb-2 text-left">First, what&apos;s your name?</label>
        <input
          type="text"
          value={name}
          onChange={e => onNameChange(e.target.value)}
          placeholder="e.g. Alex"
          className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-600 focus:outline-none focus:border-blue-500/60 focus:ring-2 focus:ring-blue-500/20 transition-all"
          onKeyDown={e => e.key === 'Enter' && name.trim() && onNext()}
          autoFocus
        />
      </div>

      <button
        onClick={onNext}
        disabled={!name.trim()}
        className="w-full py-4 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-500 hover:to-violet-500 text-white font-semibold text-base transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed shadow-lg shadow-blue-500/25"
      >
        Get Started →
      </button>
    </div>
  );
}

function CareerGoalScreen({ selected, onSelect, name }: {
  selected: string;
  onSelect: (id: string, title: string) => void;
  name: string;
}) {
  return (
    <div className="max-w-2xl mx-auto fade-in">
      <div className="text-center mb-10">
        <h2 className="text-3xl font-extrabold text-white mb-2">What&apos;s your target, {name}?</h2>
        <p className="text-gray-400">Pick the career path you want to reach. You can change this later.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {CAREER_GOALS.map(goal => (
          <button
            key={goal.id}
            onClick={() => onSelect(goal.id, goal.title)}
            className={`text-left p-5 rounded-2xl border bg-gradient-to-br ${goal.color} ${goal.border} transition-all duration-200 hover:-translate-y-0.5 group
              ${selected === goal.id ? 'ring-2 ring-white/30 scale-[1.02]' : ''}`}
          >
            <div className="flex items-start justify-between mb-3">
              <span className="text-3xl">{goal.icon}</span>
              {selected === goal.id && (
                <div className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center">
                  <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                  </svg>
                </div>
              )}
            </div>
            <div className={`text-xs font-bold uppercase tracking-wider mb-1 ${goal.badge} inline-block px-2 py-0.5 rounded-full`}>
              {goal.category}
            </div>
            <h3 className="font-bold text-white text-lg mb-1">{goal.title}</h3>
            <p className="text-sm text-gray-400 mb-3">{goal.desc}</p>
            <div className="flex flex-wrap gap-1">
              {goal.certs.map(c => (
                <span key={c} className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-500 border border-white/5">{c}</span>
              ))}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

const UPLOAD_STAGES = ['Uploading...', 'Analyzing...', 'Detecting Skills...', 'Finding Projects...', 'Matching Career...'];

function ResumeUploadScreen({ file, onFile, onSkip }: {
  file: File | null;
  onFile: (f: File) => void;
  onSkip: () => void;
}) {
  const [drag, setDrag] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadStage, setUploadStage] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File) => {
    if (!['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(f.type) && !f.name.endsWith('.txt')) return;
    onFile(f);
    setUploading(true);
    let stage = 0;
    const interval = setInterval(() => {
      stage += 1;
      setUploadStage(stage);
      if (stage >= UPLOAD_STAGES.length - 1) clearInterval(interval);
    }, 600);
  }, [onFile]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault(); setDrag(false);
    if (e.dataTransfer.files?.[0]) handleFile(e.dataTransfer.files[0]);
  }, [handleFile]);

  return (
    <div className="max-w-lg mx-auto fade-in">
      <div className="text-center mb-10">
        <h2 className="text-3xl font-extrabold text-white mb-2">Upload Your Resume</h2>
        <p className="text-gray-400">Our AI will extract your skills, projects, and experience automatically.</p>
      </div>

      <input ref={inputRef} type="file" accept=".pdf,.docx,.txt" className="hidden" onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])} />

      {!file ? (
        <div
          onDragEnter={() => setDrag(true)}
          onDragLeave={() => setDrag(false)}
          onDragOver={e => e.preventDefault()}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={`relative cursor-pointer rounded-2xl border-2 border-dashed p-12 text-center transition-all duration-200
            ${drag ? 'border-blue-500 bg-blue-500/10' : 'border-white/10 hover:border-white/25 hover:bg-white/3'}`}
        >
          <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
          </div>
          <p className="text-white font-medium mb-1">
            <span className="text-blue-400">Click to upload</span> or drag and drop
          </p>
          <p className="text-sm text-gray-500">PDF or DOCX • Max 10MB</p>
        </div>
      ) : (
        <div className="rounded-2xl border border-white/10 bg-white/3 p-6">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 rounded-xl bg-blue-500/20 flex items-center justify-center">
              <svg className="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
              </svg>
            </div>
            <div>
              <p className="font-medium text-white text-sm">{file.name}</p>
              <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
            </div>
          </div>

          {/* Progress stages */}
          <div className="space-y-2.5">
            {UPLOAD_STAGES.map((stage, i) => (
              <div key={stage} className={`flex items-center gap-3 transition-all duration-300 ${i <= uploadStage ? 'opacity-100' : 'opacity-20'}`}>
                <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-300
                  ${i < uploadStage ? 'bg-emerald-500' : i === uploadStage ? 'bg-blue-500 animate-pulse' : 'bg-white/10'}`}>
                  {i < uploadStage ? (
                    <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                    </svg>
                  ) : (
                    <span className="w-1.5 h-1.5 rounded-full bg-current" />
                  )}
                </div>
                <span className={`text-sm ${i <= uploadStage ? 'text-gray-200' : 'text-gray-600'}`}>{stage}</span>
              </div>
            ))}
          </div>

          {/* Progress bar */}
          <div className="mt-5 h-1.5 rounded-full bg-white/5 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-violet-500 rounded-full transition-all duration-700"
              style={{ width: `${Math.round(((uploadStage + 1) / UPLOAD_STAGES.length) * 100)}%` }}
            />
          </div>
        </div>
      )}

      <button
        onClick={onSkip}
        className="w-full mt-4 py-2.5 text-sm text-gray-500 hover:text-gray-300 transition-colors"
      >
        Skip — enter skills manually instead
      </button>
    </div>
  );
}

function SkillReviewScreen({ skills, missing, onToggle, onAddSkill, onRemoveMissing, onAddMissing }: {
  skills: Skill[];
  missing: string[];
  onToggle: (id: string) => void;
  onAddSkill: (name: string) => void;
  onRemoveMissing?: (name: string) => void;
  onAddMissing?: (name: string) => void;
}) {
  const [newMissing, setNewMissing] = useState('');

  const handleAddMissing = () => {
    if (newMissing.trim() && onAddMissing) { onAddMissing(newMissing.trim()); setNewMissing(''); }
  };

  return (
    <div className="max-w-2xl mx-auto fade-in">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-extrabold text-white mb-2">Review Detected Skills</h2>
        <p className="text-gray-400">Our AI found these skills in your resume. Confirm what&apos;s accurate.</p>
      </div>

      {/* Detected skills */}
      <div className="rounded-2xl border border-white/10 bg-white/3 p-6 mb-5">
        <div className="flex items-center gap-2 mb-5">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <h3 className="font-semibold text-white text-sm">Skills Detected</h3>
          <span className="ml-auto text-xs text-gray-500">{skills.filter(s => s.confirmed).length} confirmed</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {skills.map(skill => (
            <button
              key={skill.id}
              onClick={() => onToggle(skill.id)}
              className={`group flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium border transition-all duration-200
                ${skill.confirmed
                  ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300 hover:bg-red-500/15 hover:border-red-500/30 hover:text-red-300'
                  : 'bg-red-500/10 border-red-500/20 text-red-400 line-through opacity-60 hover:opacity-100 hover:no-underline'
                }`}
            >
              {skill.confirmed ? (
                <svg className="w-3.5 h-3.5 group-hover:hidden" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
              ) : null}
              <svg className={`w-3.5 h-3.5 ${skill.confirmed ? 'hidden group-hover:block' : 'block'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
              {skill.name}
            </button>
          ))}
        </div>

      </div>

      {/* Missing skills */}
      <div className="rounded-2xl border border-white/10 bg-white/3 p-6">
        <div className="flex items-center gap-2 mb-5">
          <div className="w-2 h-2 rounded-full bg-amber-400" />
          <h3 className="font-semibold text-white text-sm">Skills You&apos;ll Need to Learn</h3>
          <span className="ml-auto text-xs text-gray-500">Based on your career goal</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {missing.map(skill => (
            <span key={skill} className="group flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm border border-amber-500/20 bg-amber-500/10 text-amber-400">
              {skill}
              {onRemoveMissing && (
                <button onClick={() => onRemoveMissing(skill)} className="hover:text-amber-200 ml-1">
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
                </button>
              )}
            </span>
          ))}
        </div>

        {/* Add missing skill */}
        <div className="flex gap-2 mt-4">
          <input
            type="text"
            value={newMissing}
            onChange={e => setNewMissing(e.target.value)}
            placeholder="+ Add a skill to learn..."
            onKeyDown={e => e.key === 'Enter' && handleAddMissing()}
            className="flex-1 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/20 transition-all"
          />
          <button
            onClick={handleAddMissing}
            disabled={!newMissing.trim()}
            className="px-4 py-2 rounded-lg bg-white/10 text-gray-300 text-sm font-medium hover:bg-white/15 transition-colors disabled:opacity-40"
          >
            Add
          </button>
        </div>
      </div>
    </div>
  );
}

function PreferencesScreen({ state, onChange }: {
  state: Pick<OnboardingState, 'studyHours' | 'learningPrefs' | 'experience'>;
  onChange: (key: string, val: string | string[]) => void;
}) {
  const togglePref = (id: string) => {
    const cur = state.learningPrefs;
    onChange('learningPrefs', cur.includes(id) ? cur.filter(p => p !== id) : [...cur, id]);
  };

  return (
    <div className="max-w-lg mx-auto fade-in">
      <div className="text-center mb-10">
        <h2 className="text-3xl font-extrabold text-white mb-2">How do you learn best?</h2>
        <p className="text-gray-400">We&apos;ll tailor your roadmap and daily missions to your style.</p>
      </div>

      {/* Study hours */}
      <div className="mb-8">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Weekly Study Hours</h3>
        <div className="grid grid-cols-2 gap-3">
          {STUDY_OPTIONS.map(opt => (
            <button
              key={opt.id}
              onClick={() => onChange('studyHours', opt.id)}
              className={`p-4 rounded-xl border text-left transition-all duration-200
                ${state.studyHours === opt.id
                  ? 'border-blue-500/60 bg-blue-500/15 ring-1 ring-blue-500/30'
                  : 'border-white/10 bg-white/3 hover:border-white/20 hover:bg-white/5'}`}
            >
              <div className="font-semibold text-white">{opt.label}</div>
              <div className="text-xs text-gray-500 mt-0.5">{opt.sub}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Learning preferences */}
      <div className="mb-8">
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Preferred Learning Style <span className="text-gray-600 normal-case">(pick all that apply)</span></h3>
        <div className="grid grid-cols-2 gap-3">
          {LEARNING_PREFS.map(pref => (
            <button
              key={pref.id}
              onClick={() => togglePref(pref.id)}
              className={`p-4 rounded-xl border text-left transition-all duration-200
                ${state.learningPrefs.includes(pref.id)
                  ? 'border-violet-500/60 bg-violet-500/15 ring-1 ring-violet-500/30'
                  : 'border-white/10 bg-white/3 hover:border-white/20 hover:bg-white/5'}`}
            >
              <span className="text-xl mb-1 block">{pref.icon}</span>
              <span className="font-medium text-white text-sm">{pref.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Experience */}
      <div>
        <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Experience Level</h3>
        <div className="space-y-3">
          {EXPERIENCE_LEVELS.map(lvl => (
            <button
              key={lvl.id}
              onClick={() => onChange('experience', lvl.id)}
              className={`w-full p-4 rounded-xl border text-left transition-all duration-200 flex items-center gap-3
                ${state.experience === lvl.id
                  ? 'border-emerald-500/60 bg-emerald-500/10 ring-1 ring-emerald-500/20'
                  : 'border-white/10 bg-white/3 hover:border-white/20 hover:bg-white/5'}`}
            >
              <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-all
                ${state.experience === lvl.id ? 'border-emerald-500 bg-emerald-500' : 'border-gray-600'}`}>
                {state.experience === lvl.id && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
              </div>
              <div>
                <div className="font-semibold text-white">{lvl.label}</div>
                <div className="text-xs text-gray-500">{lvl.desc}</div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function GeneratingScreen({ name }: { name: string }) {
  const [stage, setStage] = useState(0);
  const [done, setDone] = useState(false);

  useEffect(() => {
    let current = 0;
    const interval = setInterval(() => {
      current += 1;
      setStage(current);
      if (current >= GENERATION_STAGES.length - 1) {
        clearInterval(interval);
        setTimeout(() => setDone(true), 800);
      }
    }, 700);
    return () => clearInterval(interval);
  }, []);

  const progress = Math.round(((stage + 1) / GENERATION_STAGES.length) * 100);

  return (
    <div className="max-w-md mx-auto text-center fade-in">
      <div className={`w-20 h-20 rounded-2xl mx-auto mb-8 flex items-center justify-center transition-all duration-500 ${done ? 'bg-emerald-500 shadow-lg shadow-emerald-500/30' : 'bg-gradient-to-br from-blue-500 to-violet-500 shadow-lg shadow-blue-500/25'}`}>
        {done ? (
          <svg className="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
          </svg>
        ) : (
          <svg className="w-10 h-10 text-white animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        )}
      </div>

      <h2 className="text-3xl font-extrabold text-white mb-2">
        {done ? `${name}, your profile is ready!` : `Building Your Cyber Profile...`}
      </h2>
      <p className="text-gray-400 mb-10">
        {done ? 'Your AI mentor is standing by.' : 'Hang tight — this only takes a moment.'}
      </p>

      {/* Stage list */}
      <div className="space-y-3 text-left mb-8">
        {GENERATION_STAGES.map((s, i) => (
          <div key={s} className={`flex items-center gap-3 transition-all duration-300 ${i <= stage ? 'opacity-100' : 'opacity-20'}`}>
            <div className={`w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-300
              ${i < stage ? 'bg-emerald-500' : i === stage && !done ? 'bg-blue-500 animate-pulse' : i < GENERATION_STAGES.length && done ? 'bg-emerald-500' : 'bg-white/10'}`}>
              {(i < stage || done) ? (
                <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                </svg>
              ) : (
                <span className="w-1.5 h-1.5 rounded-full bg-current" />
              )}
            </div>
            <span className={`text-sm ${i <= stage ? 'text-gray-200' : 'text-gray-600'}`}>{s}</span>
          </div>
        ))}
      </div>

      {/* Progress bar */}
      <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-blue-500 to-emerald-400 rounded-full transition-all duration-700"
          style={{ width: `${done ? 100 : progress}%` }}
        />
      </div>
    </div>
  );
}

function SuccessScreen({ name, role, readinessScore, estimatedWeeks, onEnter }: { name: string; role: string; readinessScore: number; estimatedWeeks: number; onEnter: () => void }) {
  const [visible, setVisible] = useState(false);
  useEffect(() => { setTimeout(() => setVisible(true), 200); }, []);

  return (
    <div className={`max-w-lg mx-auto text-center transition-all duration-700 ${visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
      <div className="w-20 h-20 rounded-2xl bg-emerald-500 flex items-center justify-center mx-auto mb-8 shadow-2xl shadow-emerald-500/30">
        <svg className="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
        </svg>
      </div>

      <div className="text-xs font-bold uppercase tracking-widest text-emerald-500 mb-2">Cyber Profile Created</div>
      <h2 className="text-4xl font-extrabold text-white mb-1">Welcome, {name}.</h2>
      <p className="text-gray-400 mb-10">Your AI mentor is ready. Your roadmap is built.</p>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-10">
        {[
          { label: 'Career Goal', value: role, sub: '' },
          { label: 'Readiness', value: `${readinessScore}%`, sub: 'Current level' },
          { label: 'Est. Timeline', value: `${estimatedWeeks} wks`, sub: 'Estimated' },
        ].map(stat => (
          <div key={stat.label} className="p-4 rounded-2xl border border-white/5 bg-white/3">
            <div className="text-lg font-black text-white mb-1">{stat.value}</div>
            <div className="text-xs text-gray-400">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Today's mission preview */}
      <div className="p-5 rounded-2xl border border-blue-500/20 bg-blue-500/10 mb-8 text-left">
        <div className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-2">Today&apos;s Mission — Ready</div>
        <div className="font-semibold text-white">HTTP Authentication</div>
        <div className="text-sm text-gray-400 mt-1">Estimated 35 minutes · Your AI mentor is standing by</div>
      </div>

      <button
        onClick={onEnter}
        className="w-full py-4 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-500 hover:to-violet-500 text-white font-bold text-base transition-all duration-200 shadow-lg shadow-blue-500/25 hover:-translate-y-0.5"
      >
        Enter Dashboard →
      </button>
    </div>
  );
}

// ─── Main Wizard ───────────────────────────────────────────────────────────────

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [generatingDone, setGeneratingDone] = useState(false);

  const [state, setState] = useState<OnboardingState>({
    name: '',
    targetRole: '',
    file: null,
    detectedSkills: [],
    missingSkills: [],
    studyHours: '5-10',
    learningPrefs: ['labs'],
    experience: 'beginner',
    readinessScore: 0,
    roadmap: [],
    estimatedWeeks: 0,
  });

  const update = (key: keyof OnboardingState, val: unknown) =>
    setState(prev => ({ ...prev, [key]: val }));

  const next = () => setStep(s => s + 1);
  const back = () => setStep(s => s - 1);

  // Auto-advance from generating to success when generation is "done"
  useEffect(() => {
    if (step === 5 && generatingDone) {
      const t = setTimeout(() => setStep(6), 1200);
      return () => clearTimeout(t);
    }
  }, [step, generatingDone]);

  const canProceed = () => {
    switch (step) {
      case 0: return state.name.trim().length > 0;
      case 1: return state.targetRole !== '';
      case 2: return true; // resume is optional
      case 3: return state.detectedSkills.filter(s => s.confirmed).length > 0;
      case 4: return state.studyHours !== '' && state.experience !== '';
      default: return true;
    }
  };

  const screens = [
    <WelcomeScreen key="welcome" name={state.name} onNameChange={v => update('name', v)} onNext={next} />,
    <CareerGoalScreen key="goal" selected={state.targetRole} name={state.name} onSelect={(id, title) => { update('targetRole', title); setTimeout(next, 300); }} />,
    <ResumeUploadScreen key="upload" file={state.file} onFile={async f => {
      update('file', f); 
      try {
        const formData = new FormData();
        formData.append('resume', f);
        formData.append('career_goal', state.targetRole || 'Penetration Tester');
        formData.append('study_hours', state.studyHours || '10');
        const res = await api.analyzeResume(formData);
        
        if (res.success && res.data) {
          update('detectedSkills', (res.data.matched_skills || []).map((s: string, i: number) => ({ id: String(i), name: s, confirmed: true })));
          update('missingSkills', res.data.missing_skills || []);
          update('readinessScore', res.data.readiness_score || 0);
          update('roadmap', res.data.roadmap || []);
          update('estimatedWeeks', res.data.estimated_weeks || 0);
        }
      } catch (err) {
        console.error(err);
      }
      next();
    }} onSkip={next} />,
    <SkillReviewScreen
      key="review"
      skills={state.detectedSkills}
      missing={state.missingSkills}
      onToggle={id => update('detectedSkills', state.detectedSkills.map(s => s.id === id ? { ...s, confirmed: !s.confirmed } : s))}
      onAddSkill={name => update('detectedSkills', [...state.detectedSkills, { id: Date.now().toString(), name, confirmed: true }])}
      onRemoveMissing={name => update('missingSkills', state.missingSkills.filter(s => s !== name))}
      onAddMissing={name => update('missingSkills', [...state.missingSkills, name])}
    />,
    <PreferencesScreen
      key="prefs"
      state={{ studyHours: state.studyHours, learningPrefs: state.learningPrefs, experience: state.experience }}
      onChange={(k, v) => update(k as keyof OnboardingState, v)}
    />,
    <GeneratingScreen key="generating" name={state.name} />,
    <SuccessScreen key="success" name={state.name} role={state.targetRole || 'Penetration Tester'} readinessScore={state.readinessScore} estimatedWeeks={state.estimatedWeeks} onEnter={() => router.push('/dashboard')} />,
  ];

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top bar */}
      <div className="flex items-center justify-between px-6 py-5 border-b border-white/5">
        <div className="flex items-center gap-2 font-bold text-white text-sm">
          <svg className="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          Pwndora
        </div>
        <div className="text-xs text-gray-600">Step {step + 1} of {STEPS.length}</div>
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-10">
        <div className="w-full max-w-2xl">
          <StepBar current={step} />
          {screens[step]}
        </div>
      </div>

      {/* Bottom nav — hide on welcome (has its own button), career goal (auto-advances), resume (auto-advances), generating, success */}
      {![0, 1, 2, 5, 6].includes(step) && (
        <div className="border-t border-white/5 px-6 py-5 flex items-center justify-between max-w-2xl mx-auto w-full">
          <button
            onClick={back}
            className="flex items-center gap-2 text-gray-500 hover:text-gray-300 text-sm font-medium transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M11 17l-5-5m0 0l5-5m-5 5h12" />
            </svg>
            Back
          </button>
          <button
            onClick={async () => {
              if (step === 4) {
                next();
                try {
                   await api.saveAssessment({
                     career_goal: state.targetRole || 'Penetration Tester',
                     matched_skills: state.detectedSkills.filter(s => s.confirmed).map(s => s.name),
                     missing_skills: state.missingSkills,
                     readiness_score: state.readinessScore,
                     roadmap: state.roadmap,
                     estimated_weeks: state.estimatedWeeks,
                     study_hours: parseInt(state.studyHours) || 10
                   });
                } catch(e) {
                   console.error("Failed to save assessment", e);
                }
                setTimeout(() => setGeneratingDone(true), 1500);
              } else {
                next();
              }
            }}
            disabled={!canProceed()}
            className="flex items-center gap-2 px-8 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-500 hover:to-violet-500 text-white font-semibold text-sm transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed shadow-lg shadow-blue-500/20"
          >
            {step === 4 ? 'Generate My Profile' : 'Continue'}
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
}