import logging
from typing import Dict, List, Optional, Tuple

from knowledge.loader import knowledge_loader

logger = logging.getLogger(__name__)

SKILL_ALIASES: Dict[str, str] = {
    "js": "JavaScript",
    "typescript": "JavaScript",
    "ts": "JavaScript",
    "node": "JavaScript",
    "nodejs": "JavaScript",
    "node.js": "JavaScript",
    "py": "Python",
    "python3": "Python",
    "golang": "Go",
    "k8s": "Kubernetes",
    "tf": "Terraform",
    "ad": "Active Directory",
    "active directory services": "Active Directory",
    "ms ad": "Active Directory",
    "siem solutions": "SIEM",
    "siem tools": "SIEM",
    "splunk enterprise": "Splunk",
    "network scanning": "Nmap",
    "port scanning": "Nmap",
    "metasploit framework": "Metasploit",
    "msf": "Metasploit",
    "burp": "Burp Suite",
    "burpsuite": "Burp Suite",
    "burp suite professional": "Burp Suite",
    "wireshark tshark": "Wireshark",
    "network analysis": "Wireshark",
    "aws cloud": "AWS",
    "amazon web services": "AWS",
    "microsoft azure": "Azure",
    "azure cloud": "Azure",
    "google cloud platform": "GCP",
    "google cloud": "GCP",
    "docker containers": "Docker",
    "docker compose": "Docker",
    "kubernetes clusters": "Kubernetes",
    "helm charts": "Kubernetes",
    "terraform iac": "Terraform",
    "infrastructure as code": "Terraform",
    "hashicorp terraform": "Terraform",
    "cicd pipelines": "CI/CD",
    "continuous integration": "CI/CD",
    "github actions": "CI/CD",
    "jenkins pipelines": "CI/CD",
    "owasp": "OWASP Top 10",
    "owasp top ten": "OWASP Top 10",
    "cross-site scripting": "XSS",
    "sql injection attacks": "SQL Injection",
    "sqli": "SQL Injection",
    "incident handling": "Incident Response",
    "ir": "Incident Response",
    "dfir": "Incident Response",
    "log review": "Log Analysis",
    "siem log analysis": "Log Analysis",
    "edr solutions": "EDR",
    "endpoint detection": "EDR",
    "crowdstrike falcon": "EDR",
    "sentinelone": "EDR",
    "vulnerability scanning": "Vulnerability Management",
    "nessus": "Vulnerability Management",
    "openvas": "Vulnerability Management",
    "mitre": "MITRE ATT&CK",
    "attack framework": "MITRE ATT&CK",
    "attack matrix": "MITRE ATT&CK",
    "osint techniques": "OSINT",
    "open source intelligence": "OSINT",
    "maltego": "OSINT",
    "shodan": "OSINT",
    "yara rules": "YARA",
    "yara rule writing": "YARA",
    "secure software development": "Secure Coding",
    "secure development": "Secure Coding",
    "owasp secure coding": "Secure Coding",
    "static application security testing": "SAST",
    "dynamic application security testing": "DAST",
    "owasp zap": "DAST",
    "risk evaluation": "Risk Assessment",
    "risk analysis": "Risk Assessment",
    "compliance": "Compliance Frameworks",
    "regulatory compliance": "Compliance Frameworks",
    "nist framework": "NIST",
    "nist csf": "NIST",
    "nist 800-53": "NIST",
    "iso27001": "ISO 27001",
    "iso/iec 27001": "ISO 27001",
    "information security management": "ISO 27001",
    "security audits": "Security Auditing",
    "audit": "Security Auditing",
    "bcdr": "Business Continuity",
    "business continuity and disaster recovery": "Business Continuity",
    "disaster recovery": "Business Continuity",
    "soc2": "SOC 2",
    "soc 2 compliance": "SOC 2",
    "reverse eng": "Reverse Engineering",
    "reversing": "Reverse Engineering",
    "binary analysis": "Reverse Engineering",
    "ghidra": "Reverse Engineering",
    "ida": "Reverse Engineering",
    "priv esc": "Privilege Escalation",
    "privesc": "Privilege Escalation",
    "privilege escalation techniques": "Privilege Escalation",
    "enum": "Enumeration",
    "service enumeration": "Enumeration",
    "network enumeration": "Enumeration",
    "wifi hacking": "Wireless Security",
    "wifi security": "Wireless Security",
    "aircrack": "Wireless Security",
    "wireless network security": "Wireless Security",
    "mobile app security": "Mobile Security",
    "android security": "Mobile Security",
    "ios security": "Mobile Security",
    "owasp mobile": "Mobile Security",
    "api security testing": "API Security",
    "rest api security": "API Security",
    "graphql security": "API Security",
    "container security scanning": "Container Security",
    "docker security": "Container Security",
    "trivy": "Container Security",
    "falco": "Container Security",
    "secret management": "Secrets Management",
    "vault": "Secrets Management",
    "hashicorp vault": "Secrets Management",
    "security orchestration": "Security Automation",
    "soar": "Security Automation",
    "automated security": "Security Automation",
    "packet capture analysis": "Packet Analysis",
    "pcap analysis": "Packet Analysis",
    "tcpdump": "Packet Analysis",
    "windows forensics": "Disk Analysis",
    "disk forensics": "Disk Analysis",
    "autopsy": "Disk Analysis",
    "ftk": "Disk Analysis",
    "volatility": "Memory Analysis",
    "memory forensics": "Memory Analysis",
    "ram analysis": "Memory Analysis",
    "timeline forensics": "Timeline Analysis",
    "plaso": "Timeline Analysis",
    "timesketch": "Timeline Analysis",
    "network forensics analysis": "Network Forensics",
    "pcap forensics": "Network Forensics",
    "networkminer": "Network Forensics",
    "malware reverse engineering": "Malware Analysis",
    "malware analysis tools": "Malware Analysis",
    "ida pro": "Malware Analysis",
    "dark web": "Dark Web Research",
    "darknet research": "Dark Web Research",
    "tor": "Dark Web Research",
    "dns resolution": "DNS",
    "dns security": "DNS",
    "nslookup": "DNS",
    "dig": "DNS",
    "http protocol": "HTTP",
    "https": "HTTP",
    "http/https": "HTTP",
    "web protocols": "HTTP",
    "tcp": "TCP/IP",
    "ip": "TCP/IP",
    "tcp/ip networking": "TCP/IP",
    "network fundamentals": "TCP/IP",
    "vpn configuration": "VPN",
    "vpn setup": "VPN",
    "openvpn": "VPN",
    "wireguard": "VPN",
    "firewall configuration": "Firewalls",
    "firewall management": "Firewalls",
    "iptables": "Firewalls",
    "pfsense": "Firewalls",
    "network security": "Networking",
    "computer networking": "Networking",
    "bash scripting": "Bash",
    "shell scripting": "Bash",
    "bash shell": "Bash",
    "powershell scripting": "PowerShell",
    "pwsh": "PowerShell",
    "windows powershell": "PowerShell",
    "linux administration": "Linux",
    "linux system administration": "Linux",
    "ubuntu": "Linux",
    "centos": "Linux",
    "debian": "Linux",
    "windows administration": "Windows",
    "windows server": "Windows",
    "microsoft windows": "Windows",
}


