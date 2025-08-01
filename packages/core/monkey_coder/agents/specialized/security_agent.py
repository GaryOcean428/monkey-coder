"""
Security Agent - Specialized in security analysis and vulnerability detection
Focuses on application security, infrastructure security, compliance, and threat analysis
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base_agent import BaseAgent, AgentCapability, AgentContext

logger = logging.getLogger(__name__)


class SecurityAgent(BaseAgent):
    """
    Specialized agent for security analysis and vulnerability detection
    Expertise in application security, infrastructure security, compliance
    """
    
    def __init__(self):
        super().__init__(
            name="SecuritySpecialist",
            capabilities={
                AgentCapability.SECURITY_ANALYSIS,
                AgentCapability.CODE_REVIEW,
                AgentCapability.ARCHITECTURE_DESIGN,
                AgentCapability.TESTING,
                AgentCapability.CODE_GENERATION,
            }
        )
        self.specialization = "security"
        self.preferred_model = "gpt-4.1"  # Use flagship model for complex security analysis
        
    async def _setup(self):
        """Initialize security-specific resources"""
        logger.info("Setting up Security Specialist Agent")
        
        # Security frameworks and standards
        self.update_memory("security_frameworks", {
            "owasp": {
                "top_10": ["injection", "broken_auth", "sensitive_data", "xxe", "broken_access", 
                          "security_misconfig", "xss", "insecure_deserial", "known_vulns", "logging"],
                "asvs": ["architecture", "authentication", "session", "access_control", "validation"],
                "samm": ["governance", "design", "implementation", "verification", "operations"]
            },
            "nist": {
                "cybersecurity_framework": ["identify", "protect", "detect", "respond", "recover"],
                "sp_800_53": ["access_control", "audit", "configuration", "identification"],
                "sp_800_63": ["digital_identity", "authentication", "federation"]
            },
            "iso_27001": {
                "domains": ["security_policy", "organization", "hr_security", "asset_mgmt",
                           "access_control", "cryptography", "physical_security", "operations"],
                "controls": ["preventive", "detective", "corrective", "compensating"]
            },
            "pci_dss": {
                "requirements": ["firewall", "default_passwords", "cardholder_data", "encryption",
                               "antivirus", "secure_systems", "access_control", "unique_ids",
                               "physical_access", "monitoring", "testing", "policy"]
            }
        }, memory_type="long_term")
        
        # Security testing methodologies
        self.update_memory("security_testing", {
            "sast": {
                "tools": ["sonarqube", "checkmarx", "veracode", "fortify", "semgrep"],
                "languages": ["java", "csharp", "python", "javascript", "go", "rust"],
                "vulnerabilities": ["sql_injection", "xss", "path_traversal", "hardcoded_secrets"]
            },
            "dast": {
                "tools": ["owasp_zap", "burp_suite", "nessus", "qualys", "rapid7"],
                "techniques": ["crawling", "fuzzing", "injection", "authentication_bypass"],
                "scope": ["web_apps", "apis", "mobile_apps", "web_services"]
            },
            "iast": {
                "tools": ["contrast", "hdiv", "checkmarx_iast"],
                "benefits": ["real_time", "accurate", "dev_integration"],
                "coverage": ["runtime_analysis", "data_flow", "control_flow"]
            },
            "penetration_testing": {
                "methodologies": ["owasp_testing_guide", "nist_sp_800_115", "ptes"],
                "phases": ["pre_engagement", "intelligence", "threat_modeling", "vulnerability",
                          "exploitation", "post_exploitation", "reporting"],
                "tools": ["metasploit", "nmap", "wireshark", "john", "hashcat"]
            }
        }, memory_type="long_term")
        
        # Cryptography and secure coding practices
        self.update_memory("cryptography", {
            "symmetric": {
                "algorithms": ["aes", "chacha20", "3des"],
                "modes": ["gcm", "cbc", "ctr", "ecb"],
                "key_sizes": ["128", "192", "256"]
            },
            "asymmetric": {
                "algorithms": ["rsa", "ecc", "dh", "ecdh"],
                "key_sizes": ["2048", "3072", "4096", "p256", "p384", "p521"],
                "use_cases": ["key_exchange", "digital_signatures", "encryption"]
            },
            "hashing": {
                "algorithms": ["sha256", "sha384", "sha512", "blake2", "sha3"],
                "password_hashing": ["bcrypt", "scrypt", "argon2", "pbkdf2"],
                "hmac": ["sha256", "sha384", "sha512"]
            },
            "protocols": {
                "tls": ["1.2", "1.3", "cipher_suites", "certificate_validation"],
                "oauth": ["2.0", "pkce", "jwt", "scopes", "refresh_tokens"],
                "saml": ["2.0", "assertions", "sso", "federation"]
            }
        }, memory_type="long_term")
        
        # Infrastructure security patterns
        self.update_memory("infrastructure_security", {
            "network_security": {
                "firewalls": ["stateful", "next_gen", "web_app_firewall", "network_segmentation"],
                "ids_ips": ["signature_based", "anomaly_based", "hybrid", "network_behavior"],
                "vpn": ["ipsec", "ssl_vpn", "wireguard", "zero_trust"]
            },
            "cloud_security": {
                "aws": ["iam", "vpc", "security_groups", "cloudtrail", "config", "guardduty"],
                "azure": ["aad", "network_security", "security_center", "sentinel"],
                "gcp": ["iam", "vpc", "security_command_center", "cloud_armor"],
                "shared_responsibility": ["cloud_provider", "customer", "compliance"]
            },
            "container_security": {
                "image_security": ["base_images", "vulnerability_scanning", "signing"],
                "runtime_security": ["admission_controllers", "pod_security", "network_policies"],
                "tools": ["falco", "twistlock", "aqua", "sysdig", "trivy"]
            },
            "secrets_management": {
                "tools": ["hashicorp_vault", "aws_secrets", "azure_keyvault", "k8s_secrets"],
                "practices": ["rotation", "least_privilege", "encryption", "audit"]
            }
        }, memory_type="long_term")
        
        # Compliance and governance
        self.update_memory("compliance", {
            "regulations": {
                "gdpr": ["data_protection", "privacy", "consent", "breach_notification"],
                "hipaa": ["healthcare", "phi", "administrative", "physical", "technical"],
                "sox": ["financial_reporting", "internal_controls", "audit_trails"],
                "ccpa": ["california", "consumer_privacy", "data_rights"]
            },
            "industry_standards": {
                "pci_dss": ["payment_card", "cardholder_data", "network_security"],
                "fedramp": ["federal", "cloud_security", "continuous_monitoring"],
                "iso_27001": ["isms", "risk_management", "continuous_improvement"]
            },
            "frameworks": {
                "cis_controls": ["basic", "foundational", "organizational"],
                "nist_csf": ["identify", "protect", "detect", "respond", "recover"],
                "cobit": ["governance", "management", "processes"]
            }
        }, memory_type="long_term")
        
    async def can_handle_task(self, task_description: str, context: AgentContext) -> float:
        """Determine if this agent can handle the task"""
        security_keywords = [
            "security", "vulnerability", "penetration", "audit", "compliance",
            "authentication", "authorization", "encryption", "cryptography",
            "owasp", "nist", "iso", "pci", "gdpr", "hipaa",
            "threat", "risk", "attack", "exploit", "malware",
            "firewall", "ids", "ips", "siem", "soc",
            "secure", "hardening", "scanning", "assessment",
            "privacy", "data protection", "breach", "incident",
            "access control", "identity", "federation", "sso",
            "secrets", "certificates", "keys", "tokens"
        ]
        
        task_lower = task_description.lower()
        matches = sum(1 for keyword in security_keywords if keyword in task_lower)
        
        # Higher confidence for security-specific tasks
        base_confidence = min(0.95, matches * 0.15)
        
        # Boost confidence for specific security patterns
        if any(pattern in task_lower for pattern in ["security", "vulnerability", "threat", "audit"]):
            base_confidence += 0.25
            
        if any(standard in task_lower for standard in ["owasp", "nist", "iso", "compliance"]):
            base_confidence += 0.2
            
        return min(1.0, base_confidence)
    
    async def _execute_task(self, task_description: str, context: AgentContext) -> Dict[str, Any]:
        """Execute security analysis task"""
        logger.info(f"Security Agent executing: {task_description}")
        
        # Analyze task type
        task_type = self._determine_task_type(task_description)
        
        # Prepare specialized prompt based on task type
        if task_type == "vulnerability_assessment":
            result = await self._handle_vulnerability_assessment(task_description, context)
        elif task_type == "secure_coding":
            result = await self._handle_secure_coding(task_description, context)
        elif task_type == "architecture_review":
            result = await self._handle_architecture_review(task_description, context)
        elif task_type == "compliance_audit":
            result = await self._handle_compliance_audit(task_description, context)
        elif task_type == "threat_modeling":
            result = await self._handle_threat_modeling(task_description, context)
        elif task_type == "incident_response":
            result = await self._handle_incident_response(task_description, context)
        elif task_type == "cryptography":
            result = await self._handle_cryptography_task(task_description, context)
        else:
            result = await self._handle_general_security_task(task_description, context)
        
        return {
            "type": "security_analysis",
            "task_type": task_type,
            "result": result,
            "specialization": "security",
            "frameworks_applied": self._detect_frameworks(task_description),
            "security_domains": self._identify_security_domains(task_description),
            "risk_level": self._assess_risk_level(task_description)
        }
    
    def _determine_task_type(self, task_description: str) -> str:
        """Determine the specific type of security task"""
        task_lower = task_description.lower()
        
        if any(word in task_lower for word in ["vulnerability", "pentest", "scan", "assessment"]):
            return "vulnerability_assessment"
        elif any(word in task_lower for word in ["secure code", "code review", "sast", "dast"]):
            return "secure_coding"
        elif any(word in task_lower for word in ["architecture", "design", "threat model"]):
            return "architecture_review"
        elif any(word in task_lower for word in ["compliance", "audit", "regulation", "standard"]):
            return "compliance_audit"
        elif any(word in task_lower for word in ["threat", "attack", "model", "risk"]):
            return "threat_modeling"
        elif any(word in task_lower for word in ["incident", "response", "forensics", "breach"]):
            return "incident_response"
        elif any(word in task_lower for word in ["encryption", "cryptography", "certificate", "key"]):
            return "cryptography"
        else:
            return "general"
    
    def _detect_frameworks(self, task_description: str) -> List[str]:
        """Detect security frameworks mentioned in task description"""
        frameworks = []
        task_lower = task_description.lower()
        
        framework_keywords = {
            "owasp": ["owasp"],
            "nist": ["nist"],
            "iso_27001": ["iso 27001", "iso27001"],
            "pci_dss": ["pci", "pci dss"],
            "gdpr": ["gdpr"],
            "hipaa": ["hipaa"],
            "sox": ["sox", "sarbanes"],
            "cis": ["cis controls", "cis"]
        }
        
        for framework, keywords in framework_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                frameworks.append(framework)
        
        return frameworks
    
    def _identify_security_domains(self, task_description: str) -> List[str]:
        """Identify security domains relevant to the task"""
        domains = []
        task_lower = task_description.lower()
        
        domain_keywords = {
            "application_security": ["app", "web", "api", "mobile", "software"],
            "infrastructure_security": ["network", "server", "cloud", "infrastructure"],
            "data_security": ["data", "database", "encryption", "privacy"],
            "identity_security": ["identity", "access", "authentication", "authorization"],
            "operational_security": ["monitoring", "incident", "forensics", "soc"],
            "compliance": ["compliance", "audit", "regulation", "governance"]
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                domains.append(domain)
        
        return domains if domains else ["general_security"]
    
    def _assess_risk_level(self, task_description: str) -> str:
        """Assess the risk level based on task description"""
        task_lower = task_description.lower()
        
        high_risk_keywords = ["critical", "breach", "exploit", "attack", "malware", "ransomware"]
        medium_risk_keywords = ["vulnerability", "weakness", "exposure", "misconfiguration"]
        low_risk_keywords = ["review", "assessment", "audit", "compliance"]
        
        if any(keyword in task_lower for keyword in high_risk_keywords):
            return "high"
        elif any(keyword in task_lower for keyword in medium_risk_keywords):
            return "medium"
        elif any(keyword in task_lower for keyword in low_risk_keywords):
            return "low"
        else:
            return "medium"
    
    async def _handle_vulnerability_assessment(self, task_description: str, context: AgentContext) -> str:
        """Handle vulnerability assessment and penetration testing tasks"""
        prompt = f"""
