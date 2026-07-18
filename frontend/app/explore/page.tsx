'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card } from '@/components/ui/Card';
import Badge from '@/components/ui/Badge';
import Button from '@/components/ui/Button';
import Skeleton from '@/components/ui/Skeleton';
import { SUPPORTED_CAREERS } from '@/constants';
import { Career, Certification, RoadmapStep } from '@/types';
import { getCareers, getCertifications, getLearningPath, getSkillResources } from '@/services/api';
import { useToast } from '@/components/ui';

interface ResourceLink {
  name: string;
  url: string;
  type: string;
}

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
  'Security Architect': {
    description: 'Design and oversee enterprise security infrastructure. Build zero trust architectures and security policies.',
    icon: '🏗️',
    skills: ['Networking', 'Firewalls', 'IAM', 'Threat Modeling', 'Docker'],
  },
  'DevSecOps Engineer': {
    description: 'Integrate security into CI/CD pipelines. Automate security testing and enforce compliance in deployments.',
    icon: '⚙️',
    skills: ['CI/CD', 'Docker', 'Kubernetes', 'SAST', 'Terraform'],
  },
  'GRC Analyst': {
    description: 'Manage governance, risk, and compliance programs. Ensure organizations meet regulatory and security standards.',
    icon: '📋',
    skills: ['Compliance Frameworks', 'NIST', 'ISO 27001', 'Risk Assessment', 'Security Auditing'],
  },
  'Incident Responder': {
    description: 'Lead response to security breaches. Coordinate containment, eradication, and recovery efforts.',
    icon: '🚨',
    skills: ['Incident Response', 'SIEM', 'Memory Analysis', 'Network Forensics', 'MITRE ATT&CK'],
  },
};

const ROLE_RESOURCE_ICONS: Record<string, string> = {
  course: 'M12 6.042a8.967 8.967 0 00-3.597.093A7.025 7.025 0 005.05 8.04a6.966 6.966 0 00-1.68 4.62c0 3.867 3.133 7 7 7s7-3.133 7-7a6.966 6.966 0 00-1.68-4.62 7.025 7.025 0 00-3.402-.894A8.967 8.967 0 0012 6.042z',
  book: 'M12 6.042a8.967 8.967 0 00-3.597.093A7.025 7.025 0 005.05 8.04a6.966 6.966 0 00-1.68 4.62c0 3.867 3.133 7 7 7s7-3.133 7-7a6.966 6.966 0 00-1.68-4.62 7.025 7.025 0 00-3.402-.894A8.967 8.967 0 0012 6.042z',
  'hands-on': 'M15.042 21.672L13.684 16.6m0 0l-2.51 2.225.569-9.47 5.227 7.917-3.286-.672zM12 2.25V4.5m5.834.166l-1.591 1.591M20.25 10.5H18M7.757 14.743l-1.59 1.59M6 10.5H3.75m4.007-4.243l-1.59-1.59',
  tool: 'M11.42 15.17l-5.1-5.1m0 0L11.42 4.97m-5.1 5.1H3.75m7.67-7.67l5.1 5.1m0 0l-5.1 5.1m5.1-5.1H20.25',
  docs: 'M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z',
  article: 'M12 7.5h1.5m-1.5 3h1.5m-7.5 3h7.5m-7.5 3h7.5m3-9h3.375c.621 0 1.125.504 1.125 1.125V18a2.25 2.25 0 01-2.25 2.25M16.5 7.5V18a2.25 2.25 0 002.25 2.25M16.5 7.5V4.875c0-.621-.504-1.125-1.125-1.125H4.125C3.504 3.75 3 4.254 3 4.875V18a2.25 2.25 0 002.25 2.25h13.5',
};

function ResourceIcon({ type }: { type: string }) {
  const path = ROLE_RESOURCE_ICONS[type] || ROLE_RESOURCE_ICONS['course'];
  return (
    <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d={path} />
    </svg>
  );
}

