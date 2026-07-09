export interface Skill {
  name: string
  category: string
  difficulty: "beginner" | "intermediate" | "advanced"
}

export interface Career {
  id: string
  title: string
  description: string
}

export interface Assessment {
  career_readiness: number
  matched_skills: Skill[]
  missing_skills: Skill[]
}

export interface RoadmapStep {
  step: number
  skill: string
  category: string
  estimated_hours: number
  prerequisites: string[]
}

export interface Project {
  title: string
  difficulty: string
  skills: string[]
  estimated_time: string
}
