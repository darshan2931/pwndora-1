export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const SUPPORTED_CAREERS = [
  { id: 'soc_analyst', title: 'SOC Analyst', icon: '🔍', color: 'blue' },
  { id: 'penetration_tester', title: 'Penetration Tester', icon: '🔓', color: 'red' },
  { id: 'cloud_security_engineer', title: 'Cloud Security Engineer', icon: '☁️', color: 'purple' },
  { id: 'appsec_engineer', title: 'Application Security Engineer', icon: '🛡️', color: 'green' },
  { id: 'threat_intel_analyst', title: 'Threat Intelligence Analyst', icon: '🕵️', color: 'yellow' },
  { id: 'forensics_analyst', title: 'Digital Forensics Analyst', icon: '🔬', color: 'orange' },
] as const;

export const DIFFICULTY_COLORS: Record<string, string> = {
  beginner: 'bg-green-100 text-green-700',
  easy: 'bg-green-100 text-green-700',
  intermediate: 'bg-yellow-100 text-yellow-700',
  medium: 'bg-yellow-100 text-yellow-700',
  advanced: 'bg-red-100 text-red-700',
  hard: 'bg-red-100 text-red-700',
};

export const READINESS_THRESHOLDS = {
  low: 40,
  medium: 70,
} as const;

export const READINESS_LABELS = {
  low: { text: 'Needs Improvement', color: 'text-error', bg: 'bg-red-500' },
  medium: { text: 'On Track', color: 'text-warning', bg: 'bg-yellow-500' },
  high: { text: 'Strong Foundation', color: 'text-accent', bg: 'bg-accent' },
} as const;

export const MENTOR_SUGGESTED_QUESTIONS = [
  'What certifications should I get for SOC Analyst?',
  'How do I transition from IT to cybersecurity?',
  'What projects should I build for my portfolio?',
  'How long does it take to become a penetration tester?',
  'What are the most in-demand cybersecurity skills?',
  'Can you explain the difference between blue team and red team?',
] as const;
