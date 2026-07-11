'use client';

import { useState, useEffect } from 'react';

export default function DashboardPage() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem('assessment');
    if (stored) setData(JSON.parse(stored));
  }, []);

  if (!data) {
    return (
      <div className="text-center py-20">
        <h1 className="text-3xl font-bold mb-4">No Assessment Found</h1>
        <p className="text-gray-600 mb-6">Complete a career assessment first.</p>
        <a href="/upload" className="bg-primary text-white px-6 py-3 rounded-lg hover:bg-blue-700">Start Assessment</a>
      </div>
    );
  }

  const readiness = data.career_readiness || 0;

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Career Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-sm border text-center">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Career Readiness</h3>
          <div className="text-4xl font-bold text-primary">{readiness}%</div>
          <div className="w-full bg-gray-200 rounded-full h-2 mt-3">
            <div className="bg-primary h-2 rounded-full" style={{ width: `${readiness}%` }} />
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Matched Skills</h3>
          <div className="text-4xl font-bold text-accent">{data.matched_skills?.length || 0}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="text-sm font-medium text-gray-500 mb-2">Missing Skills</h3>
          <div className="text-4xl font-bold text-error">{data.missing_skills?.length || 0}</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="font-semibold mb-3">Current Skills</h3>
          <div className="flex flex-wrap gap-2">
            {data.matched_skills?.map((s: string) => (
              <span key={s} className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">{s}</span>
            ))}
          </div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h3 className="font-semibold mb-3">Skills to Learn</h3>
          <div className="flex flex-wrap gap-2">
            {data.missing_skills?.map((s: string) => (
              <span key={s} className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm">{s}</span>
            ))}
          </div>
        </div>
      </div>

      {data.ai_summary && (
        <div className="bg-white p-6 rounded-lg shadow-sm border mt-6">
          <h3 className="font-semibold mb-3">AI Analysis</h3>
          <p className="text-gray-700 whitespace-pre-line">{data.ai_summary}</p>
        </div>
      )}

      <div className="mt-8 flex gap-4">
        <a href="/roadmap" className="bg-primary text-white px-6 py-3 rounded-lg hover:bg-blue-700">View Roadmap</a>
        <a href="/mentor" className="border border-primary text-primary px-6 py-3 rounded-lg hover:bg-blue-50">Ask AI Mentor</a>
      </div>
    </div>
  );
}