function SkillResources({ skill, resources, loading }: { skill: string; resources: ResourceLink[]; loading: boolean }) {
  if (loading) {
    return (
      <div className="mt-2 ml-4 flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
        <svg className="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        Loading resources...
      </div>
    );
  }

  if (resources.length === 0) return null;

  return (
    <div className="mt-2 ml-4 space-y-1">
      {resources.map((r) => (
        <a
          key={r.url}
          href={r.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 p-1.5 rounded-md bg-gray-50 dark:bg-gray-800/80 border border-gray-100 dark:border-gray-700 hover:border-primary/40 dark:hover:border-primary/40 hover:bg-primary/5 dark:hover:bg-primary/5 transition-all group"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex items-center justify-center w-5 h-5 rounded bg-primary/10 dark:bg-primary/20 text-primary flex-shrink-0">
            <ResourceIcon type={r.type} />
          </div>
          <span className="text-xs font-medium text-gray-700 dark:text-gray-300 group-hover:text-primary truncate">
            {r.name}
          </span>
          <svg className="w-3 h-3 text-gray-400 group-hover:text-primary flex-shrink-0 ml-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 6H5.25A2.25 2.25 0 003 8.25v10.5A2.25 2.25 0 005.25 21h10.5A2.25 2.25 0 0018 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
          </svg>
        </a>
      ))}
    </div>
  );
}

export default function ExplorePage() {
  const [careers, setCareers] = useState<Career[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSkill, setSelectedSkill] = useState<string | null>(null);
  const [expandedRole, setExpandedRole] = useState<string | null>(null);

  const [certifications, setCertifications] = useState<Record<string, Certification[]>>({});
  const [loadingCerts, setLoadingCerts] = useState<Record<string, boolean>>({});

  const [learningPath, setLearningPath] = useState<Record<string, RoadmapStep[]>>({});
  const [loadingPath, setLoadingPath] = useState<Record<string, boolean>>({});

  const [resources, setResources] = useState<Record<string, ResourceLink[]>>({});
  const [loadingResources, setLoadingResources] = useState<Record<string, boolean>>({});

  const [expandedSkill, setExpandedSkill] = useState<string | null>(null);

  useEffect(() => {
    getCareers()
      .then(data => {
        if (data.success && data.data) setCareers(data.data);
        else fallback();
      })
      .catch(() => fallback())
      .finally(() => setLoading(false));

    function fallback() {
      setCareers(SUPPORTED_CAREERS.map(c => ({
        id: c.id,
        title: c.title,
        description: careerDescriptions[c.title]?.description || '',
      })));
    }
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

  const fetchCertifications = useCallback(async (roleName: string) => {
    if (certifications[roleName]) return;
    setLoadingCerts(prev => ({ ...prev, [roleName]: true }));
    try {
      const res = await getCertifications(roleName);
      setCertifications(prev => ({ ...prev, [roleName]: res.data || [] }));
    } catch {
      setCertifications(prev => ({ ...prev, [roleName]: [] }));
    } finally {
      setLoadingCerts(prev => ({ ...prev, [roleName]: false }));
    }
  }, [certifications]);

  const fetchLearningPath = useCallback(async (career: string) => {
    if (learningPath[career]) return;
    setLoadingPath(prev => ({ ...prev, [career]: true }));
    try {
      const res = await getLearningPath(career);
      const seq: (string | { skill: string })[] = res.data?.sequence || [];
      const steps: RoadmapStep[] = seq.map((s, i) => ({
        step: i + 1,
        skill: typeof s === 'string' ? s : s.skill || String(s),
        category: '',
        estimated_hours: 0,
        prerequisites: [],
      }));
      setLearningPath(prev => ({ ...prev, [career]: steps }));
    } catch {
      setLearningPath(prev => ({ ...prev, [career]: [] }));
    } finally {
      setLoadingPath(prev => ({ ...prev, [career]: false }));
    }
  }, [learningPath]);

  const fetchSkillResources = useCallback(async (skillName: string) => {
    if (resources[skillName]) return;
    setLoadingResources(prev => ({ ...prev, [skillName]: true }));
    try {
      const res = await getSkillResources(skillName);
      setResources(prev => ({ ...prev, [skillName]: res.data || [] }));
    } catch {
      setResources(prev => ({ ...prev, [skillName]: [] }));
    } finally {
      setLoadingResources(prev => ({ ...prev, [skillName]: false }));
    }
  }, [resources]);

  const handleExplore = (roleName: string) => {
    if (expandedRole === roleName) {
      setExpandedRole(null);
      setExpandedSkill(null);
    } else {
      setExpandedRole(roleName);
      setExpandedSkill(null);
      fetchCertifications(roleName);
      fetchLearningPath(roleName);
    }
  };

  const handleSkillClick = (skillName: string) => {
    if (expandedSkill === skillName) {
      setExpandedSkill(null);
    } else {
      setExpandedSkill(skillName);
      fetchSkillResources(skillName);
    }
  };

  const difficultyVariant = (diff: string): 'success' | 'warning' | 'danger' => {
    if (diff === 'beginner' || diff === 'easy') return 'success';
    if (diff === 'intermediate' || diff === 'medium') return 'warning';
    return 'danger';
  };

  return (
    <div className="page-container fade-in">
      <div className="mb-8">
        <h1 className="page-title">Explore Cybersecurity Careers</h1>
        <p className="page-subtitle max-w-2xl">
          Discover the right cybersecurity career path for you. Each role has unique skills, certifications, and project requirements.
        </p>
      </div>

      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Filter by Skill</h3>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedSkill(null)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-1 ${!selectedSkill ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'}`}
          >
            All Careers
          </button>
          {allSkills.map(skill => (
            <button
              key={skill}
              onClick={() => setSelectedSkill(selectedSkill === skill ? null : skill)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-1 ${selectedSkill === skill ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'}`}
            >
              {skill}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => (
            <div key={i} className="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 space-y-4">
              <Skeleton className="h-6 w-1/3" />
              <Skeleton className="h-4 w-2/3" />
              <Skeleton className="h-4 w-1/2" />
              <div className="flex gap-2">
                <Skeleton className="h-6 w-16 rounded-full" />
                <Skeleton className="h-6 w-20 rounded-full" />
              </div>
            </div>
          ))}
        </div>
      ) : (
        <>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            Showing {filteredCareers.length} career{filteredCareers.length !== 1 ? 's' : ''}
            {selectedSkill && ` matching "${selectedSkill}"`}
          </p>

          <div className="space-y-4">
            {filteredCareers.map((career, idx) => {
              const info = careerDescriptions[career.title];
              const isExpanded = expandedRole === career.title;

              return (
                <div key={career.id || career.title} className="slide-up" style={{ animationDelay: `${idx * 40}ms` } as React.CSSProperties}>
                  <Card
                    hover={!isExpanded}
                    className={`transition-all duration-300 ${isExpanded ? 'ring-2 ring-primary/30 dark:ring-primary/40 shadow-lg' : 'hover:shadow-lg hover:-translate-y-0.5'}`}
                  >
                    <div
                      className="cursor-pointer"
                      onClick={() => handleExplore(career.title)}
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <span className="text-3xl">{info?.icon || '🛡️'}</span>
                            <div>
                              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">{career.title}</h3>
                              {career.estimated_weeks && (
                                <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                                  <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                                  </svg>
                                  ~{career.estimated_weeks} weeks to learn
                                </span>
                              )}
                            </div>
                          </div>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                            {career.description || info?.description || ''}
                          </p>
                          <div className="flex flex-wrap gap-1.5">
                            {(info?.skills || []).slice(0, 5).map(s => (
                              <Badge key={s} variant="primary" size="sm">{s}</Badge>
                            ))}
                          </div>
                        </div>

                        <div className="flex flex-col items-end gap-2 flex-shrink-0">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleExplore(career.title);
                            }}
                          >
                            {isExpanded ? 'Close' : 'Explore Role →'}
                          </Button>
                          <svg
                            className={`w-5 h-5 text-gray-400 dark:text-gray-500 transition-transform duration-300 ${isExpanded ? 'rotate-180' : ''}`}
                            fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                          </svg>
                        </div>
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700 space-y-6 fade-in">

                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 flex items-center gap-2">
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
                            </svg>
                            Required Skills
                          </h4>
                          <div className="space-y-1">
                            {(info?.skills || []).map(skill => (
                              <div key={skill}>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleSkillClick(skill);
                                  }}
                                  className={`w-full text-left flex items-center gap-2 px-3 py-2 rounded-lg transition-all text-sm ${expandedSkill === skill ? 'bg-primary/10 dark:bg-primary/20 text-primary' : 'hover:bg-gray-50 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300'}`}
                                >
                                  <span className="w-2 h-2 rounded-full bg-primary/60 flex-shrink-0" />
                                  <span className="font-medium">{skill}</span>
                                  <svg
                                    className={`w-3 h-3 ml-auto transition-transform duration-200 ${expandedSkill === skill ? 'rotate-180' : ''}`}
                                    fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
                                  >
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                                  </svg>
                                </button>
                                {expandedSkill === skill && (
                                  <SkillResources
                                    skill={skill}
                                    resources={resources[skill] || []}
                                    loading={loadingResources[skill] || false}
                                  />
                                )}
                              </div>
                            ))}
                          </div>
                        </div>

                        {learningPath[career.title] && learningPath[career.title].length > 0 && (
                          <div>
                            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 010 3.75H5.625a1.875 1.875 0 010-3.75z" />
                              </svg>
                              Learning Path
                            </h4>
                            <div className="relative pl-6">
                              <div className="absolute left-2 top-2 bottom-2 w-0.5 bg-primary/20 dark:bg-primary/30" />
                              <div className="space-y-3">
                                {learningPath[career.title].map((step, i) => (
                                  <div key={i} className="relative flex items-start gap-3">
                                    <div className="absolute -left-4 w-4 h-4 rounded-full bg-primary/20 dark:bg-primary/30 border-2 border-primary/50 flex-shrink-0 z-10" />
                                    <div className="flex-1 bg-gray-50 dark:bg-gray-800/60 rounded-lg px-3 py-2 border border-gray-100 dark:border-gray-700">
                                      <div className="flex items-center justify-between">
                                        <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                                          {i + 1}. {step.skill}
                                        </span>
                                        {step.estimated_hours > 0 && (
                                          <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                                            <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                              <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                                            </svg>
                                            {step.estimated_hours}h
                                          </span>
                                        )}
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        )}

                        {loadingPath[career.title] && (
                          <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                            </svg>
                            Loading learning path...
                          </div>
                        )}

                        {certifications[career.title] && certifications[career.title].length > 0 && (
                          <div>
                            <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3 flex items-center gap-2">
                              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5" />
                              </svg>
                              Recommended Certifications
                            </h4>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                              {certifications[career.title].map((cert) => (
                                <div
                                  key={cert.name}
                                  className="flex items-center gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800/60 border border-gray-100 dark:border-gray-700"
                                >
                                  <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-accent/10 dark:bg-accent/20 text-accent flex-shrink-0">
                                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.436 60.436 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5" />
                                    </svg>
                                  </div>
                                  <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium text-gray-800 dark:text-gray-200 truncate">{cert.name}</p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">{cert.vendor}</p>
                                  </div>
                                  <Badge variant={difficultyVariant(cert.difficulty)} size="sm">{cert.difficulty}</Badge>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {loadingCerts[career.title] && (
                          <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                            </svg>
                            Loading certifications...
                          </div>
                        )}

                        <div className="flex gap-3 pt-2">
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              window.location.href = `/upload?career=${encodeURIComponent(career.title)}`;
                            }}
                          >
                            Take Assessment for This Role
                          </Button>
                        </div>
                      </div>
                    )}
                  </Card>
                </div>
              );
            })}
          </div>

          {filteredCareers.length === 0 && (
            <div className="text-center py-16">
              <p className="text-gray-500 dark:text-gray-400 mb-4">No careers match the selected skill filter.</p>
              <Button variant="outline" onClick={() => setSelectedSkill(null)}>Show All Careers</Button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
