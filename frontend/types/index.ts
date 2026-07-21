// ─── Core Entities ────────────────────────────────────────────────────────────

export interface Skill {
  id: string;
  name: string;
  category: string;
  confirmed: boolean;
  level: 'beginner' | 'intermediate' | 'advanced';
}

export interface Project {
  id: string;
  title: string;
  description: string;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  estimatedHours: number;
  skills: string[];
  completed: boolean;
  completedAt?: string;
  githubUrl?: string;
}

export interface Certification {
  id: string;
  name: string;
  issuer: string;
  status: 'planned' | 'in-progress' | 'completed';
  completedAt?: string;
  credentialId?: string;
}

export interface Achievement {
  id: string;
  title: string;
  description: string;
  icon: string;
  unlockedAt: string;
  type?: 'streak' | 'skill' | 'project' | 'milestone';
}

// ─── Roadmap ──────────────────────────────────────────────────────────────────

export type RoadmapNodeType = 'skill' | 'project' | 'certification' | 'milestone';
export type RoadmapNodeStatus = 'completed' | 'in-progress' | 'available' | 'locked';

export interface RoadmapNode {
  id: string;
  title: string;
  description: string;
  type: RoadmapNodeType;
  status: RoadmapNodeStatus;
  estimatedHours: number;
  difficulty: 'Beginner' | 'Intermediate' | 'Advanced';
  resources: Resource[];
  skills: string[];
  prerequisites: string[];
  completedAt?: string;
}

export interface Resource {
  id: string;
  title: string;
  type: 'video' | 'article' | 'lab' | 'book' | 'course';
  url: string;
  duration?: string;
  free: boolean;
}

// ─── Profile ──────────────────────────────────────────────────────────────────

export type ExperienceLevel = 'Beginner' | 'Intermediate' | 'Advanced';
export type LearningPreference = 'videos' | 'reading' | 'labs' | 'projects';

export interface CyberProfile {
  id: string;
  name: string;
  email: string;
  avatarInitials: string;
  targetRole: string;
  targetRoleCategory: string;
  experience: ExperienceLevel;
  readiness: number;
  weeklyStudyHours: number;
  learningPreferences: LearningPreference[];
  knownSkills: Skill[];
  missingSkills: Skill[];
  completedSkills: string[];
  projects: Project[];
  certifications: Certification[];
  achievements: Achievement[];
  totalStudyHours: number;
  currentStreak: number;
  longestStreak: number;
  joinedAt: string;
  lastActive: string;
  roadmapProgress: number;
}

// ─── Mentor ───────────────────────────────────────────────────────────────────

export interface MentorMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface MentorContext {
  todayMission: RoadmapNode | null;
  nextMilestone: RoadmapNode | null;
  lastCompleted: RoadmapNode | null;
  recentAchievement: Achievement | null;
  currentStreak: number;
  weeklyProgress: number;
  estimatedTimeToReady: string;
}

// ─── Dashboard ────────────────────────────────────────────────────────────────

export interface WeeklyProgress {
  day: string;
  hours: number;
  goal: number;
}

export interface DailyMission {
  node: RoadmapNode;
  estimatedMinutes: number;
  priority: 'high' | 'medium' | 'low';
}

// ─── Assessment ───────────────────────────────────────────────────────────────

export interface AssessmentResult {
  detectedSkills: Skill[];
  missingSkills: Skill[];
  detectedProjects: Project[];
  detectedCertifications: Certification[];
  careerMatch: number;
  readinessScore: number;
  estimatedWeeks: number;
  strengths: string[];
  gaps: string[];
}

// ─── GitHub Evidence ──────────────────────────────────────────────────────────

export interface GitHubProfile {
  username: string;
  profile_url: string;
  avatar_url: string | null;
  public_repositories: number;
  followers: number;
  following: number;
  account_created_at: string | null;
  fetched_at: string | null;
}

export interface GitHubRepoMetadata {
  name: string;
  full_name: string;
  description: string;
  html_url: string;
  stars: number;
  forks: number;
  topics: string[];
  languages: Record<string, number>;
  has_readme: boolean;
  selection_reasons: string[];
}

export interface GitHubRepoAIAnalysis {
  project_purpose: string | null;
  technical_domains: string[];
  demonstrated_technologies: { name: string; evidence: string }[];
  cybersecurity_relevance: {
    is_relevant: boolean;
    areas: string[];
    evidence: string | null;
  };
  complexity: string | null;
  observable_evidence: string[];
}

export interface GitHubRepoEvidence {
  name: string;
  full_name: string;
  description: string;
  html_url: string;
  stars: number;
  forks: number;
  topics: string[];
  languages: Record<string, number>;
  has_readme: boolean;
  selection_reasons: string[];
  ai_analysis: GitHubRepoAIAnalysis | null;
}

