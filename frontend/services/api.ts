import { API_BASE_URL } from "@/constants"
import type { Assessment, Career, Project, RoadmapStep } from "@/types"

export async function analyzeCareer(formData: FormData): Promise<Assessment> {
  const res = await fetch(`${API_BASE_URL}/career/analyze`, {
    method: "POST",
    body: formData,
  })
  if (!res.ok) throw new Error("Analysis failed")
  return res.json()
}

export async function getCareers(): Promise<Career[]> {
  const res = await fetch(`${API_BASE_URL}/careers`)
  return res.json()
}

export async function getProjects(skill?: string): Promise<Project[]> {
  const params = skill ? `?skill=${skill}` : ""
  const res = await fetch(`${API_BASE_URL}/projects${params}`)
  return res.json()
}