As a Security Specialist Agent, conduct comprehensive vulnerability assessment for:

{task_description}

Requirements:
1. Perform systematic vulnerability identification using OWASP methodology
2. Conduct static (SAST) and dynamic (DAST) application security testing
3. Analyze infrastructure and network security vulnerabilities
4. Assess configuration security and hardening gaps
5. Identify privilege escalation and lateral movement risks
6. Evaluate data exposure and privacy vulnerabilities
7. Provide risk-based prioritization with CVSS scoring
8. Include actionable remediation recommendations

Context from previous work:
{self._format_context(context)}

Please provide:
1. Comprehensive vulnerability assessment report
2. Risk-based prioritization matrix
3. Technical vulnerability details with proof-of-concept
4. Remediation roadmap with timelines
5. Security testing automation recommendations
6. Compliance gap analysis
7. Security monitoring improvements
8. Executive summary with business impact
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_secure_coding(self, task_description: str, context: AgentContext) -> str:
        """Handle secure coding and code review tasks"""
        prompt = f"""
As a Security Specialist Agent, perform secure code analysis for:

{task_description}

Requirements:
1. Conduct comprehensive OWASP Top 10 vulnerability analysis
2. Review input validation and output encoding practices
3. Analyze authentication and session management security
4. Assess authorization and access control implementation
5. Review cryptographic implementations and key management
6. Evaluate error handling and logging security
7. Analyze third-party dependencies and supply chain risks
8. Provide secure coding guidelines and best practices

Context from previous work:
{self._format_context(context)}

Please provide:
1. Detailed security code review findings
2. OWASP Top 10 compliance analysis
3. Secure coding recommendations
4. Vulnerability remediation code examples
5. Security testing integration guidance
6. Dependency security analysis
7. Security development lifecycle improvements
8. Developer security training recommendations
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_architecture_review(self, task_description: str, context: AgentContext) -> str:
        """Handle security architecture review tasks"""
        prompt = f"""
