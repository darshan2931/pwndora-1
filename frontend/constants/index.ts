export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

export const SUPPORTED_CAREERS = [
  { id: "soc_analyst", title: "SOC Analyst" },
  { id: "penetration_tester", title: "Penetration Tester" },
  { id: "cloud_security_engineer", title: "Cloud Security Engineer" },
  { id: "appsec_engineer", title: "Application Security Engineer" },
  { id: "threat_intel_analyst", title: "Threat Intelligence Analyst" },
  { id: "forensics_analyst", title: "Digital Forensics Analyst" },
] as const

export const DIFFICULTY_COLORS = {
  beginner: "bg-green-100 text-green-800",
  intermediate: "bg-yellow-100 text-yellow-800",
  advanced: "bg-red-100 text-red-800",
} as const

export const READINESS_THRESHOLDS = {
  low: 40,
  medium: 70,
} as const
