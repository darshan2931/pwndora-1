import { describe, it, expect } from 'vitest';
import type {
  Skill,
  Career,
  AssessmentData,
  RoadmapStep,
  Project,
  MentorMessage,
} from '@/types';

describe('Types', () => {
  it('Skill type works with valid data', () => {
    const skill: Skill = {
      name: 'Linux',
      category: 'Operating Systems',
      difficulty: 'beginner',
      prerequisites: [],
      estimated_hours: 20,
    };
    expect(skill.name).toBe('Linux');
    expect(skill.difficulty).toBe('beginner');
  });

  it('Career type works with valid data', () => {
    const career: Career = {
      id: 'soc_analyst',
      title: 'SOC Analyst',
      required_skills: ['SIEM', 'Linux'],
    };
    expect(career.id).toBe('soc_analyst');
  });

  it('AssessmentData type works with valid data', () => {
    const data: AssessmentData = {
      career_goal: 'SOC Analyst',
      career_readiness: 65,
      matched_skills: ['Linux', 'Python'],
      missing_skills: ['SIEM'],
      roadmap: [],
      estimated_weeks: 24,
    };
    expect(data.career_readiness).toBe(65);
    expect(data.matched_skills).toHaveLength(2);
  });

  it('RoadmapStep type works', () => {
    const step: RoadmapStep = {
      step: 1,
      skill: 'Linux',
      category: 'OS',
      estimated_hours: 20,
      prerequisites: [],
    };
    expect(step.step).toBe(1);
  });

  it('MentorMessage type works', () => {
    const msg: MentorMessage = {
      role: 'user',
      content: 'What skills do I need?',
    };
    expect(msg.role).toBe('user');
  });
});
