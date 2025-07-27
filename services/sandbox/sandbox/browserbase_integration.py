"""
BrowserBase Sandbox Integration

Provides secure browser automation environment using BrowserBase cloud browsers.
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from browserbase import Browserbase
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

logger = logging.getLogger(__name__)


class BrowserBaseSandboxManager:
    """Manages BrowserBase browser instances for secure automation."""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_metadata: Dict[str, Dict[str, Any]] = {}
        self.api_key = os.getenv("BROWSERBASE_API_KEY")
        self.project_id = os.getenv("BROWSERBASE_PROJECT_ID")
        
        if not self.api_key or not self.project_id:
            logger.warning("BrowserBase credentials not found. Browser automation disabled.")
        
        # Initialize BrowserBase client
        if self.api_key:
            self.browserbase = Browserbase(self.api_key)
    
    async def execute_browser_action(
        self,
        url: str,
        action: str,
        execution_id: str,
        timeout: int = 30,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute browser automation action using BrowserBase.
        
        Args:
            url: Target URL
            action: Action to perform (navigate, screenshot, extract_text, etc.)
            execution_id: Unique execution identifier
            timeout: Execution timeout in seconds
            metadata: Additional execution metadata
            
        Returns:
            Dictionary containing action results and logs
        """
        if not self.api_key or not self.project_id:
            raise RuntimeError("BrowserBase credentials not configured")
        
        session_data = None
        try:
            # Create browser session
            session_data = await self._create_browser_session(execution_id, timeout)
            
            # Execute browser action with timeout
            result = await asyncio.wait_for(
                self._execute_action(session_data, url, action, metadata),
                timeout=timeout
            )
            
            return {
                "output": result,
                "logs": session_data.get("logs", []),
                "session_id": session_data.get("session_id"),
                "execution_time": result.get("execution_time", 0)
            }
            
        except asyncio.TimeoutError:
            logger.error(f"Browser action timeout for {execution_id}")
            return {
                "output": None,
                "logs": [f"Browser action timed out after {timeout} seconds"],
                "error": "TIMEOUT"
            }
        except Exception as e:
            logger.error(f"BrowserBase execution failed for {execution_id}: {str(e)}")
            return {
                "output": None,
                "logs": [f"Browser action error: {str(e)}"],
                "error": str(e)
            }
        finally:
            if session_data and execution_id in self.active_sessions:
                await self._cleanup_session(execution_id)
    
    async def _create_browser_session(
        self,
        execution_id: str,
        timeout: int
    ) -> Dict[str, Any]:
        """Create and configure a new BrowserBase session."""
        try:
            # Create session via API
            session_response = await self._create_session_api()
            session_id = session_response["id"]
            
            # Connect to browser using Playwright
            playwright = await async_playwright().start()
            browser = await playwright.chromium.connect_over_cdp(
                f"wss://connect.browserbase.com?apiKey={self.api_key}&sessionId={session_id}"
            )
            
            # Get default context and page
            context = browser.contexts[0] if browser.contexts else await browser.new_context()
            page = await context.new_page() if not context.pages else context.pages[0]
            
            session_data = {
                "session_id": session_id,
                "playwright": playwright,
                "browser": browser,
                "context": context,
                "page": page,
                "logs": [],
                "created_at": datetime.utcnow()
            }
            
            # Store session reference
            self.active_sessions[execution_id] = session_data
            self.session_metadata[execution_id] = {
                "created_at": datetime.utcnow(),
                "timeout": timeout,
                "session_id": session_id
            }
            
            logger.info(f"Created BrowserBase session {session_id} for {execution_id}")
            return session_data
            
        except Exception as e:
            logger.error(f"Failed to create BrowserBase session: {str(e)}")
            raise
    
    async def _create_session_api(self) -> Dict[str, Any]:
        """Create session using BrowserBase API."""
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.browserbase.com/v1/sessions",
                headers={
                    "x-bb-api-key": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "projectId": self.project_id,
                    "browserSettings": {
                        "fingerprint": {
                            "browser": "chrome",
                            "os": "linux"
                        }
                    }
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def _execute_action(
        self,
        session_data: Dict[str, Any],
        url: str,
        action: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the specified browser action."""
        page = session_data["page"]
        logs = session_data["logs"]
        start_time = datetime.utcnow()
        
        try:
            result = {}
            
            if action == "navigate":
                await page.goto(url, wait_until="domcontentloaded")
                result = {"url": url, "title": await page.title()}
                logs.append(f"Navigated to: {url}")
            
            elif action == "screenshot":
                await page.goto(url, wait_until="domcontentloaded")
                screenshot_bytes = await page.screenshot(full_page=True)
                result = {
                    "screenshot": screenshot_bytes.hex(),
                    "url": url,
                    "title": await page.title()
                }
                logs.append(f"Screenshot taken of: {url}")
            
            elif action == "extract_text":
                await page.goto(url, wait_until="domcontentloaded")
                content = await page.inner_text("body")
                result = {
                    "text": content,
                    "url": url,
                    "title": await page.title(),
                    "length": len(content)
                }
                logs.append(f"Text extracted from: {url}")
            
            elif action == "extract_links":
                await page.goto(url, wait_until="domcontentloaded")
                links = await page.evaluate("""
                    () => {
                        const links = Array.from(document.querySelectorAll('a[href]'));
                        return links.map(link => ({
                            text: link.textContent.trim(),
                            href: link.href,
                            title: link.title || null
                        }));
                    }
                """)
                result = {
                    "links": links,
                    "url": url,
                    "count": len(links)
                }
                logs.append(f"Extracted {len(links)} links from: {url}")
            
            elif action == "wait_for_element":
                selector = metadata.get("selector") if metadata else None
                if not selector:
                    raise ValueError("Selector required for wait_for_element action")
                
                await page.goto(url, wait_until="domcontentloaded")
                await page.wait_for_selector(selector, timeout=10000)
                element_text = await page.inner_text(selector)
                result = {
                    "selector": selector,
                    "text": element_text,
                    "url": url
                }
                logs.append(f"Element {selector} found on: {url}")
            
            elif action == "click_element":
                selector = metadata.get("selector") if metadata else None
                if not selector:
                    raise ValueError("Selector required for click_element action")
                
                await page.goto(url, wait_until="domcontentloaded")
                await page.click(selector)
                await page.wait_for_load_state("domcontentloaded")
                result = {
                    "selector": selector,
                    "url": page.url,
                    "title": await page.title()
                }
                logs.append(f"Clicked element {selector} on: {url}")
            
            else:
                raise ValueError(f"Unsupported browser action: {action}")
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            result["execution_time"] = execution_time
            result["success"] = True
            
            return result
            
        except Exception as e:
            logger.error(f"Browser action {action} failed: {str(e)}")
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            logs.append(f"Action {action} failed: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "action": action,
                "url": url
            }
    
    async def _cleanup_session(self, execution_id: str):
        """Clean up a browser session."""
        try:
            if execution_id in self.active_sessions:
                session_data = self.active_sessions[execution_id]
                
                # Close browser resources
                if "page" in session_data:
                    await session_data["page"].close()
                if "context" in session_data:
                    await session_data["context"].close()
                if "browser" in session_data:
                    await session_data["browser"].close()
                if "playwright" in session_data:
                    await session_data["playwright"].stop()
                
                # Remove from tracking
                del self.active_sessions[execution_id]
                del self.session_metadata[execution_id]
                
                logger.info(f"Cleaned up browser session for {execution_id}")
                
        except Exception as e:
            logger.error(f"Failed to cleanup session {execution_id}: {str(e)}")
    
    async def get_active_count(self) -> int:
        """Get the number of active browser sessions."""
        return len(self.active_sessions)
    
    async def cleanup_idle(self) -> int:
        """Clean up idle sessions older than 10 minutes."""
        cleaned_count = 0
        cutoff_time = datetime.utcnow() - timedelta(minutes=10)
        
        idle_executions = []
        for execution_id, metadata in self.session_metadata.items():
            if metadata["created_at"] < cutoff_time:
                idle_executions.append(execution_id)
        
        for execution_id in idle_executions:
            await self._cleanup_session(execution_id)
            cleaned_count += 1
        
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} idle BrowserBase sessions")
        
        return cleaned_count
    
    async def cleanup_all(self):
        """Clean up all active browser sessions."""
        execution_ids = list(self.active_sessions.keys())
        for execution_id in execution_ids:
            await self._cleanup_session(execution_id)
        
        logger.info("Cleaned up all BrowserBase sessions")
