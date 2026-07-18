"""Curated free learning resources for cybersecurity skills."""

FREE_RESOURCES = {
    "Linux": [
        {"name": "Linux Journey", "url": "https://linuxjourney.com/", "type": "course"},
        {"name": "The Linux Command Line (free book)", "url": "https://linuxcommand.org/tlcl.php", "type": "book"},
        {"name": "OverTheWire: Bandit", "url": "https://overthewire.org/wargames/bandit/", "type": "hands-on"},
        {"name": "Linux Upskill Challenge", "url": "https://linuxupskillchallenge.org/", "type": "course"},
    ],
    "Windows": [
        {"name": "Microsoft Learn: Windows", "url": "https://learn.microsoft.com/en-us/windows/", "type": "course"},
        {"name": "PowerShell for Beginners", "url": "https://learn.microsoft.com/en-us/powershell/scripting/learn/ps101/00-introduction", "type": "course"},
        {"name": "TryHackMe: Windows Fundamentals", "url": "https://tryhackme.com/room/windowsfundamentals1xbx", "type": "hands-on"},
    ],
    "Bash": [
        {"name": "OverTheWire: Bandit", "url": "https://overthewire.org/wargames/bandit/", "type": "hands-on"},
        {"name": "Bash Scripting Tutorial", "url": "https://ryanstutorials.net/bash-scripting-tutorial/", "type": "course"},
        {"name": "Explainshell", "url": "https://explainshell.com/", "type": "tool"},
    ],
    "PowerShell": [
        {"name": "Microsoft Learn: PowerShell", "url": "https://learn.microsoft.com/en-us/powershell/scripting/overview", "type": "course"},
        {"name": "PSKoans (learn by doing)", "url": "https://github.com/vexx32/PSKoans", "type": "hands-on"},
    ],
    "TCP/IP": [
        {"name": "Cisco Skills for All", "url": "https://skillsforall.com/", "type": "course"},
        {"name": "Computer Networking (free Stanford course)", "url": "https://www.youtube.com/playlist?list=PLoROMvodv4rN6U3MvKXmRraXNst5KlKQR", "type": "course"},
        {"name": "How the Internet Works", "url": "https://www.inetsolutions.org/how-the-internet-works-a-visual-overview/", "type": "article"},
    ],
    "DNS": [
        {"name": "Cloudflare Learning Center: DNS", "url": "https://www.cloudflare.com/learning/dns/what-is-dns/", "type": "article"},
        {"name": "TryHackMe: DNS in Detail", "url": "https://tryhackme.com/room/dnsindetail", "type": "hands-on"},
        {"name": "Cisco Skills for All", "url": "https://skillsforall.com/", "type": "course"},
    ],
    "HTTP": [
        {"name": "MDN: HTTP Overview", "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview", "type": "article"},
        {"name": "TryHackMe: HTTP in Detail", "url": "https://tryhackme.com/room/httpindetail", "type": "hands-on"},
        {"name": "HTTP/2 Explained", "url": "https://http2-explained.haxx.se/", "type": "book"},
    ],
    "VPN": [
        {"name": "AWS VPN Documentation", "url": "https://docs.aws.amazon.com/vpn/", "type": "docs"},
        {"name": "OpenVPN Community Guides", "url": "https://openvpn.net/community-resources/", "type": "docs"},
    ],
    "Firewalls": [
        {"name": "pfSense Documentation", "url": "https://docs.netgate.com/pfsense/en/latest/", "type": "docs"},
        {"name": "TryHackMe: Firewalls", "url": "https://tryhackme.com/room/firewalls", "type": "hands-on"},
        {"name": "iptables Tutorial", "url": "https://wiki.archlinux.org/title/iptables", "type": "docs"},
    ],
    "Python": [
        {"name": "Automate the Boring Stuff with Python", "url": "https://automatetheboringstuff.com/", "type": "book"},
        {"name": "Python.org Official Tutorial", "url": "https://docs.python.org/3/tutorial/", "type": "course"},
        {"name": "HackerRank Python", "url": "https://www.hackerrank.com/domains/python", "type": "hands-on"},
        {"name": "CS50P: Intro to Python", "url": "https://cs50.harvard.edu/python/", "type": "course"},
    ],
    "JavaScript": [
        {"name": "MDN Web Docs", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript", "type": "docs"},
        {"name": "JavaScript.info", "url": "https://javascript.info/", "type": "course"},
        {"name": "freeCodeCamp JavaScript", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/", "type": "course"},
    ],
    "Go": [
        {"name": "Go Official Tour", "url": "https://go.dev/tour/", "type": "course"},
        {"name": "Go by Example", "url": "https://gobyexample.com/", "type": "course"},
        {"name": "Exercism Go Track", "url": "https://exercism.org/tracks/go", "type": "hands-on"},
    ],
    "SQL": [
        {"name": "SQLBolt", "url": "https://sqlbolt.com/", "type": "hands-on"},
        {"name": "W3Schools SQL", "url": "https://www.w3schools.com/sql/", "type": "course"},
        {"name": "Mode SQL Tutorial", "url": "https://mode.com/sql-tutorial/", "type": "course"},
    ],
    "Burp Suite": [
        {"name": "PortSwigger Web Security Academy", "url": "https://portswigger.net/web-security", "type": "course"},
        {"name": "Burp Suite Documentation", "url": "https://portswigger.net/burp/documentation", "type": "docs"},
        {"name": "TryHackMe: Burp Suite", "url": "https://tryhackme.com/room/burpsuitebasics", "type": "hands-on"},
    ],
    "OWASP Top 10": [
        {"name": "OWASP Top 10 Official", "url": "https://owasp.org/www-project-top-ten/", "type": "docs"},
        {"name": "PortSwigger: OWASP Top 10", "url": "https://portswigger.net/web-security/owasp-top-10", "type": "course"},
        {"name": "TryHackMe: OWASP Top 10", "url": "https://tryhackme.com/room/owasptop10", "type": "hands-on"},
    ],
    "XSS": [
        {"name": "PortSwigger: XSS", "url": "https://portswigger.net/web-security/cross-site-scripting", "type": "course"},
        {"name": "OWASP XSS Prevention", "url": "https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Scripting_Prevention_Cheat_Sheet.html", "type": "docs"},
        {"name": "TryHackMe: XSS", "url": "https://tryhackme.com/room/xss", "type": "hands-on"},
    ],
    "SQL Injection": [
        {"name": "PortSwigger: SQL Injection", "url": "https://portswigger.net/web-security/sql-injection", "type": "course"},
        {"name": "SQLi Lessons", "url": "http://www.damnsmalllinux.org/putknow/sqlinjection.html", "type": "course"},
        {"name": "TryHackMe: SQL Injection", "url": "https://tryhackme.com/room/sqlilab", "type": "hands-on"},
    ],
    "AWS": [
        {"name": "AWS Skill Builder (free tier)", "url": "https://skillbuilder.aws/", "type": "course"},
        {"name": "AWS Well-Architected Labs", "url": "https://wellarchitectedlabs.com/", "type": "hands-on"},
        {"name": "AWS Documentation", "url": "https://docs.aws.amazon.com/", "type": "docs"},
    ],
    "Azure": [
        {"name": "Microsoft Learn: Azure", "url": "https://learn.microsoft.com/en-us/azure/", "type": "course"},
        {"name": "Azure for Beginners", "url": "https://learn.microsoft.com/en-us/azure/architecture/cloud-adoption/getting-started/azure-quick-start-guide", "type": "course"},
    ],
    "GCP": [
        {"name": "Google Cloud Skills Boost", "url": "https://cloudskillsboost.google/", "type": "course"},
        {"name": "Google Cloud Documentation", "url": "https://cloud.google.com/docs", "type": "docs"},
    ],
    "Docker": [
        {"name": "Docker Official Tutorial", "url": "https://docs.docker.com/get-started/", "type": "course"},
        {"name": "Play with Docker", "url": "https://labs.play-with-docker.com/", "type": "hands-on"},
        {"name": "Docker Curriculum", "url": "https://docker-curriculum.com/", "type": "course"},
    ],
    "Kubernetes": [
        {"name": "Kubernetes Official Tutorials", "url": "https://kubernetes.io/docs/tutorials/", "type": "course"},
        {"name": "Katacoda K8s Scenarios", "url": "https://www.katacoda.com/courses/kubernetes", "type": "hands-on"},
        {"name": "Kubernetes the Hard Way", "url": "https://github.com/kelseyhightower/kubernetes-the-hard-way", "type": "hands-on"},
    ],
    "Terraform": [
        {"name": "HashiCorp Learn: Terraform", "url": "https://developer.hashicorp.com/terraform/tutorials", "type": "course"},
        {"name": "Terraform Best Practices", "url": "https://www.terraform-best-practices.com/", "type": "article"},
    ],
    "SIEM": [
        {"name": "Splunk Free Training", "url": "https://www.splunk.com/en_us/training/free-courses.html", "type": "course"},
        {"name": "TryHackMe: SIEM", "url": "https://tryhackme.com/room/siem", "type": "hands-on"},
        {"name": "Wazuh Documentation", "url": "https://documentation.wazuh.com/", "type": "docs"},
    ],
    "Splunk": [
        {"name": "Splunk Free Training", "url": "https://www.splunk.com/en_us/training/free-courses.html", "type": "course"},
        {"name": "Splunk Fundamentals 1 (free)", "url": "https://education.splunk.com/course/splunk-fundamentals-1", "type": "course"},
        {"name": "TryHackMe: Splunk", "url": "https://tryhackme.com/room/splunk101", "type": "hands-on"},
    ],
    "MITRE ATT&CK": [
        {"name": "MITRE ATT&CK Official", "url": "https://attack.mitre.org/", "type": "docs"},
        {"name": "MITRE ATT&CK Navigator", "url": "https://mitre-attack.github.io/attack-navigator/", "type": "tool"},
        {"name": "TryHackMe: ATT&CK", "url": "https://tryhackme.com/room/mitre", "type": "hands-on"},
    ],
    "Nmap": [
        {"name": "Nmap Official Guide", "url": "https://nmap.org/book/", "type": "book"},
        {"name": "TryHackMe: Nmap", "url": "https://tryhackme.com/room/furthernmap", "type": "hands-on"},
        {"name": "Nmap Interactive Tutorial", "url": "https://hackguru.tech/learning/path/ethical-hacking/nmap-scanning/interactive-tutorial", "type": "hands-on"},
    ],
    "Metasploit": [
        {"name": "Metasploit Unleashed (free)", "url": "https://www.offensive-security.com/metasploit-unleashed/", "type": "course"},
        {"name": "TryHackMe: Metasploit", "url": "https://tryhackme.com/room/metasploitintro", "type": "hands-on"},
        {"name": "Metasploit Documentation", "url": "https://docs.metasploit.com/", "type": "docs"},
    ],
    "Active Directory": [
        {"name": "TryHackMe: Active Directory Basics", "url": "https://tryhackme.com/room/adbasics", "type": "hands-on"},
        {"name": "Hack The Box: Active Directory", "url": "https://academy.hackthebox.com/path/preview/active-directory-essentials", "type": "course"},
        {"name": "AD Security Hardening (Microsoft)", "url": "https://learn.microsoft.com/en-us/windows-server/identity/securing-secure-domain-controllers", "type": "docs"},
    ],
    "Memory Analysis": [
        {"name": "Volatility Documentation", "url": "https://volatility3.readthedocs.io/", "type": "docs"},
        {"name": "DFIR Training: Memory Forensics", "url": "https://www.dfir.training/", "type": "course"},
        {"name": "13Cubed: Volatility", "url": "https://www.youtube.com/playlist?list=PLoROMvodv4rMa2eyW0Liz18sMwhJolCCk", "type": "course"},
    ],
    "Disk Analysis": [
        {"name": "Autopsy Documentation", "url": "https://www.autopsy.com/learning/", "type": "course"},
        {"name": "DFIR Training", "url": "https://www.dfir.training/", "type": "course"},
    ],
    "Log Analysis": [
        {"name": "TryHackMe: Log Analysis", "url": "https://tryhackme.com/room/introtoshells", "type": "hands-on"},
        {"name": "Elastic: Log Analysis", "url": "https://www.elastic.co/guide/en/elastic-stack/current/index.html", "type": "docs"},
    ],
    "Incident Response": [
        {"name": "NIST IR Guide (SP 800-61)", "url": "https://csrc.nist.gov/pubs/sp/800/61/r2/final", "type": "docs"},
        {"name": "SANS DFIR Poster", "url": "https://www.sans.org/white-papers/incident-handlers-handbook/", "type": "article"},
        {"name": "TryHackMe: Incident Response", "url": "https://tryhackme.com/room/dfir", "type": "hands-on"},
    ],
    "Secure Coding": [
        {"name": "OWASP Secure Coding Practices", "url": "https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/", "type": "docs"},
        {"name": "SEI CERT Secure Coding", "url": "https://wiki.sei.cmu.edu/confluence/display/java/SEI+CERT+Oracle+Coding+Standard+for+Java", "type": "docs"},
    ],
    "SAST": [
        {"name": "OWASP SAST Guide", "url": "https://owasp.org/www-project-devsecops-guideline/", "type": "docs"},
        {"name": "SonarQube Community Edition (free)", "url": "https://www.sonarsource.com/products/sonarcloud/", "type": "tool"},
    ],
    "DAST": [
        {"name": "OWASP ZAP Getting Started", "url": "https://www.zaproxy.org/getting-started/", "type": "docs"},
        {"name": "OWASP Testing Guide", "url": "https://owasp.org/www-project-web-security-testing-guide/", "type": "docs"},
    ],
    "CI/CD": [
        {"name": "GitHub Actions Documentation", "url": "https://docs.github.com/en/actions", "type": "docs"},
        {"name": "GitHub Actions Learning Path", "url": "https://skills.github.com/", "type": "course"},
    ],
    "Threat Modeling": [
        {"name": "OWASP Threat Dragon (free tool)", "url": "https://owasp.org/www-project-threat-dragon/", "type": "tool"},
        {"name": "Microsoft Threat Modeling Tool", "url": "https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool", "type": "tool"},
        {"name": "OWASP Threat Modeling Cheat Sheet", "url": "https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html", "type": "docs"},
    ],
    "Privilege Escalation": [
        {"name": "TryHackMe: Linux Privilege Escalation", "url": "https://tryhackme.com/room/linuxprivesc", "type": "hands-on"},
        {"name": "TryHackMe: Windows Privilege Escalation", "url": "https://tryhackme.com/room/winprivesc2", "type": "hands-on"},
        {"name": "GTFOBins", "url": "https://gtfobins.github.io/", "type": "tool"},
        {"name": "LOLBAS", "url": "https://lolbas-project.github.io/", "type": "tool"},
    ],
    "Enumeration": [
        {"name": "TryHackMe: Enumeration", "url": "https://tryhackme.com/room/dvwa", "type": "hands-on"},
        {"name": "HackTricks", "url": "https://book.hacktricks.xyz/", "type": "article"},
    ],
    "Networking": [
        {"name": "Cisco Skills for All", "url": "https://skillsforall.com/", "type": "course"},
        {"name": "TryHackMe: Intro to Networking", "url": "https://tryhackme.com/room/introtonetworking", "type": "hands-on"},
        {"name": "Computer Networking (Stanford)", "url": "https://www.youtube.com/playlist?list=PLoROMvodv4rN6U3MvKXmRraXNst5KlKQR", "type": "course"},
    ],
    "Wireshark": [
        {"name": "Wireshark Official Documentation", "url": "https://www.wireshark.org/docs/", "type": "docs"},
        {"name": "TryHackMe: Wireshark", "url": "https://tryhackme.com/room/wireshark", "type": "hands-on"},
        {"name": "Wireshark Wiki", "url": "https://wiki.wireshark.org/", "type": "docs"},
    ],
    "Cryptography": [
        {"name": "Crypto101 (free book)", "url": "https://www.crypto101.io/", "type": "book"},
        {"name": "CryptoHack", "url": "https://cryptohack.org/", "type": "hands-on"},
        {"name": "Coursera: Cryptography (free audit)", "url": "https://www.coursera.org/learn/crypto", "type": "course"},
    ],
    "Reverse Engineering": [
        {"name": "Reverse Engineering for Beginners (free book)", "url": "https://beginners.re/", "type": "book"},
        {"name": "Ghidra Documentation", "url": "https://ghidra-sre.org/", "type": "docs"},
        {"name": "TryHackMe: Reverse Engineering", "url": "https://tryhackme.com/room/rpmed", "type": "hands-on"},
    ],
    "Vulnerability Management": [
        {"name": "Nessus Essentials (free)", "url": "https://www.tenable.com/products/nessus/nessus-essentials", "type": "tool"},
        {"name": "OpenVAS Documentation", "url": "https://docs.greenbone.net/", "type": "docs"},
        {"name": "NVD (National Vulnerability Database)", "url": "https://nvd.nist.gov/", "type": "tool"},
    ],
    "Compliance Frameworks": [
        {"name": "NIST Cybersecurity Framework", "url": "https://www.nist.gov/cyberframework", "type": "docs"},
        {"name": "ISO 27001 Overview", "url": "https://www.iso.org/iso-27001-information-security.html", "type": "docs"},
        {"name": "NIST SP 800-53 (free)", "url": "https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final", "type": "docs"},
    ],
    "NIST": [
        {"name": "NIST Cybersecurity Framework", "url": "https://www.nist.gov/cyberframework", "type": "docs"},
        {"name": "NIST Publications (free)", "url": "https://csrc.nist.gov/publications", "type": "docs"},
    ],
    "ISO 27001": [
        {"name": "ISO 27001 Overview", "url": "https://www.iso.org/iso-27001-information-security.html", "type": "docs"},
        {"name": "ISMS Implementation Guide", "url": "https://www.iso.org/standard/27001", "type": "docs"},
    ],
    "Risk Assessment": [
        {"name": "NIST Risk Management Framework", "url": "https://csrc.nist.gov/projects/risk-management", "type": "docs"},
        {"name": "ISACA Resources", "url": "https://www.isaca.org/resources", "type": "docs"},
    ],
    "Security Auditing": [
        {"name": "NIST Audit Guide", "url": "https://csrc.nist.gov/publications/detail/sp/800-53a/rev-5/final", "type": "docs"},
        {"name": "ISACA Audit Standards", "url": "https://www.isaca.org/standards", "type": "docs"},
    ],
    "Wireless Security": [
        {"name": "TryHackMe: Wireless Hacking", "url": "https://tryhackme.com/room/wifihacking101", "type": "hands-on"},
        {"name": "Aircrack-ng Documentation", "url": "https://www.aircrack-ng.org/doku.php", "type": "docs"},
    ],
    "EDR": [
        {"name": "TryHackMe: EDR", "url": "https://tryhackme.com/room/sigma", "type": "hands-on"},
        {"name": "Elastic EDR Documentation", "url": "https://www.elastic.co/guide/en/security/current/index.html", "type": "docs"},
    ],
    "IAM": [
        {"name": "AWS IAM Documentation", "url": "https://docs.aws.amazon.com/iam/", "type": "docs"},
        {"name": "Azure AD Documentation", "url": "https://learn.microsoft.com/en-us/azure/active-directory/", "type": "docs"},
    ],
    "OSINT": [
        {"name": "TryHackMe: OSINT", "url": "https://tryhackme.com/room/ohsint", "type": "hands-on"},
        {"name": "OSINT Framework", "url": "https://osintframework.com/", "type": "tool"},
        {"name": "Maltego Case File (free)", "url": "https://www.maltego.com/ce/", "type": "tool"},
    ],
    "Dark Web Research": [
        {"name": "Tor Project", "url": "https://www.torproject.org/", "type": "tool"},
        {"name": "Ahmia (Tor search engine)", "url": "https://ahmia.fi/", "type": "tool"},
    ],
    "YARA": [
        {"name": "YARA Official Documentation", "url": "https://yara.readthedocs.io/", "type": "docs"},
        {"name": "YARA Rules Repository", "url": "https://github.com/Yara-Rules/rules", "type": "tool"},
    ],
    "Timeline Analysis": [
        {"name": "Plaso Documentation", "url": "https://plaso.readthedocs.io/", "type": "docs"},
        {"name": "Timesketch Documentation", "url": "https://timesketch.org/", "type": "docs"},
    ],
    "Malware Analysis": [
        {"name": "Ghidra Documentation", "url": "https://ghidra-sre.org/", "type": "docs"},
        {"name": "Any.Run (free sandbox)", "url": "https://any.run/", "type": "tool"},
        {"name": "TryHackMe: Malware Analysis", "url": "https://tryhackme.com/room/malmalintroductory", "type": "hands-on"},
    ],
    "Network Forensics": [
        {"name": "Wireshark Documentation", "url": "https://www.wireshark.org/docs/", "type": "docs"},
        {"name": "NetworkMiner", "url": "https://www.netresec.com/?page=NetworkMiner", "type": "tool"},
        {"name": "SANS Network Forensics", "url": "https://www.sans.org/white-papers/network-forensics/", "type": "article"},
    ],
}


def get_free_resources(skill_name: str) -> list:
    """Get curated free resources for a skill. Falls back to a general search URL."""
    if skill_name in FREE_RESOURCES:
        return FREE_RESOURCES[skill_name]
    return [
        {
            "name": f"Search free {skill_name} courses",
            "url": f"https://www.google.com/search?q=free+{skill_name.replace(' ', '+')}+course+site:tryhackme.com+OR+site:freecodecamp.org+OR+site:cybrary.it",
            "type": "search",
        }
    ]
