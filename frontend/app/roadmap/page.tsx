'use client';

import { useState, useEffect } from 'react';

export default function RoadmapPage() {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    const stored = sessionStorage.getItem('assessment');
    if (stored) setData(JSON.parse(stored));
  }, []);

  if (!data) {
    return (
      <div className="text-center py-20">
        <h1 className="text-3xl font-bold mb-4">No Roadmap Available</h1>
        <p className="text-gray-600 mb-6">Complete an assessment to generate your learning roadmap.</p>
        <a href="/upload" className="bg-primary text-white px-6 py-3 rounded-lg hover:bg-blue-700">Start Assessment</a>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Learning Roadmap</h1>
      <p className="text-gray-600 mb-8">Your personalized path to becoming a <strong>{data.career_goal}</strong></p>

      <div className="space-y-4">
        {data.roadmap?.map((step: any, i: number) => (
          <div key={i} className="bg-white p-6 rounded-lg shadow-sm border flex gap-4">
            <div className="flex-shrink-0 w-10 h-10 bg-primary text-white rounded-full flex items-center justify-center font-bold">
              {step.step || i + 1}
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-lg">{step.skill}</h3>
              <p className="text-sm text-gray-500 mt-1">
                {step.estimated_hours}h estimated
                {step.prerequisites?.length > 0 && ` · Prerequisites: ${step.prerequisites.join(', ')}`}
              </p>
              {step.resources?.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {step.resources.map((r: string) => (
                    <span key={r} className="bg-blue-50 text-blue-700 px-2 py-1 rounded text-xs">{r}</span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {data.estimated_weeks > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-sm border mt-6 text-center">
          <p className="text-gray-600">Estimated completion: <strong>{data.estimated_weeks} weeks</strong></p>
        </div>
      )}

      {data.projects?.length > 0 && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4">Recommended Projects</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.projects.map((p: any, i: number) => (
              <div key={i} className="bg-white p-5 rounded-lg shadow-sm border">
                <h4 className="font-semibold">{p.title}</h4>
                <p className="text-sm text-gray-500 mt-1">{p.difficulty} · {p.estimated_hours}h</p>
                <div className="flex flex-wrap gap-1 mt-2">
                  {p.skills?.map((s: string) => (
                    <span key={s} className="bg-purple-100 text-purple-700 px-2 py-0.5 rounded text-xs">{s}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