As a Security Specialist Agent, conduct security architecture review for:

{task_description}

Requirements:
1. Analyze security architecture design patterns and anti-patterns
2. Review defense-in-depth implementation and layered security
3. Assess zero-trust architecture principles and implementation
4. Evaluate security boundaries and trust zones
5. Review data flow security and encryption in transit/at rest
6. Analyze identity and access management architecture
7. Assess threat surface and attack vector analysis
8. Provide security architecture improvement recommendations

Context from previous work:
{self._format_context(context)}

Please provide:
1. Security architecture assessment report
2. Threat modeling and attack surface analysis
3. Security design pattern recommendations
4. Zero-trust implementation roadmap
5. Data security and privacy architecture
6. Identity and access management improvements
7. Security monitoring and incident response architecture
8. Compliance architecture alignment
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_compliance_audit(self, task_description: str, context: AgentContext) -> str:
        """Handle compliance audit and regulatory assessment tasks"""
        frameworks = self._detect_frameworks(task_description)
        compliance_framework = frameworks[0] if frameworks else "iso_27001"
        
        prompt = f"""
As a Security Specialist Agent, conduct compliance audit for {compliance_framework}:

{task_description}

Requirements:
1. Perform comprehensive {compliance_framework} compliance assessment
2. Analyze control implementation and effectiveness
3. Identify compliance gaps and remediation requirements
4. Assess policy and procedure alignment with standards
5. Review documentation and evidence collection
6. Evaluate continuous monitoring and improvement processes
7. Assess risk management and governance frameworks
8. Provide compliance roadmap and remediation plan

Context from previous work:
{self._format_context(context)}

Please provide:
1. Comprehensive compliance assessment report
2. Control implementation gap analysis
3. Remediation roadmap with priorities and timelines
4. Policy and procedure recommendations
5. Evidence collection and documentation requirements
6. Continuous monitoring implementation plan
7. Risk management framework improvements
8. Executive compliance dashboard recommendations
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_threat_modeling(self, task_description: str, context: AgentContext) -> str:
        """Handle threat modeling and risk assessment tasks"""
        prompt = f"""
