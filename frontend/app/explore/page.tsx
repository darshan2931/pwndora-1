'use client';

import { useState, useEffect } from 'react';
import { Card } from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import Skeleton, { SkeletonCard } from '@/components/ui/Skeleton';
import { SUPPORTED_CAREERS } from '@/constants';
import { Career } from '@/types';
import Link from 'next/link';

const careerDescriptions: Record<string, { description: string; icon: string; skills: string[] }> = {
  'SOC Analyst': {
    description: 'Monitor and respond to security incidents. Analyze logs, detect threats, and ensure organizational security.',
    icon: '🔍',
    skills: ['SIEM', 'Log Analysis', 'Incident Response', 'TCP/IP', 'Linux'],
  },
  'Penetration Tester': {
    description: 'Identify and exploit vulnerabilities in systems and networks. Conduct authorized security assessments.',
    icon: '🔓',
    skills: ['Nmap', 'Metasploit', 'Enumeration', 'Privilege Escalation', 'Python'],
  },
  'Cloud Security Engineer': {
    description: 'Secure cloud infrastructure and services. Implement security controls across AWS, Azure, and GCP.',
    icon: '☁️',
    skills: ['AWS', 'Azure', 'Docker', 'Kubernetes', 'Terraform'],
  },
  'Application Security Engineer': {
    description: 'Secure software throughout its lifecycle. Perform code reviews, threat modeling, and vulnerability assessments.',
    icon: '🛡️',
    skills: ['Secure Coding', 'OWASP', 'SAST', 'DAST', 'Threat Modeling'],
  },
  'Threat Intelligence Analyst': {
    description: 'Research and analyze cyber threats. Track threat actors and provide actionable intelligence.',
    icon: '🕵️',
    skills: ['MITRE ATT&CK', 'Log Analysis', 'Python', 'Incident Response'],
  },
  'Digital Forensics Analyst': {
    description: 'Investigate cyber incidents by analyzing digital evidence. Recover data and reconstruct attack timelines.',
    icon: '🔬',
    skills: ['Memory Analysis', 'Disk Analysis', 'Log Analysis', 'Incident Response'],
  },
};

export default function ExplorePage() {
  const [careers, setCareers] = useState<Career[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSkill, setSelectedSkill] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/v1/careers')
      .then(res => res.json())
      .then(data => {
        if (data.success && data.data) setCareers(data.data);
        else {
          setCareers(SUPPORTED_CAREERS.map(c => ({
            id: c.id,
            title: c.title,
            description: careerDescriptions[c.title]?.description || '',
          })));
        }
      })
      .catch(() => {
        setCareers(SUPPORTED_CAREERS.map(c => ({
          id: c.id,
          title: c.title,
          description: careerDescriptions[c.title]?.description || '',
        })));
      })
      .finally(() => setLoading(false));
  }, []);

  const allSkills = Array.from(new Set(
    Object.values(careerDescriptions).flatMap(c => c.skills)
  )).sort();

  const filteredCareers = selectedSkill
    ? careers.filter(c => {
        const info = careerDescriptions[c.title];
        return info?.skills.includes(selectedSkill);
      })
    : careers;

  return (
    <div className="page-container fade-in">
      <div className="mb-8">
        <h1 className="page-title">Explore Cybersecurity Careers</h1>
        <p className="page-subtitle max-w-2xl">
          Discover the right cybersecurity career path for you. Each role has unique skills, certifications, and project requirements.
        </p>
      </div>

      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Filter by Skill</h3>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedSkill(null)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
              !selectedSkill ? 'bg-primary text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            All Careers
          </button>
          {allSkills.map(skill => (
            <button
              key={skill}
              onClick={() => setSelectedSkill(selectedSkill === skill ? null : skill)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                selectedSkill === skill ? 'bg-primary text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {skill}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => <SkeletonCard key={i} />)}
        </div>
      ) : (
        <>
          <p className="text-sm text-gray-500 mb-4">
            Showing {filteredCareers.length} career{filteredCareers.length !== 1 ? 's' : ''}
            {selectedSkill && ` matching "${selectedSkill}"`}
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCareers.map((career) => {
              const info = careerDescriptions[career.title];
              return (
                <Card key={career.id || career.title} hover className="flex flex-col slide-up">
                  <div className="flex items-center gap-3 mb-3">
                    <span className="text-3xl">{info?.icon || '🛡️'}</span>
                    <h3 className="text-lg font-semibold text-gray-900">{career.title}</h3>
                  </div>

                  <p className="text-sm text-gray-600 mb-4 flex-1">
                    {career.description || info?.description || ''}
                  </p>

                  <div className="mb-4">
                    <p className="text-xs font-medium text-gray-500 mb-2">Key Skills</p>
                    <div className="flex flex-wrap gap-1.5">
                      {(info?.skills || []).slice(0, 5).map(s => (
                        <Badge key={s} variant="primary" size="sm">{s}</Badge>
                      ))}
                    </div>
                  </div>

                  {career.estimated_weeks && (
                    <p className="text-xs text-gray-500 mb-3">
                      <svg className="w-3.5 h-3.5 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      ~{career.estimated_weeks} weeks to learn
                    </p>
                  )}

                  <Link href={`/upload?career=${encodeURIComponent(career.title)}`}>
                    <Button variant="outline" fullWidth size="sm">
                      Start Assessment →
                    </Button>
                  </Link>
                </Card>
              );
            })}
          </div>

          {filteredCareers.length === 0 && (
            <div className="text-center py-16">
              <p className="text-gray-500 mb-4">No careers match the selected skill filter.</p>
              <Button variant="outline" onClick={() => setSelectedSkill(null)}>Show All Careers</Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
