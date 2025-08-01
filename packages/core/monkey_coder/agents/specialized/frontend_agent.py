"""
Frontend Specialist Agent - Specialized in UI/UX and frontend development
Focuses on React, Vue, Angular, CSS, HTML, and modern frontend frameworks
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..base_agent import BaseAgent, AgentCapability, AgentContext

logger = logging.getLogger(__name__)


class FrontendAgent(BaseAgent):
    """
    Specialized agent for frontend development tasks
    Expertise in UI/UX, React, Vue, Angular, CSS, HTML, accessibility
    """
    
    def __init__(self):
        super().__init__(
            name="FrontendSpecialist",
            capabilities={
                AgentCapability.CODE_GENERATION,
                AgentCapability.CODE_REVIEW,
                AgentCapability.ARCHITECTURE_DESIGN,
                AgentCapability.TESTING,
                AgentCapability.PERFORMANCE_OPTIMIZATION,
            }
        )
        self.specialization = "frontend"
        self.preferred_model = "gpt-4.1"  # Use flagship model for complex UI work
        
    async def _setup(self):
        """Initialize frontend-specific resources"""
        logger.info("Setting up Frontend Specialist Agent")
        
        # Frontend frameworks and patterns
        self.update_memory("frontend_frameworks", {
            "react": {
                "patterns": ["hooks", "context", "higher_order_components", "render_props"],
                "libraries": ["redux", "zustand", "react-query", "styled-components"],
                "testing": ["jest", "react-testing-library", "enzyme"]
            },
            "vue": {
                "patterns": ["composition_api", "options_api", "mixins", "composables"],
                "libraries": ["vuex", "pinia", "vue-router", "vuetify"],
                "testing": ["vue-test-utils", "cypress"]
            },
            "angular": {
                "patterns": ["components", "services", "directives", "pipes"],
                "libraries": ["rxjs", "ngrx", "angular-material", "primeng"],
                "testing": ["jasmine", "karma", "protractor"]
            },
            "vanilla": {
                "patterns": ["web_components", "module_pattern", "observer_pattern"],
                "libraries": ["lit", "stencil", "web-components"],
                "testing": ["mocha", "chai", "sinon"]
            }
        }, memory_type="long_term")
        
        # CSS and styling patterns
        self.update_memory("styling_patterns", {
            "methodologies": ["bem", "atomic_css", "oocss", "smacss"],
            "preprocessors": ["sass", "less", "stylus", "postcss"],
            "frameworks": ["tailwind", "bootstrap", "material-ui", "ant-design"],
            "architecture": ["css-in-js", "css-modules", "styled-components"]
        }, memory_type="long_term")
        
        # Accessibility and UX patterns
        self.update_memory("accessibility_patterns", {
            "aria": ["roles", "properties", "states", "live-regions"],
            "keyboard": ["tab-order", "focus-management", "keyboard-shortcuts"],
            "screen_readers": ["alt-text", "semantic-html", "headings"],
            "guidelines": ["wcag-aa", "wcag-aaa", "section-508"]
        }, memory_type="long_term")
        
    async def can_handle_task(self, task_description: str, context: AgentContext) -> float:
        """Determine if this agent can handle the task"""
        frontend_keywords = [
            "react", "vue", "angular", "frontend", "ui", "ux", "css", "html",
            "component", "interface", "responsive", "accessibility", "styling",
            "form", "navigation", "dashboard", "layout", "design system",
            "typescript", "javascript", "jsx", "tsx", "scss", "sass",
            "tailwind", "bootstrap", "material-ui", "antd", "styled-components"
        ]
        
        task_lower = task_description.lower()
        matches = sum(1 for keyword in frontend_keywords if keyword in task_lower)
        
        # Higher confidence for frontend-specific tasks
        base_confidence = min(0.9, matches * 0.15)
        
        # Boost confidence for specific frontend patterns
        if any(pattern in task_lower for pattern in ["component", "interface", "ui", "frontend"]):
            base_confidence += 0.2
            
        if any(framework in task_lower for framework in ["react", "vue", "angular"]):
            base_confidence += 0.3
            
        return min(1.0, base_confidence)
    
    async def _execute_task(self, task_description: str, context: AgentContext) -> Dict[str, Any]:
        """Execute frontend development task"""
        logger.info(f"Frontend Agent executing: {task_description}")
        
        # Analyze task type
        task_type = self._determine_task_type(task_description)
        
        # Prepare specialized prompt based on task type
        if task_type == "component_creation":
            result = await self._handle_component_creation(task_description, context)
        elif task_type == "styling":
            result = await self._handle_styling_task(task_description, context)
        elif task_type == "accessibility":
            result = await self._handle_accessibility_task(task_description, context)
        elif task_type == "performance":
            result = await self._handle_performance_task(task_description, context)
        elif task_type == "testing":
            result = await self._handle_testing_task(task_description, context)
        else:
            result = await self._handle_general_frontend_task(task_description, context)
        
        return {
            "type": "frontend_development",
            "task_type": task_type,
            "result": result,
            "specialization": "frontend",
            "frameworks_used": self._detect_frameworks(task_description),
            "accessibility_considered": "accessibility" in task_description.lower(),
            "responsive_design": "responsive" in task_description.lower()
        }
    
    def _determine_task_type(self, task_description: str) -> str:
        """Determine the specific type of frontend task"""
        task_lower = task_description.lower()
        
        if any(word in task_lower for word in ["component", "widget", "element"]):
            return "component_creation"
        elif any(word in task_lower for word in ["style", "css", "design", "theme"]):
            return "styling"
        elif any(word in task_lower for word in ["accessibility", "a11y", "screen reader"]):
            return "accessibility"
        elif any(word in task_lower for word in ["performance", "optimize", "bundle"]):
            return "performance"
        elif any(word in task_lower for word in ["test", "testing", "spec"]):
            return "testing"
        else:
            return "general"
    
    def _detect_frameworks(self, task_description: str) -> List[str]:
        """Detect frameworks mentioned in task description"""
        frameworks = []
        task_lower = task_description.lower()
        
        framework_map = {
            "react": ["react", "jsx", "tsx"],
            "vue": ["vue", "vue.js"],
            "angular": ["angular", "ng"],
            "svelte": ["svelte"],
            "solid": ["solid.js", "solidjs"]
        }
        
        for framework, keywords in framework_map.items():
            if any(keyword in task_lower for keyword in keywords):
                frameworks.append(framework)
        
        return frameworks
    
    async def _handle_component_creation(self, task_description: str, context: AgentContext) -> str:
        """Handle component creation tasks"""
        frameworks = self._detect_frameworks(task_description)
        framework = frameworks[0] if frameworks else "react"  # Default to React
        
        prompt = f"""