As a Security Specialist Agent, conduct comprehensive threat modeling for:

{task_description}

Requirements:
1. Apply STRIDE threat modeling methodology
2. Identify assets, threats, vulnerabilities, and attack vectors
3. Analyze threat actors and their capabilities and motivations
4. Assess likelihood and impact using qualitative and quantitative methods
5. Evaluate existing security controls and their effectiveness
6. Identify residual risks and additional security requirements
7. Provide risk-based security control recommendations
8. Design threat intelligence and monitoring requirements

Context from previous work:
{self._format_context(context)}

Please provide:
1. Comprehensive threat model with STRIDE analysis
2. Asset inventory and classification
3. Threat actor analysis and attack scenarios
4. Risk assessment matrix with likelihood and impact
5. Security control gap analysis and recommendations
6. Incident response and monitoring requirements
7. Security awareness and training recommendations
8. Threat intelligence integration plan
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_incident_response(self, task_description: str, context: AgentContext) -> str:
        """Handle incident response and digital forensics tasks"""
        prompt = f"""
As a Security Specialist Agent, design incident response plan for:

{task_description}

Requirements:
1. Develop comprehensive incident response procedures (NIST framework)
2. Design incident classification and escalation procedures
3. Create forensics and evidence collection protocols
4. Establish communication and notification procedures
5. Design containment, eradication, and recovery procedures
6. Develop post-incident analysis and lessons learned processes
7. Create incident response team roles and responsibilities
8. Design incident response testing and tabletop exercises

Context from previous work:
{self._format_context(context)}

Please provide:
1. Complete incident response plan and procedures
2. Incident classification and escalation matrix
3. Digital forensics and evidence handling procedures
4. Communication and stakeholder notification plans
5. Technical containment and recovery procedures
6. Post-incident analysis and improvement processes
7. Incident response team training and exercises
8. Legal and regulatory compliance considerations
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_cryptography_task(self, task_description: str, context: AgentContext) -> str:
        """Handle cryptography and key management tasks"""
        prompt = f"""