class SkillNormalizationService:

    def __init__(self):
        self._canonical_map: Optional[Dict[str, str]] = None
        self._skill_data: Optional[Dict[str, dict]] = None

    def _build_maps(self):
        if self._canonical_map is not None:
            return

        skills = knowledge_loader.get_skills()
        self._skill_data = {}
        self._canonical_map = {}

        for skill in skills:
            name = skill.get("name", "")
            if not name:
                continue
            self._skill_data[name.lower()] = skill
            self._canonical_map[name.lower()] = name

        for alias, canonical in SKILL_ALIASES.items():
            if canonical.lower() in self._canonical_map:
                self._canonical_map[alias.lower()] = self._canonical_map[canonical.lower()]

    def normalize(self, raw_name: str) -> Optional[str]:
        self._build_maps()
        if not raw_name or not raw_name.strip():
            return None

        cleaned = raw_name.strip()
        key = cleaned.lower()

        if key in self._canonical_map:
            return self._canonical_map[key]

        for canonical_key, canonical_name in self._canonical_map.items():
            if key in canonical_key or canonical_key in key:
                return canonical_name

        return None

    def get_skill_data(self, skill_name: str) -> Optional[dict]:
        self._build_maps()
        if not skill_name:
            return None
        return self._skill_data.get(skill_name.lower())

    def get_all_canonical_names(self) -> List[str]:
        self._build_maps()
        return sorted(set(self._canonical_map.values()))

    def batch_normalize(self, names: List[str]) -> Dict[str, Optional[str]]:
        result = {}
        for name in names:
            result[name] = self.normalize(name)
        return result


skill_normalizer = SkillNormalizationService()
