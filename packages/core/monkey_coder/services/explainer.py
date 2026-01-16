"""
Code explanation service using AI models
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel


class ExplainConfig(BaseModel):
    """Configuration for code explanation"""
    detail_level: str = "medium"  # brief, medium, detailed
    include_examples: bool = True
    language: str = "python"


class CodeExplainer:
    """Explains what code does in natural language"""
    
    def __init__(self, config: Optional[ExplainConfig] = None):
        self.config = config or ExplainConfig()
    
    async def explain(
        self,
        code: str,
        language: str = "python",
        detail_level: str = "medium"
    ) -> Dict[str, Any]:
        """Explain what code does in natural language.
        
        Args:
            code: Source code to explain
            language: Programming language
            detail_level: Level of detail (brief, medium, detailed)
            
        Returns:
            Dictionary with explanation and metadata
        """
        # TODO: Implement actual explanation using AI model
        # For now, return a structured placeholder
        explanation = self._generate_explanation(code, language, detail_level)
        
        return {
            "code": code,
            "explanation": explanation,
            "language": language,
            "detail_level": detail_level,
            "components": self._extract_components(code, language),
            "complexity": self._assess_complexity(code)
        }
    
    def _generate_explanation(self, code: str, language: str, detail_level: str) -> str:
        """Generate explanation text"""
        # This is a placeholder - in production, this would use an AI model
        lines = code.strip().split('\n')
        
        if detail_level == "brief":
            return f"This {language} code snippet contains {len(lines)} lines of code."
        
        elif detail_level == "medium":
            explanation = f"This {language} code snippet contains {len(lines)} lines. "
            
            # Simple heuristic analysis
            if "def " in code or "function " in code:
                explanation += "It defines one or more functions. "
            if "class " in code:
                explanation += "It defines one or more classes. "
            if "import " in code or "from " in code:
                explanation += "It imports external dependencies. "
            
            return explanation
        
        else:  # detailed
            explanation = f"Detailed explanation of {language} code:\n\n"
            explanation += f"Total lines: {len(lines)}\n"
            explanation += f"Code structure: TODO - implement detailed analysis\n"
            return explanation
    
    def _extract_components(self, code: str, language: str) -> Dict[str, Any]:
        """Extract code components (functions, classes, etc.)"""
        components = {
            "functions": [],
            "classes": [],
            "imports": []
        }
        
        # Simple extraction for Python
        if language == "python":
            for line in code.split('\n'):
                line = line.strip()
                if line.startswith("def "):
                    func_name = line[4:].split('(')[0].strip()
                    components["functions"].append(func_name)
                elif line.startswith("class "):
                    class_name = line[6:].split(':')[0].split('(')[0].strip()
                    components["classes"].append(class_name)
                elif line.startswith("import ") or line.startswith("from "):
                    components["imports"].append(line)
        
        return components
    
    def _assess_complexity(self, code: str) -> str:
        """Assess code complexity"""
        lines = len(code.strip().split('\n'))
        
        if lines < 10:
            return "low"
        elif lines < 50:
            return "medium"
        else:
            return "high"