As a Security Specialist Agent with cryptography expertise, implement:

{task_description}

Requirements:
1. Design cryptographic architecture with appropriate algorithms
2. Implement secure key generation, distribution, and management
3. Design encryption-in-transit and encryption-at-rest solutions
4. Implement digital signatures and certificate management
5. Design secure authentication and authorization protocols
6. Implement cryptographic key lifecycle management
7. Assess quantum-resistant cryptography requirements
8. Design Hardware Security Module (HSM) integration

Context from previous work:
{self._format_context(context)}

Please provide:
1. Cryptographic architecture design
2. Key management system implementation
3. Encryption implementation with best practices
4. Digital signature and PKI implementation
5. Secure protocol design and implementation
6. Key lifecycle management procedures
7. Quantum-resistant cryptography roadmap
8. HSM integration and hardware security
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_general_security_task(self, task_description: str, context: AgentContext) -> str:
        """Handle general security tasks"""
        prompt = f"""
As a Security Specialist Agent, address this comprehensive security challenge:

{task_description}

Requirements:
1. Apply defense-in-depth security principles
2. Implement risk-based security controls
3. Ensure compliance with relevant security standards
4. Design security monitoring and incident detection
5. Implement security awareness and training programs
6. Design business continuity and disaster recovery
7. Ensure privacy and data protection compliance
8. Provide security governance and risk management

Context from previous work:
{self._format_context(context)}

Please provide a comprehensive security solution addressing all aspects of the challenge with industry best practices and standards compliance.
"""
        
        return await self._generate_response(prompt, context)    
    async def process(self, task: str, context: AgentContext) -> Dict[str, Any]:
        """Process a security analysis task"""
        return await self._execute_task(task, context)
