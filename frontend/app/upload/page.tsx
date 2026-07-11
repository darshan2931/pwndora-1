'use client';

import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { SUPPORTED_CAREERS } from '@/constants';

export default function UploadPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const preselectedCareer = searchParams.get('career') || '';

  const [careerGoal, setCareerGoal] = useState(preselectedCareer);
  const [studyHours, setStudyHours] = useState(10);
  const [manualSkills, setManualSkills] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    const formData = new FormData();
    formData.append('career_goal', careerGoal);
    formData.append('study_hours', studyHours.toString());
    if (file) formData.append('resume', file);
    else if (manualSkills) formData.append('manual_skills', manualSkills);

    try {
      const res = await fetch('/api/v1/career/analyze', { method: 'POST', body: formData });
      const data = await res.json();
      if (data.success) {
        sessionStorage.setItem('assessment', JSON.stringify(data.data));
        router.push('/dashboard');
      }
    } catch (err) {
      alert('Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Career Assessment</h1>
      <form onSubmit={handleSubmit} className="bg-white p-8 rounded-lg shadow-sm border space-y-6">
        <div>
          <label className="block text-sm font-medium mb-2">Target Career</label>
          <select value={careerGoal} onChange={e => setCareerGoal(e.target.value)} className="w-full border rounded-lg px-3 py-2" required>
            <option value="">Select a career...</option>
            {SUPPORTED_CAREERS.map(c => <option key={c.id} value={c.title}>{c.title}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Weekly Study Hours</label>
          <input type="number" value={studyHours} onChange={e => setStudyHours(Number(e.target.value))} min={1} max={40} className="w-full border rounded-lg px-3 py-2" />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Upload Resume (PDF/DOCX)</label>
          <input type="file" accept=".pdf,.docx,.txt" onChange={e => setFile(e.target.files?.[0] || null)} className="w-full border rounded-lg px-3 py-2" />
        </div>

        <div className="text-center text-sm text-gray-500">— OR —</div>

        <div>
          <label className="block text-sm font-medium mb-2">Manual Skills (comma-separated)</label>
          <textarea value={manualSkills} onChange={e => setManualSkills(e.target.value)} placeholder="Linux, Python, Networking, SIEM" className="w-full border rounded-lg px-3 py-2 h-20" />
        </div>

        <button type="submit" disabled={loading || !careerGoal} className="w-full bg-primary text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50">
          {loading ? 'Analyzing...' : 'Analyze My Profile'}
        </button>
      </form>
    </div>
  );
}
