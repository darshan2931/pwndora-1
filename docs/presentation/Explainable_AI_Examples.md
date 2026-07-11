# Explainable AI Examples

## Overview

CyberPath AI provides explainable recommendations — every suggestion includes reasoning.

---

## Example 1: Career Readiness

**User Profile**: Linux, Python, Networking
**Target Role**: SOC Analyst
**Readiness**: 43%

**AI Explanation**:
> Your readiness for SOC Analyst is 43%. You already have a solid foundation with Linux, Python, and Networking — skills that are essential for monitoring and analyzing security events. To reach job readiness, focus on learning SIEM tools (like Splunk or Wazuh), understanding MITRE ATT&CK framework, and building incident response skills. These three areas will close the gap between your current abilities and what employers expect.

---

## Example 2: Roadmap Order

**Missing Skills**: SIEM, MITRE ATT&CK, Incident Response, Log Analysis

**AI Explanation**:
> This roadmap starts with Log Analysis because it builds the foundation for understanding security events. Once you can read and interpret logs, SIEM tools become much easier to learn — they're essentially log analysis at scale. MITRE ATT&CK comes next because it provides the framework for classifying threats you'll see in SIEM. Finally, Incident Response ties everything together by teaching you how to act on the alerts you've learned to detect.

---

## Example 3: Mentor Response

**Question**: "Should I get Security+ or jump straight to BTL1?"

**AI Response**:
> Based on your profile, I recommend starting with CompTIA Security+ first. Here's why:
>
> 1. **Foundation**: Security+ covers fundamental concepts (network security, cryptography, risk management) that BTL1 assumes you already know
> 2. **Industry recognition**: Security+ is more widely recognized by employers, especially for entry-level SOC roles
> 3. **Prerequisite**: BTL1 content builds on Security+ knowledge areas
>
> After Security+, Blue Team Level 1 will feel like a natural next step, focusing specifically on detection, analysis, and response — the hands-on SOC skills you need.

---

## Example 4: Skill Gap Analysis

**User has**: Linux, Python
**Role requires**: Linux, Python, SIEM, Burp Suite, OWASP, Nmap

**AI Explanation**:
> You have 2 of 6 required skills (33%). Your Python and Linux skills are strong foundations. The biggest gap is in security-specific tools: SIEM for defensive monitoring, Nmap for network scanning, and Burp Suite for web application testing. I recommend learning Nmap first — it's the most widely used tool and will help you understand network security concepts that apply to SIEM as well.

---

## Why This Matters

- **Trust**: Users understand why they're being told to learn specific things
- **Motivation**: Clear reasoning helps users stay committed to the roadmap
- **Accountability**: Recommendations are tied to knowledge base data, not random AI suggestions
- **Debugging**: If a recommendation seems wrong, the explanation reveals the reasoning
