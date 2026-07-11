'use client';

import { useState, useEffect } from 'react';
import { SUPPORTED_CAREERS } from '@/constants';

export default function ExplorePage() {
  const [careers, setCareers] = useState<any[]>([]);

  useEffect(() => {
    fetch('/api/v1/careers')
      .then(res => res.json())
      .then(data => setCareers(data.data || []))
      .catch(() => {
        setCareers(SUPPORTED_CAREERS.map(c => ({ id: c.id, title: c.title, description: '' })));
      });
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Explore Cybersecurity Careers</h1>
      <p className="text-gray-600 mb-8">Choose a career path to see required skills, certifications, and learning resources.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {careers.map((career) => (
          <div key={career.id} className="bg-white p-6 rounded-lg shadow-sm border hover:shadow-md transition">
            <h3 className="text-lg font-semibold mb-2">{career.title}</h3>
            <p className="text-sm text-gray-600 mb-4">{career.description}</p>
            <a href={`/upload?career=${encodeURIComponent(career.title)}`} className="text-primary text-sm font-medium hover:underline">
              Start Assessment →
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