As a Frontend Specialist Agent, create a high-quality {framework} component based on this request:

{task_description}

Requirements:
1. Follow {framework} best practices and patterns
2. Include proper TypeScript types if applicable
3. Implement accessibility features (ARIA labels, keyboard navigation)
4. Include responsive design considerations
5. Add proper error handling and loading states
6. Include comprehensive JSDoc comments
7. Consider performance optimizations

Context from previous work:
{self._format_context(context)}

Please provide:
1. Component implementation
2. Usage examples
3. Props/API documentation
4. Accessibility notes
5. Testing suggestions
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_styling_task(self, task_description: str, context: AgentContext) -> str:
        """Handle CSS/styling tasks"""
        prompt = f"""
As a Frontend Specialist Agent, create comprehensive styling solution for:

{task_description}

Requirements:
1. Follow CSS best practices and methodologies (BEM, OOCSS)
2. Ensure responsive design for mobile, tablet, desktop
3. Include accessibility considerations (contrast, focus states)
4. Optimize for performance (minimize reflows, efficient selectors)
5. Use modern CSS features where appropriate
6. Include fallbacks for older browsers if needed
7. Consider dark mode and theme support

Context from previous work:
{self._format_context(context)}

Please provide:
1. CSS/SCSS implementation
2. Mobile-first responsive breakpoints
3. Accessibility compliance notes
4. Browser compatibility information
5. Performance considerations
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_accessibility_task(self, task_description: str, context: AgentContext) -> str:
        """Handle accessibility-focused tasks"""
        prompt = f"""
As a Frontend Specialist Agent with accessibility expertise, address:

{task_description}

Requirements:
1. Ensure WCAG 2.1 AA compliance
2. Implement proper ARIA attributes and roles
3. Optimize for screen readers and assistive technologies
4. Include keyboard navigation support
5. Ensure sufficient color contrast
6. Provide alternative text for images
7. Implement proper focus management

Context from previous work:
{self._format_context(context)}

Please provide:
1. Accessibility implementation
2. ARIA attribute usage
3. Keyboard navigation patterns
4. Screen reader testing notes
5. WCAG compliance checklist
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_performance_task(self, task_description: str, context: AgentContext) -> str:
        """Handle performance optimization tasks"""
        prompt = f"""
As a Frontend Specialist Agent focused on performance, optimize:

{task_description}

Requirements:
1. Implement code splitting and lazy loading
2. Optimize bundle size and load times
3. Use efficient rendering patterns
4. Minimize DOM manipulations
5. Implement proper caching strategies
6. Optimize images and assets
7. Follow Core Web Vitals best practices

Context from previous work:
{self._format_context(context)}

Please provide:
1. Performance optimization implementation
2. Bundle analysis recommendations
3. Loading strategy improvements
4. Caching implementation
5. Performance monitoring suggestions
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_testing_task(self, task_description: str, context: AgentContext) -> str:
        """Handle frontend testing tasks"""
        frameworks = self._detect_frameworks(task_description)
        framework = frameworks[0] if frameworks else "react"
        
        prompt = f"""
As a Frontend Specialist Agent, create comprehensive tests for:

{task_description}

Requirements:
1. Write unit tests for {framework} components
2. Include integration tests for user interactions
3. Add accessibility testing
4. Test responsive behavior
5. Include error boundary testing
6. Add performance testing considerations
7. Implement visual regression testing if needed

Context from previous work:
{self._format_context(context)}

Please provide:
1. Unit test implementation
2. Integration test scenarios
3. Accessibility test cases
4. Mock strategies
5. Test coverage analysis
"""
        
        return await self._generate_response(prompt, context)
    
    async def _handle_general_frontend_task(self, task_description: str, context: AgentContext) -> str:
        """Handle general frontend development tasks"""
        prompt = f"""
As a Frontend Specialist Agent, complete this frontend development task:

{task_description}

Requirements:
1. Follow modern frontend best practices
2. Ensure cross-browser compatibility
3. Implement responsive design
4. Include accessibility features
5. Optimize for performance
6. Add proper error handling
7. Include comprehensive documentation

Context from previous work:
{self._format_context(context)}

Please provide a complete, production-ready solution with explanations.
"""
        
        return await self._generate_response(prompt, context)    
    async def process(self, task: str, context: AgentContext) -> Dict[str, Any]:
        """Process a frontend development task"""
        return await self._execute_task(task, context)