export interface GitHubTechEvidence {
  technology: string;
  source: string;
  evidence_type: string;
  repository: string;
  details: Record<string, any>;
}

export interface GitHubAnalysisData {
  status: string;
  username?: string;
  profile_url?: string;
  avatar_url?: string | null;
  public_repositories?: number;
  followers?: number;
  following?: number;
  repositories_analyzed?: number;
  all_technologies?: GitHubTechEvidence[];
  repositories?: GitHubRepoEvidence[];
  message?: string;
  cached?: boolean;
}

// ─── Skill Evidence ───────────────────────────────────────────────────────────

export interface SkillEvidenceSource {
  source: string;
  raw_confidence: number;
  effective_confidence: number;
  weight: number;
  contribution: number;
  repository?: string | null;
  evidence_text?: string | null;
  details: Record<string, any>;
}

export interface SkillEvidenceItem {
  skill_id: string;
  skill_name: string;
  category: string;
  confidence: number;
  confidence_level: 'high' | 'medium' | 'low' | 'minimal';
  sources: SkillEvidenceSource[];
  evidence_count: number;
  strongest_source?: string | null;
  last_updated?: string | null;
}

export interface SkillEvidenceSummary {
  total_skills: number;
  high_confidence: number;
  medium_confidence: number;
  low_confidence: number;
  minimal_confidence: number;
  skills: SkillEvidenceItem[];
}

export interface SkillEvidenceAnalysisData {
  status: string;
  total_skills?: number;
  high_confidence?: number;
  medium_confidence?: number;
  low_confidence?: number;
  minimal_confidence?: number;
  average_confidence?: number;
  analyzed_at?: string | null;
  cached?: boolean;
  message?: string;
}

export interface SkillEvidenceListData {
  evidence: SkillEvidenceItem[];
  total_skills: number;
  high_confidence: number;
  medium_confidence: number;
  low_confidence: number;
  minimal_confidence: number;
  average_confidence: number;
  analysis_status: string;
}

// ─── Role Gap Analysis ────────────────────────────────────────────────────────

export interface RoleListItem {
  role_id: string;
  role_name: string;
  description: string;
  required_skills_count: number;
  optional_skills_count: number;
  recommended_certifications: string[];
  estimated_duration?: string | null;
}

export interface RoleDetail {
  role_id: string;
  role_name: string;
  description: string;
  required_skills: RoleSkillConfig[];
  optional_skills: RoleSkillConfig[];
  recommended_certifications: string[];
  suggested_projects: string[];
  estimated_duration?: string | null;
}

export interface RoleSkillConfig {
  skill_name: string;
  importance: 'required' | 'critical' | 'important' | 'beneficial';
  importance_score: number;
  minimum_confidence: number;
  is_required: boolean;
}

export type GapStatus = 'covered' | 'minimal' | 'partial' | 'critical' | 'missing';
export type SkillImportance = 'required' | 'critical' | 'important' | 'beneficial';
export type PriorityLevel = 'highest' | 'high' | 'medium' | 'low';

export interface SkillGap {
  skill_id: string;
  skill_name: string;
  category: string;
  confidence: number;
  minimum_confidence: number;
  gap_size: number;
  gap_status: GapStatus;
  importance: SkillImportance;
  importance_score: number;
  is_required: boolean;
  has_prerequisites: boolean;
  blocked_by: string[];
  unblocked_skills: string[];
  priority_score: number;
  priority_level: PriorityLevel;
  evidence_sources: Record<string, any>[];
  recommendation_reason: string;
}

export interface NextSkillRecommendation {
  skill_id: string;
  skill_name: string;
  category: string;
  confidence: number;
  gap_size: number;
  importance: SkillImportance;
  priority_score: number;
  estimated_hours?: number | null;
  prerequisites_met: boolean;
  blockers: string[];
  recommendation_reason: string;
  learning_resources: Record<string, any>[];
}

export interface RoleGapAnalysisData {
  role_id: string;
  role_name: string;
  role_description: string;
  readiness_score: number;
  readiness_level: 'excellent' | 'good' | 'developing' | 'beginning' | 'not_started';
  total_skills: number;
  covered_count: number;
  partial_count: number;
  missing_count: number;
  skill_gaps: SkillGap[];
  priority_breakdown: {
    highest: SkillGap[];
    high: SkillGap[];
    medium: SkillGap[];
    low: SkillGap[];
  };
  recommended_next_skill?: NextSkillRecommendation | null;
  learning_path: Record<string, any>[];
  ai_explanation?: string | null;
  analyzed_at?: string | null;
}
