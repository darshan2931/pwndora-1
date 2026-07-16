export interface Skill {
  name: string;
  category: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  prerequisites?: string[];
  estimated_hours?: number;
  related_tools?: string[];
  learning_resources?: string[];
}

export interface Career {
  id: string;
  title: string;
  description?: string;
  required_skills?: string[];
  optional_skills?: string[];
  certifications?: string[];
  projects?: string[];
  estimated_weeks?: number;
}

export interface Assessment {
  success: boolean;
  data: AssessmentData;
}

export interface AssessmentData {
  career_goal: string;
  career_readiness: number;
  matched_skills: string[];
  missing_skills: string[];
  matched_certifications?: string[];
  recommended_projects?: ProjectRecommendation[];
  roadmap?: RoadmapStep[];
  estimated_weeks?: number;
  ai_summary?: string;
  study_hours?: number;
}

export interface RoadmapStep {
  step: number;
  skill: string;
  category: string;
  estimated_hours: number;
  prerequisites: string[];
  resources?: string[];
  projects?: string[];
}

export interface Project {
  id?: string;
  title: string;
  description?: string;
  difficulty: string;
  skills: string[];
  estimated_hours?: number;
  estimated_time?: string;
}

export interface ProjectRecommendation {
  title: string;
  difficulty: string;
  skills: string[];
  estimated_hours: number;
  reason?: string;
}

export interface MentorMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: number;
}

export interface MentorChatResponse {
  success: boolean;
  response: string;
  session_id?: string;
}

export interface CareerAnalysisResponse {
  success: boolean;
  data: AssessmentData;
}

export interface CareersResponse {
  success: boolean;
  data: Career[];
}

export interface ProjectsResponse {
  success: boolean;
  data: Project[];
}

export interface SkillCategory {
  name: string;
  skills: string[];
}

export interface SkillsResponse {
  success: boolean;
  data: {
    categories: SkillCategory[];
  };
}

export interface CertificationsResponse {
  success: boolean;
  data: Certification[];
}

export interface Certification {
  name: string;
  vendor: string;
  difficulty: string;
  recommended_for: string[];
  prerequisites?: string[];
  study_resources?: string[];
}
