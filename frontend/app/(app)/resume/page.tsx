'use client';

import { useEffect, useState, useRef, useCallback } from 'react';
import {
  FileText, Upload, CheckCircle2, AlertCircle, Loader2,
  Globe, Link2, Briefcase, GraduationCap,
  Award, Code, ExternalLink, Info, GitBranch, Star, GitFork, Search
} from 'lucide-react';
import { api } from '@/services/api';
import type { GitHubAnalysisData, GitHubRepoEvidence, GitHubTechEvidence, SkillEvidenceItem } from '@/types';
import { SkillEvidenceSection } from '@/components/SkillEvidenceSection';

type ProfileData = {
  id: string;
  status: string;
  profile: any;
  urls: any;
  metadata: any;
  error: string | null;
  created_at: string | null;
} | null;

const STATUS_LABELS: Record<string, { label: string; cls: string }> = {
  uploaded: { label: 'Uploaded', cls: 'badge-gray' },
  extracting: { label: 'Extracting Text...', cls: 'badge-yellow' },
  analyzing: { label: 'Analyzing with AI...', cls: 'badge-blue' },
  completed: { label: 'Completed', cls: 'badge-green' },
  failed: { label: 'Failed', cls: 'badge-red' },
};

function ProfileOverview({ profile }: { profile: any }) {
  if (!profile) return null;
  return (
    <div className="space-y-4">
      {(profile.full_name || profile.email || profile.phone || profile.location) && (
        <div className="surface p-5">
          <h3 className="text-section-title mb-3">Personal Information</h3>
          <div className="grid grid-cols-2 gap-3">
            {profile.full_name && (
              <div>
                <span className="text-label">Name</span>
                <p className="text-sm text-[#fafafa] mt-0.5">{profile.full_name}</p>
              </div>
            )}
            {profile.email && (
              <div>
                <span className="text-label">Email</span>
                <p className="text-sm text-[#fafafa] mt-0.5">{profile.email}</p>
              </div>
            )}
            {profile.phone && (
              <div>
                <span className="text-label">Phone</span>
                <p className="text-sm text-[#fafafa] mt-0.5">{profile.phone}</p>
              </div>
            )}
            {profile.location && (
              <div>
                <span className="text-label">Location</span>
                <p className="text-sm text-[#fafafa] mt-0.5">{profile.location}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {profile.summary && (
        <div className="surface p-5">
          <h3 className="text-section-title mb-2">Summary</h3>
          <p className="text-sm text-zinc-400 leading-relaxed">{profile.summary}</p>
        </div>
      )}

      {profile.experience?.length > 0 && (
        <div className="surface p-5">
          <div className="flex items-center gap-2 mb-4">
            <Briefcase className="w-4 h-4 text-blue-400" />
            <h3 className="text-section-title">Experience</h3>
            <span className="ml-auto badge-gray">{profile.experience.length}</span>
          </div>
          <div className="space-y-3">
            {profile.experience.map((exp: any, i: number) => (
              <div key={i} className="p-3 rounded-lg bg-white/[0.03] border border-white/[0.06]">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-sm font-semibold text-[#fafafa]">{exp.role}</span>
                  {exp.company && <span className="text-xs text-zinc-500">at {exp.company}</span>}
                </div>
                {exp.description && (
                  <p className="text-xs text-zinc-400 mt-1.5 leading-relaxed">{exp.description}</p>
                )}
                <div className="flex items-center gap-2 mt-2 flex-wrap">
                  {exp.start_date && (
                    <span className="text-[10px] text-zinc-600">
                      {exp.start_date} — {exp.end_date || 'Present'}
                    </span>
                  )}
                  {exp.technologies?.map((t: string) => (
                    <span key={t} className="badge-gray text-[10px]">{t}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {profile.education?.length > 0 && (
        <div className="surface p-5">
          <div className="flex items-center gap-2 mb-4">
            <GraduationCap className="w-4 h-4 text-violet-400" />
            <h3 className="text-section-title">Education</h3>
            <span className="ml-auto badge-gray">{profile.education.length}</span>
          </div>
          <div className="space-y-3">
            {profile.education.map((edu: any, i: number) => (
              <div key={i} className="p-3 rounded-lg bg-white/[0.03] border border-white/[0.06]">
                <div className="text-sm font-semibold text-[#fafafa]">
                  {edu.degree}{edu.field ? ` in ${edu.field}` : ''}
                </div>
                {edu.institution && (
                  <div className="text-xs text-zinc-400 mt-0.5">{edu.institution}</div>
                )}
                {edu.start_date && (
                  <div className="text-[10px] text-zinc-600 mt-1">
                    {edu.start_date} — {edu.end_date || 'Present'}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function SkillsSection({ skills }: { skills: any[] }) {
  if (!skills?.length) return null;
  return (
    <div className="surface p-5">
      <div className="flex items-center gap-2 mb-4">
        <Code className="w-4 h-4 text-emerald-400" />
        <h3 className="text-section-title">Skills</h3>
        <span className="ml-auto badge-gray">{skills.length}</span>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {skills.map((s: any, i: number) => (
          <span key={i} className="badge-blue">{s.name || s}</span>
        ))}
      </div>
    </div>
  );
}

function ProjectsSection({ projects }: { projects: any[] }) {
  if (!projects?.length) return null;
  return (
    <div className="surface p-5">
      <div className="flex items-center gap-2 mb-4">
        <Code className="w-4 h-4 text-blue-400" />
        <h3 className="text-section-title">Projects</h3>
        <span className="ml-auto badge-gray">{projects.length}</span>
      </div>
      <div className="space-y-3">
        {projects.map((p: any, i: number) => (
          <div key={i} className="p-3 rounded-lg bg-white/[0.03] border border-white/[0.06]">
            <div className="text-sm font-semibold text-[#fafafa]">{p.name}</div>
            {p.description && (
              <p className="text-xs text-zinc-400 mt-1 leading-relaxed">{p.description}</p>
            )}
            <div className="flex items-center gap-2 mt-2 flex-wrap">
              {p.technologies?.map((t: string) => (
                <span key={t} className="badge-violet text-[10px]">{t}</span>
              ))}
              {p.url && (
                <a href={p.url} target="_blank" rel="noopener noreferrer"
                  className="text-[10px] text-blue-400 hover:underline flex items-center gap-1 ml-auto">
                  <ExternalLink className="w-3 h-3" />Link
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function CertificationsSection({ certs }: { certs: any[] }) {
  if (!certs?.length) return null;
  return (
    <div className="surface p-5">
      <div className="flex items-center gap-2 mb-4">
        <Award className="w-4 h-4 text-amber-400" />
        <h3 className="text-section-title">Certifications</h3>
        <span className="ml-auto badge-gray">{certs.length}</span>
      </div>
      <div className="space-y-2">
        {certs.map((c: any, i: number) => (
          <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-white/[0.03] border border-white/[0.06]">
            <div className="w-7 h-7 rounded-lg bg-amber-500/10 flex items-center justify-center flex-shrink-0">
              <Award className="w-3.5 h-3.5 text-amber-400" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-semibold text-[#fafafa]">{c.name}</div>
              {c.issuer && <div className="text-[10px] text-zinc-500">{c.issuer}</div>}
            </div>
            {c.date && <span className="badge-gray text-[10px]">{c.date}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}

function DetectedLinks({ urls }: { urls: any }) {
  if (!urls) return null;
  const sections = [
    { key: 'github', label: 'GitHub', icon: Code, color: 'text-zinc-300' },
    { key: 'linkedin', label: 'LinkedIn', icon: Briefcase, color: 'text-blue-400' },
    { key: 'portfolio', label: 'Portfolio', icon: Globe, color: 'text-violet-400' },
    { key: 'personal_website', label: 'Personal Website', icon: Globe, color: 'text-emerald-400' },
    { key: 'other', label: 'Other Links', icon: Link2, color: 'text-zinc-400' },
  ];

  const hasAny = sections.some(s => urls[s.key]?.length > 0);
  if (!hasAny) return null;

  return (
    <div className="surface p-5">
      <div className="flex items-center gap-2 mb-4">
        <Link2 className="w-4 h-4 text-zinc-400" />
        <h3 className="text-section-title">Detected Links</h3>
      </div>
      <div className="space-y-3">
        {sections.map(s => {
          if (!urls[s.key]?.length) return null;
          const Icon = s.icon;
          return (
            <div key={s.key}>
              <span className="text-label mb-1.5 block">{s.label}</span>
              <div className="space-y-1">
                {urls[s.key].map((url: string, i: number) => (
                  <a key={i} href={url} target="_blank" rel="noopener noreferrer"
                    className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/[0.03] border border-white/[0.06] hover:border-white/[0.10] transition-colors group">
                    <Icon className={`w-3.5 h-3.5 ${s.color} flex-shrink-0`} />
                    <span className="text-xs text-zinc-300 group-hover:text-[#fafafa] truncate flex-1">{url}</span>
                    <ExternalLink className="w-3 h-3 text-zinc-700 group-hover:text-zinc-400 flex-shrink-0" />
                  </a>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function GitHubEvidenceSection({
  githubData,
  analyzing,
  onAnalyze,
  error,
}: {
  githubData: GitHubAnalysisData | null;
  analyzing: boolean;
  onAnalyze: () => void;
  error: string | null;
}) {
  if (!githubData && !analyzing) return null;

  const isCompleted = githubData?.status === 'completed';
  const isNoProfile = githubData?.status === 'no_github_profile';
  const username = githubData?.username;

  return (
    <div className="space-y-4">
      <div className="surface p-5">
        <div className="flex items-center gap-2 mb-4">
          <GitBranch className="w-4 h-4 text-zinc-300" />
          <h3 className="text-section-title">GitHub Evidence</h3>
          {isCompleted && (
            <span className="ml-auto badge-green">
              {githubData.repositories_analyzed} repos analyzed
            </span>
          )}
        </div>

        {isNoProfile && (
          <div className="flex items-start gap-2 p-3 rounded-lg bg-zinc-500/10 border border-zinc-500/20">
            <Info className="w-4 h-4 text-zinc-400 mt-0.5 flex-shrink-0" />
            <span className="text-sm text-zinc-400">
              {githubData.message || 'No GitHub profile detected in your resume.'}
            </span>
          </div>
        )}

        {username && isCompleted && (
          <div className="flex items-center gap-4 mb-4 flex-wrap">
            {githubData.avatar_url && (
              <img
                src={githubData.avatar_url}
                alt={username}
                className="w-10 h-10 rounded-full border border-white/10"
              />
            )}
            <div>
              <div className="text-sm font-semibold text-[#fafafa]">{username}</div>
              <div className="text-xs text-zinc-500">{githubData.profile_url}</div>
            </div>
            <div className="flex items-center gap-3 ml-auto">
              <div className="text-center">
                <div className="text-xs font-medium text-[#fafafa]">{githubData.public_repositories}</div>
                <div className="text-[10px] text-zinc-500">repos</div>
              </div>
              <div className="text-center">
                <div className="text-xs font-medium text-[#fafafa]">{githubData.followers}</div>
                <div className="text-[10px] text-zinc-500">followers</div>
              </div>
              <div className="text-center">
                <div className="text-xs font-medium text-[#fafafa]">{githubData.following}</div>
                <div className="text-[10px] text-zinc-500">following</div>
              </div>
            </div>
          </div>
        )}

        {!isCompleted && !isNoProfile && (
          <button
            onClick={onAnalyze}
            disabled={analyzing}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-500/15 text-blue-400 hover:bg-blue-500/25 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {analyzing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">Analyzing GitHub Evidence...</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span className="text-sm">Analyze GitHub Evidence</span>
              </>
            )}
          </button>
        )}

        {isCompleted && githubData.cached && (
          <button
            onClick={onAnalyze}
            disabled={analyzing}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/[0.04] text-zinc-400 hover:bg-white/[0.08] transition-colors text-xs disabled:opacity-50"
          >
            {analyzing ? <Loader2 className="w-3 h-3 animate-spin" /> : <Search className="w-3 h-3" />}
            Refresh
          </button>
        )}
      </div>

      {error && (
        <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
          <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
          <span className="text-sm text-red-400">{error}</span>
        </div>
      )}

      {isCompleted && githubData.all_technologies && githubData.all_technologies.length > 0 && (
        <ObservedTechnologies technologies={githubData.all_technologies} />
      )}

      {isCompleted && githubData.repositories && githubData.repositories.length > 0 && (
        <RepositoriesList repositories={githubData.repositories} />
      )}

      {isCompleted && (
        <div className="flex items-start gap-2 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
          <Info className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
          <div className="text-xs text-blue-400 leading-relaxed">
            These technologies were observed in public GitHub evidence. CyberPath will combine this with resume claims and assessments before calculating final skill confidence.
          </div>
        </div>
      )}
    </div>
  );
}

function ObservedTechnologies({ technologies }: { technologies: GitHubTechEvidence[] }) {
  const grouped: Record<string, string[]> = {};
  for (const t of technologies) {
    const tech = t.technology;
    if (!grouped[tech]) grouped[tech] = [];
    if (t.repository && !grouped[tech].includes(t.repository)) {
      grouped[tech].push(t.repository);
    }
  }

  const techEntries = Object.entries(grouped).sort((a, b) => b[1].length - a[1].length);

  return (
    <div className="surface p-5">
      <div className="flex items-center gap-2 mb-4">
        <Code className="w-4 h-4 text-emerald-400" />
        <h3 className="text-section-title">Observed Technologies</h3>
        <span className="ml-auto badge-gray">{techEntries.length}</span>
      </div>
      <div className="space-y-2">
        {techEntries.map(([tech, repos]) => (
          <div key={tech} className="flex items-start gap-3 p-2.5 rounded-lg bg-white/[0.03] border border-white/[0.06]">
            <span className="badge-blue text-xs mt-0.5">{tech}</span>
            <div className="flex-1 min-w-0">
              <span className="text-[10px] text-zinc-500 uppercase tracking-wider">Observed in:</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {repos.map(r => (
                  <span key={r} className="text-xs text-zinc-400">{r}</span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function RepositoriesList({ repositories }: { repositories: GitHubRepoEvidence[] }) {
  return (
    <div className="surface p-5">
      <div className="flex items-center gap-2 mb-4">
        <GitBranch className="w-4 h-4 text-blue-400" />
        <h3 className="text-section-title">Repository Analysis</h3>
        <span className="ml-auto badge-gray">{repositories.length}</span>
      </div>
      <div className="space-y-3">
        {repositories.map((repo) => (
          <RepoCard key={repo.full_name} repo={repo} />
        ))}
      </div>
    </div>
  );
}

function RepoCard({ repo }: { repo: GitHubRepoEvidence }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="p-3.5 rounded-lg bg-white/[0.03] border border-white/[0.06]">
      <div className="flex items-center gap-2 flex-wrap">
        <a
          href={repo.html_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm font-semibold text-[#fafafa] hover:text-blue-400 transition-colors flex items-center gap-1.5"
        >
          {repo.name}
          <ExternalLink className="w-3 h-3 text-zinc-600" />
        </a>
        <div className="flex items-center gap-2 ml-auto">
          {repo.stars > 0 && (
            <span className="flex items-center gap-1 text-xs text-zinc-400">
              <Star className="w-3 h-3" />{repo.stars}
            </span>
          )}
          {repo.forks > 0 && (
            <span className="flex items-center gap-1 text-xs text-zinc-400">
              <GitFork className="w-3 h-3" />{repo.forks}
            </span>
          )}
        </div>
      </div>

      {repo.description && (
        <p className="text-xs text-zinc-400 mt-1.5 leading-relaxed">{repo.description}</p>
      )}

      <div className="flex items-center gap-2 mt-2 flex-wrap">
        {repo.topics?.slice(0, 4).map((t) => (
          <span key={t} className="badge-violet text-[10px]">{t}</span>
        ))}
      </div>

      {repo.selection_reasons?.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {repo.selection_reasons.map((r, i) => (
            <span key={i} className="text-[10px] text-zinc-600 bg-white/[0.03] px-1.5 py-0.5 rounded">
              {r}
            </span>
          ))}
        </div>
      )}

      {repo.ai_analysis && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="mt-2 text-[10px] text-blue-400 hover:text-blue-300 transition-colors"
        >
          {expanded ? 'Hide analysis' : 'Show AI analysis'}
        </button>
      )}

      {expanded && repo.ai_analysis && (
        <div className="mt-3 p-3 rounded-lg bg-white/[0.02] border border-white/[0.04] space-y-2">
          {repo.ai_analysis.project_purpose && (
            <div>
              <span className="text-[10px] text-zinc-500 uppercase tracking-wider">Purpose</span>
              <p className="text-xs text-zinc-300 mt-0.5">{repo.ai_analysis.project_purpose}</p>
            </div>
          )}
          {repo.ai_analysis.complexity && (
            <div>
              <span className="text-[10px] text-zinc-500 uppercase tracking-wider">Complexity</span>
              <p className="text-xs text-zinc-300 mt-0.5">{repo.ai_analysis.complexity}</p>
            </div>
          )}
          {repo.ai_analysis.technical_domains?.length > 0 && (
            <div>
              <span className="text-[10px] text-zinc-500 uppercase tracking-wider">Technical Domains</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {repo.ai_analysis.technical_domains.map((d) => (
                  <span key={d} className="badge-gray text-[10px]">{d}</span>
                ))}
              </div>
            </div>
          )}
          {repo.ai_analysis.demonstrated_technologies?.length > 0 && (
            <div>
              <span className="text-[10px] text-zinc-500 uppercase tracking-wider">Demonstrated Technologies</span>
              <div className="mt-1 space-y-1">
                {repo.ai_analysis.demonstrated_technologies.map((t) => (
                  <div key={t.name} className="text-xs">
                    <span className="text-zinc-300 font-medium">{t.name}</span>
                    <span className="text-zinc-500 ml-1.5">{t.evidence}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          {repo.ai_analysis.cybersecurity_relevance?.is_relevant && (
            <div>
              <span className="text-[10px] text-zinc-500 uppercase tracking-wider">Cybersecurity Relevance</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {repo.ai_analysis.cybersecurity_relevance.areas?.map((a) => (
                  <span key={a} className="badge-yellow text-[10px]">{a}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function ResumePage() {
  const [profile, setProfile] = useState<ProfileData>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const [githubData, setGithubData] = useState<GitHubAnalysisData | null>(null);
  const [githubLoading, setGithubLoading] = useState(false);
  const [githubError, setGithubError] = useState<string | null>(null);
  const [skillEvidenceData, setSkillEvidenceData] = useState<{ evidence: SkillEvidenceItem[]; total_skills: number; high_confidence: number; medium_confidence: number; low_confidence: number; minimal_confidence: number; average_confidence: number; analysis_status: string } | null>(null);
  const [skillEvidenceLoading, setSkillEvidenceLoading] = useState(false);
  const [skillEvidenceError, setSkillEvidenceError] = useState<string | null>(null);

  useEffect(() => {
    loadProfile();
  }, []);

  useEffect(() => {
    if (profile?.status === 'completed' && profile?.urls?.github?.length > 0) {
      loadGithubProfile();
    }
  }, [profile?.status]);

  useEffect(() => {
    if (profile?.status === 'completed') {
      loadSkillEvidence();
    }
  }, [profile?.status]);

  async function loadProfile() {
    try {
      setLoading(true);
      const res = await api.getResumeProfile();
      setProfile(res.data);
    } catch (e: any) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  async function loadGithubProfile() {
    try {
      const res = await api.getGithubProfile();
      if (res.data && res.data.processing_status === 'completed') {
        setGithubData({
          status: 'completed',
          username: res.data.username,
          profile_url: res.data.profile_url,
          avatar_url: res.data.avatar_url,
          public_repositories: res.data.public_repositories,
          followers: res.data.followers,
          following: res.data.following,
          repositories_analyzed: res.data.repositories_analyzed,
          cached: true,
        });
      } else if (res.data) {
        setGithubData({
          status: res.data.processing_status,
          username: res.data.username,
        });
      }
    } catch (e: any) {
      console.error('Failed to load GitHub profile:', e);
    }
  }

  async function handleGithubAnalyze() {
    setGithubLoading(true);
    setGithubError(null);
    try {
      const res = await api.analyzeGithub(false);
      if (res.data.status === 'completed') {
        setGithubData({
          status: 'completed',
          username: res.data.username,
          profile_url: res.data.profile_url,
          avatar_url: res.data.avatar_url,
          public_repositories: res.data.public_repositories,
          followers: res.data.followers,
          following: res.data.following,
          repositories_analyzed: res.data.repositories_analyzed,
          all_technologies: res.data.all_technologies,
          repositories: res.data.repositories,
          cached: res.data.cached,
        });
      } else {
        setGithubData({
          status: res.data.status,
          message: res.data.message,
        });
      }
    } catch (e: any) {
      setGithubError(e?.message || 'Failed to analyze GitHub profile.');
    } finally {
      setGithubLoading(false);
    }
  }

  async function loadSkillEvidence() {
    try {
      const res = await api.getSkillEvidence();
      if (res.data && res.data.analysis_status === 'completed') {
        setSkillEvidenceData({
          evidence: res.data.evidence || [],
          total_skills: res.data.total_skills,
          high_confidence: res.data.high_confidence,
          medium_confidence: res.data.medium_confidence,
          low_confidence: res.data.low_confidence,
          minimal_confidence: res.data.minimal_confidence,
          average_confidence: res.data.average_confidence,
          analysis_status: 'completed',
        });
      } else if (res.data) {
        setSkillEvidenceData({
          evidence: [],
          total_skills: 0,
          high_confidence: 0,
          medium_confidence: 0,
          low_confidence: 0,
          minimal_confidence: 0,
          average_confidence: 0,
          analysis_status: res.data.analysis_status || 'pending',
        });
      }
    } catch (e: any) {
      console.error('Failed to load skill evidence:', e);
    }
  }

  async function handleSkillEvidenceAnalyze() {
    setSkillEvidenceLoading(true);
    setSkillEvidenceError(null);
    try {
      const res = await api.analyzeSkillEvidence(false);
      if (res.data.status === 'completed') {
        const evRes = await api.getSkillEvidence();
        if (evRes.data && evRes.data.analysis_status === 'completed') {
          setSkillEvidenceData({
            evidence: evRes.data.evidence || [],
            total_skills: evRes.data.total_skills,
            high_confidence: evRes.data.high_confidence,
            medium_confidence: evRes.data.medium_confidence,
            low_confidence: evRes.data.low_confidence,
            minimal_confidence: evRes.data.minimal_confidence,
            average_confidence: evRes.data.average_confidence,
            analysis_status: 'completed',
          });
        }
      } else {
        setSkillEvidenceError(res.data.message || 'Skill evidence analysis failed.');
      }
    } catch (e: any) {
      setSkillEvidenceError(e?.message || 'Failed to analyze skill evidence.');
    } finally {
      setSkillEvidenceLoading(false);
    }
  }

  const handleUpload = useCallback(async (file: File) => {
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext !== 'pdf' && ext !== 'docx') {
      setError('Only PDF and DOCX files are supported.');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setError('File must be under 5MB.');
      return;
    }

    setError(null);
    setUploading(true);
    setProcessing(true);

    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await api.analyzeResumeProfile(formData);

      setProfile({
        id: res.data.id,
        status: 'completed',
        profile: res.data.profile,
        urls: res.data.urls,
        metadata: res.data.metadata,
        error: null,
        created_at: null,
      });
    } catch (e: any) {
      setError(e?.message || 'Failed to analyze resume. Please try again.');
    } finally {
      setUploading(false);
      setProcessing(false);
    }
  }, []);

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  }

  function onFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) handleUpload(file);
    if (fileRef.current) fileRef.current.value = '';
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto animate-fade-in">
        <div className="skeleton h-8 w-48 mb-6" />
        <div className="skeleton h-64 w-full rounded-xl" />
      </div>
    );
  }

  const hasProfile = profile?.status === 'completed' && profile?.profile;
  const statusInfo = profile ? STATUS_LABELS[profile.status] : null;

  return (
    <div className="max-w-4xl mx-auto animate-fade-in space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-page-title">Resume Intelligence</h1>
          <p className="text-sm text-zinc-500 mt-1">
            Upload your resume to extract and structure your professional profile.
          </p>
        </div>
        {statusInfo && (
          <span className={statusInfo.cls}>{statusInfo.label}</span>
        )}
      </div>

      {/* Upload area */}
      <div
        onDrop={onDrop}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onClick={() => fileRef.current?.click()}
        className={`surface border-2 border-dashed p-10 text-center cursor-pointer transition-all ${
          dragOver
            ? 'border-blue-500/50 bg-blue-500/5'
            : 'border-white/[0.08] hover:border-white/[0.15]'
        } ${processing ? 'pointer-events-none opacity-60' : ''}`}
      >
        <input ref={fileRef} type="file" accept=".pdf,.docx" onChange={onFileChange} className="hidden" />
        {processing ? (
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
            <div className="text-sm text-zinc-400">Processing your resume...</div>
            <div className="text-xs text-zinc-600">Extracting text and analyzing with AI</div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center">
              <Upload className="w-6 h-6 text-blue-400" />
            </div>
            <div>
              <div className="text-sm font-medium text-[#fafafa]">
                Drop your resume here or click to browse
              </div>
              <div className="text-xs text-zinc-500 mt-1">
                Supports PDF and DOCX files up to 5MB
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/10 border border-red-500/20">
          <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
          <span className="text-sm text-red-400">{error}</span>
        </div>
      )}

      {/* Info banner */}
      {hasProfile && (
        <div className="flex items-start gap-2 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
          <Info className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
          <div className="text-xs text-blue-400 leading-relaxed">
            These are resume-extracted claims. CyberPath will verify and enrich them with evidence in the next analysis phase.
          </div>
        </div>
      )}

      {/* Profile display */}
      {hasProfile && (
        <div className="space-y-4">
          {/* Metadata */}
          {profile.metadata && (
            <div className="surface p-4">
              <div className="flex items-center gap-4 flex-wrap">
                {profile.metadata.file_type && (
                  <div className="flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-zinc-500" />
                    <span className="text-xs text-zinc-400 uppercase">{profile.metadata.file_type}</span>
                  </div>
                )}
                {profile.metadata.character_count > 0 && (
                  <span className="text-xs text-zinc-500">
                    {profile.metadata.character_count.toLocaleString()} characters extracted
                  </span>
                )}
                {profile.metadata.page_count && (
                  <span className="text-xs text-zinc-500">
                    {profile.metadata.page_count} pages
                  </span>
                )}
              </div>
            </div>
          )}

          <ProfileOverview profile={profile.profile} />
          <SkillsSection skills={profile.profile?.skills || []} />
          <ProjectsSection projects={profile.profile?.projects || []} />
          <CertificationsSection certs={profile.profile?.certifications || []} />
          <DetectedLinks urls={profile.urls} />
          <GitHubEvidenceSection
            githubData={githubData}
            analyzing={githubLoading}
            onAnalyze={handleGithubAnalyze}
            error={githubError}
          />
          <SkillEvidenceSection
            evidenceData={skillEvidenceData}
            analyzing={skillEvidenceLoading}
            onAnalyze={handleSkillEvidenceAnalyze}
            error={skillEvidenceError}
          />
        </div>
      )}

      {/* Empty state */}
      {!hasProfile && !processing && !error && (
        <div className="text-center py-12">
          <FileText className="w-12 h-12 text-zinc-700 mx-auto mb-3" />
          <div className="text-sm text-zinc-500">No resume analyzed yet</div>
          <div className="text-xs text-zinc-600 mt-1">Upload a PDF or DOCX file to get started</div>
        </div>
      )}
    </div>
  );
}
