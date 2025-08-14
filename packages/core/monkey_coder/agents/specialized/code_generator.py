"""
Code Generator Agent - Specialized in generating high-quality code
Uses quantum execution for exploring multiple implementation approaches
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base_agent import BaseAgent, AgentCapability, AgentContext

logger = logging.getLogger(__name__)


class CodeGeneratorAgent(BaseAgent):
    """
    Specialized agent for code generation tasks
    Explores multiple implementation approaches using quantum execution
    """
    
    def __init__(self, provider_registry=None):
        super().__init__(
            name="CodeGenerator",
            capabilities={
                AgentCapability.CODE_GENERATION,
                AgentCapability.REFACTORING,
                AgentCapability.ARCHITECTURE_DESIGN,
            }
        )
        # Reference to provider registry for actual AI calls
        self.provider_registry = provider_registry
        self.preferred_model = "gpt-5"  # Default to GPT-5 flagship model
        
    async def _setup(self):
        """Initialize agent-specific resources"""
        logger.info("Setting up Code Generator Agent")
        
        # Initialize common patterns and templates
        self.update_memory("common_patterns", {
            "singleton": "Singleton design pattern template",
            "factory": "Factory pattern template",
            "observer": "Observer pattern template",
            "mvc": "Model-View-Controller template",
            "repository": "Repository pattern template",
        }, memory_type="long_term")
        
        # Initialize language-specific templates
        self.update_memory("language_templates", {
            "python": {
                "class": "Python class template",
                "function": "Python function template",
                "async_function": "Python async function template",
                "dataclass": "Python dataclass template",
            },
            "javascript": {
                "class": "JavaScript class template",
                "function": "JavaScript function template",
                "async_function": "JavaScript async function template",
                "react_component": "React component template",
            },
            "typescript": {
                "interface": "TypeScript interface template",
                "type": "TypeScript type template",
                "class": "TypeScript class template",
                "function": "TypeScript function template",
            }
        }, memory_type="long_term")
        
    async def process(self, task: str, context: AgentContext, **kwargs) -> Dict[str, Any]:
        """
        Process code generation task
        
        Args:
            task: Task description
            context: Agent context with files and metadata
            **kwargs: Additional parameters for variation
            
        Returns:
            Generated code and metadata
        """
        start_time = datetime.now()
        
        # Extract parameters
        style = kwargs.get("style", "clean")
        optimize = kwargs.get("optimize", False)
        comprehensive = kwargs.get("comprehensive", False)
        
        # Analyze task requirements
        analysis = await self._analyze_requirements(task, context)
        
        # Select appropriate model based on task complexity
        model_choice = await self._select_model(analysis)
        
        # Use MCP tools if available
        mcp_context = {}
        if "filesystem" in context.mcp_servers and self.mcp_clients.get("filesystem"):
            try:
                # Get project structure for context
                project_files = await self.use_mcp_tool("filesystem", "list_directory", {
                    "path": context.workspace_path or "."
                })
                mcp_context["project_structure"] = project_files
            except Exception as e:
                logger.warning(f"Failed to get project structure via MCP: {e}")
                
        # Generate code based on style and requirements
        if style == "clean":
            code = await self._generate_clean_code(task, analysis, context, mcp_context)
        elif style == "optimized" or optimize:
            code = await self._generate_optimized_code(task, analysis, context, mcp_context)
        elif style == "verbose" or comprehensive:
            code = await self._generate_comprehensive_code(task, analysis, context, mcp_context)
        else:
            code = await self._generate_default_code(task, analysis, context, mcp_context)
            
        # Add documentation if comprehensive
        if comprehensive:
            code["documentation"] = await self._generate_documentation(code["code"], analysis)
            
        # Add tests if requested
        if analysis.get("include_tests", False):
            code["tests"] = await self._generate_tests(code["code"], analysis)
            
        # Update memory with successful patterns
        self._learn_from_generation(task, code, analysis)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "code": code.get("code", ""),
            "language": analysis.get("language", "python"),
            "files": code.get("files", []),
            "documentation": code.get("documentation"),
            "tests": code.get("tests"),
            "confidence": self._calculate_confidence(code, analysis),
            "metadata": {
                "agent": self.name,
                "style": style,
                "model": model_choice,
                "execution_time": execution_time,
                "mcp_tools_used": list(mcp_context.keys()),
                "analysis": analysis,
            }
        }
        
    def get_quantum_variations(self, task: str, context: AgentContext) -> List[Dict[str, Any]]:
        """
        Get quantum variations for code generation
        
        Returns variations exploring different implementation approaches
        """
        variations = [
            {
                "id": "clean_code",
                "params": {"style": "clean"},
                "weight": 1.0,
                "metadata": {"description": "Clean, readable code following best practices"}
            },
            {
                "id": "optimized",
                "params": {"style": "optimized", "optimize": True},
                "weight": 0.8,
                "metadata": {"description": "Performance-optimized implementation"}
            },
            {
                "id": "comprehensive",
                "params": {"style": "verbose", "comprehensive": True},
                "weight": 0.9,
                "metadata": {"description": "Comprehensive with docs and tests"}
            },
        ]
        
        # Add language-specific variations if detected
        if "python" in task.lower():
            variations.append({
                "id": "pythonic",
                "params": {"style": "pythonic"},
                "weight": 1.1,
                "metadata": {"description": "Idiomatic Python implementation"}
            })
        elif "javascript" in task.lower() or "typescript" in task.lower():
            variations.append({
                "id": "modern_js",
                "params": {"style": "modern_js"},
                "weight": 1.1,
                "metadata": {"description": "Modern JavaScript/TypeScript patterns"}
            })
            
        return variations
        
    async def _analyze_requirements(self, task: str, context: AgentContext) -> Dict[str, Any]:
        """Analyze task requirements to determine approach"""
        analysis = {
            "complexity": self._estimate_complexity(task),
            "language": self._detect_language(task, context),
            "patterns": self._identify_patterns(task),
            "include_tests": "test" in task.lower(),
            "include_docs": "document" in task.lower() or "doc" in task.lower(),
            "framework": self._detect_framework(task, context),
        }
        
        # Check context files for additional clues
        if context.files:
            analysis["existing_code"] = True
            analysis["file_types"] = list(set(
                file.split('.')[-1] for file in context.files.keys()
                if '.' in file
            ))
            
        return analysis
        
    async def _select_model(self, analysis: Dict[str, Any]) -> str:
        """Select appropriate model based on task analysis"""
        complexity = analysis.get("complexity", "medium")
        
        if complexity == "high":
            # Use most capable model for complex tasks
            return "gpt-5"  # Latest flagship model with reasoning capabilities
        elif complexity == "low":
            # Use faster model for simple tasks
            return "gpt-5-mini"  # Fast and cost-effective GPT-5 variant
        else:
            # Default to balanced model
            return "gpt-5"  # Default flagship model
            
    async def _call_ai_provider(self, prompt: str, model: str, **kwargs) -> Dict[str, Any]:
        """
        Actually call the AI provider to generate code.
        
        Args:
            prompt: The prompt to send to the AI
            model: Model to use for generation
            **kwargs: Additional parameters for the AI call
            
        Returns:
            Response from the AI provider
        """
        if not self.provider_registry:
            logger.warning("No provider registry available, returning placeholder")
            return {"result": f"# Placeholder code - Provider registry not available\n# Prompt: {prompt[:100]}..."}
        
        # Try OpenAI first (as it has GPT-5 support)
        from ...providers import ProviderType
        openai_provider = self.provider_registry.get_provider(ProviderType.OPENAI)
        
        if openai_provider:
            try:
                # Prepare messages for the AI call
                messages = [
                    {
                        "role": "system",
                        "content": "You are an expert software engineer. Generate high-quality, production-ready code based on the user's requirements. Follow best practices, include proper error handling, and add comments where helpful."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
                
                # Call the provider with GPT-5 support
                response = await openai_provider.generate_completion(
                    model=model,
                    messages=messages,
                    max_tokens=kwargs.get("max_tokens", 4096),
                    temperature=kwargs.get("temperature", 0.1),
                    enable_web_search=kwargs.get("enable_web_search", False),
                    **kwargs
                )
                
                logger.info(f"Successfully generated code using {model}")
                return {"result": response.get("content", "")}
                
            except Exception as e:
                logger.error(f"Failed to call OpenAI provider: {e}")
                # Fallback to placeholder
                return {"result": f"# Error calling AI provider: {e}\n# Prompt: {prompt[:100]}..."}
        
        # Fallback if no provider available
        logger.warning("No OpenAI provider available, returning placeholder")
        return {"result": f"# Placeholder code - No AI provider available\n# Prompt: {prompt[:100]}..."}

    def _build_code_generation_prompt(self, task: str, analysis: Dict[str, Any], 
                                    context: AgentContext, mcp_context: Dict[str, Any], 
                                    style: str = "clean") -> str:
        """Build a comprehensive prompt for code generation."""
        prompt_parts = [
            f"Task: {task}",
            f"Programming Language: {analysis.get('language', 'python')}",
            f"Style: {style}",
            f"Complexity: {analysis.get('complexity', 'medium')}",
        ]
        
        if analysis.get('framework'):
            prompt_parts.append(f"Framework: {analysis['framework']}")
            
        if analysis.get('patterns'):
            prompt_parts.append(f"Design Patterns: {', '.join(analysis['patterns'])}")
        
        # Add context information
        context_str = self._format_context(context, mcp_context)
        if context_str != "No additional context":
            prompt_parts.append(f"Context:\n{context_str}")
        
        # Add specific style instructions
        style_instructions = {
            "clean": "Generate clean, readable code following best practices. Include clear variable names, proper formatting, and helpful comments.",
            "optimized": "Generate performance-optimized code. Focus on efficiency, minimize redundancy, and use optimal algorithms and data structures.",
            "comprehensive": "Generate comprehensive code with full documentation, error handling, input validation, and unit tests.",
            "pythonic": "Generate idiomatic Python code following PEP 8 standards and Python best practices.",
            "modern_js": "Generate modern JavaScript/TypeScript using ES6+ features, async/await, and current best practices."
        }
        
        if style in style_instructions:
            prompt_parts.append(f"Instructions: {style_instructions[style]}")
        
        # Add requirements for tests and documentation if requested
        if analysis.get('include_tests'):
            prompt_parts.append("Please include unit tests for the generated code.")
            
        if analysis.get('include_docs'):
            prompt_parts.append("Please include comprehensive documentation.")
        
        return "\n\n".join(prompt_parts)
            
    async def _generate_clean_code(self, task: str, analysis: Dict[str, Any], 
                                  context: AgentContext, mcp_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate clean, readable code"""
        model = await self._select_model(analysis)
        prompt = self._build_code_generation_prompt(task, analysis, context, mcp_context, "clean")
        
        # Actually call the AI provider
        response = await self._call_ai_provider(prompt, model)
        
        return {"code": response["result"]}
        
    async def _generate_optimized_code(self, task: str, analysis: Dict[str, Any],
                                     context: AgentContext, mcp_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance-optimized code"""
        model = await self._select_model(analysis)
        prompt = self._build_code_generation_prompt(task, analysis, context, mcp_context, "optimized")
        
        # Actually call the AI provider
        response = await self._call_ai_provider(prompt, model, temperature=0.05)  # Lower temperature for optimization
        
        return {"code": response["result"]}
        
    async def _generate_comprehensive_code(self, task: str, analysis: Dict[str, Any],
                                         context: AgentContext, mcp_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive code with all supporting files"""
        model = await self._select_model(analysis)
        prompt = self._build_code_generation_prompt(task, analysis, context, mcp_context, "comprehensive")
        
        # Actually call the AI provider with higher token limit for comprehensive output
        response = await self._call_ai_provider(prompt, model, max_tokens=8192, temperature=0.2)
        
        # Parse multiple files from response
        code_parts = self._parse_multiple_files(response["result"])
        
        return {
            "code": code_parts.get("main", response["result"]),
            "files": code_parts
        }
        
    async def _generate_default_code(self, task: str, analysis: Dict[str, Any],
                                   context: AgentContext, mcp_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate code with balanced approach"""
        return await self._generate_clean_code(task, analysis, context, mcp_context)
        
    async def _generate_documentation(self, code: str, analysis: Dict[str, Any]) -> str:
        """Generate documentation for the code"""
        if not self.provider_registry:
            return f"# Documentation placeholder - Provider not available\n## Overview\nDocumentation for {analysis['language']} code."
        
        model = await self._select_model(analysis)
        prompt = f"""Generate comprehensive documentation for the following code:

Language: {analysis.get('language', 'python')}
Framework: {analysis.get('framework', 'N/A')}

Code:
```
{code}
```

Please provide:
1. Overview of what the code does
2. Function/class descriptions
3. Parameter explanations
4. Usage examples
5. Any important notes or considerations

Format the documentation appropriately for {analysis.get('language', 'python')} (e.g., docstrings for Python, JSDoc for JavaScript)."""

        response = await self._call_ai_provider(prompt, model, max_tokens=2048)
        return response["result"]
        
    async def _generate_tests(self, code: str, analysis: Dict[str, Any]) -> str:
        """Generate tests for the code"""
        framework = analysis.get("framework", "pytest" if analysis["language"] == "python" else "jest")
        
        if not self.provider_registry:
            return f"# Test placeholder - Provider not available\n# Framework: {framework}\n# Test implementation placeholder"
        
        model = await self._select_model(analysis)
        prompt = f"""Generate comprehensive unit tests for the following code:

Language: {analysis.get('language', 'python')}
Testing Framework: {framework}

Code to test:
```
{code}
```

Please provide:
1. Test cases covering main functionality
2. Edge cases and error conditions
3. Mock dependencies where appropriate
4. Clear test descriptions
5. Proper setup and teardown if needed

Follow {framework} testing conventions and best practices."""

        response = await self._call_ai_provider(prompt, model, max_tokens=3072)
        return response["result"]
        
    def _estimate_complexity(self, task: str) -> str:
        """Estimate task complexity"""
        task_lower = task.lower()
        
        # High complexity indicators
        if any(term in task_lower for term in ["architecture", "system", "microservice", "distributed", "full stack"]):
            return "high"
            
        # Low complexity indicators
        if any(term in task_lower for term in ["simple", "basic", "function", "helper", "utility"]):
            return "low"
            
        return "medium"
        
    def _detect_language(self, task: str, context: AgentContext) -> str:
        """Detect programming language from task and context"""
        task_lower = task.lower()
        
        # Check explicit mentions
        languages = {
            "python": ["python", "py", "django", "flask", "fastapi"],
            "javascript": ["javascript", "js", "node", "react", "vue", "angular"],
            "typescript": ["typescript", "ts", "tsx"],
            "java": ["java", "spring", "springboot"],
            "go": ["go", "golang"],
            "rust": ["rust", "cargo"],
            "cpp": ["c++", "cpp"],
            "csharp": ["c#", "csharp", "dotnet", ".net"],
        }
        
        for lang, keywords in languages.items():
            if any(kw in task_lower for kw in keywords):
                return lang
                
        # Check file extensions in context
        if context.files:
            for filename in context.files.keys():
                if filename.endswith(".py"):
                    return "python"
                elif filename.endswith((".js", ".jsx")):
                    return "javascript"
                elif filename.endswith((".ts", ".tsx")):
                    return "typescript"
                    
        # Default to Python
        return "python"
        
    def _identify_patterns(self, task: str) -> List[str]:
        """Identify design patterns mentioned in task"""
        patterns = []
        task_lower = task.lower()
        
        pattern_keywords = {
            "singleton": ["singleton"],
            "factory": ["factory"],
            "observer": ["observer", "event", "listener"],
            "mvc": ["mvc", "model view controller"],
            "repository": ["repository"],
            "adapter": ["adapter"],
            "decorator": ["decorator"],
            "strategy": ["strategy"],
        }
        
        for pattern, keywords in pattern_keywords.items():
            if any(kw in task_lower for kw in keywords):
                patterns.append(pattern)
                
        return patterns
        
    def _detect_framework(self, task: str, context: AgentContext) -> Optional[str]:
        """Detect framework from task and context"""
        task_lower = task.lower()
        
        frameworks = {
            "django": ["django"],
            "flask": ["flask"],
            "fastapi": ["fastapi"],
            "react": ["react"],
            "vue": ["vue"],
            "angular": ["angular"],
            "express": ["express"],
            "spring": ["spring"],
            "rails": ["rails", "ruby on rails"],
        }
        
        for framework, keywords in frameworks.items():
            if any(kw in task_lower for kw in keywords):
                return framework
                
        return None
        
    def _format_context(self, context: AgentContext, mcp_context: Dict[str, Any]) -> str:
        """Format context for prompt"""
        context_parts = []
        
        if context.files:
            context_parts.append("Existing files:")
            for filename, content in context.files.items():
                context_parts.append(f"\n{filename}:\n{content[:500]}...")
                
        if mcp_context.get("project_structure"):
            context_parts.append("\nProject structure:")
            context_parts.append(str(mcp_context["project_structure"]))
            
        if context.metadata:
            context_parts.append("\nAdditional context:")
            context_parts.append(str(context.metadata))
            
        return "\n".join(context_parts) if context_parts else "No additional context"
        
    def _parse_multiple_files(self, response: str) -> Dict[str, str]:
        """Parse multiple files from a single response"""
        files = {}
        current_file = None
        current_content: List[str] = []
        
        for line in response.split('\n'):
            # Simple file detection pattern
            if line.startswith("### File:") or line.startswith("## File:") or line.startswith("# File:"):
                if current_file and current_content:
                    files[current_file] = '\n'.join(current_content)
                current_file = line.split(":", 1)[1].strip()
                current_content = []
            elif current_file:
                current_content.append(line)
                
        # Save last file
        if current_file and current_content:
            files[current_file] = '\n'.join(current_content)
            
        # If no files detected, treat entire response as main
        if not files:
            files["main"] = response
            
        return files
        
    def _calculate_confidence(self, code: Dict[str, Any], analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for generated code"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on completeness
        if code.get("code"):
            confidence += 0.2
        if code.get("documentation"):
            confidence += 0.1
        if code.get("tests"):
            confidence += 0.1
            
        # Adjust based on complexity match
        if analysis.get("complexity") == "low":
            confidence += 0.1
        elif analysis.get("complexity") == "high" and code.get("files"):
            confidence += 0.05
            
        return min(confidence, 1.0)
        
    def _learn_from_generation(self, task: str, code: Dict[str, Any], analysis: Dict[str, Any]):
        """Learn patterns from successful generation"""
        # Store successful patterns
        if code.get("confidence", 0) > 0.8:
            pattern_key = f"{analysis['language']}_{analysis.get('framework', 'general')}"
            patterns = self.recall_memory("successful_patterns") or {}
            
            if pattern_key not in patterns:
                patterns[pattern_key] = []
                
            patterns[pattern_key].append({
                "task_summary": task[:100],
                "approach": analysis,
                "confidence": code.get("confidence", 0),
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only last 10 patterns per key
            patterns[pattern_key] = patterns[pattern_key][-10:]
            
            self.update_memory("successful_patterns", patterns)
