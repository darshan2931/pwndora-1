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
  earnedAt: string;
  type: 'streak' | 'skill' | 'project' | 'milestone';
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
