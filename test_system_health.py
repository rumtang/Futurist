"""
System health check for CX Futurist AI.

Verifies that all services are running and can process requests.
"""

import asyncio
import httpx
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, List, Tuple
import socketio
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn


# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8100")
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL", "ws://localhost:8100")
TIMEOUT_SECONDS = 10

# Rich console for pretty output
console = Console()


class SystemHealthChecker:
    """Check health of all system components."""
    
    def __init__(self):
        self.results: Dict[str, Dict[str, Any]] = {}
        self.api_client = None
        self.socket_client = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.api_client = httpx.AsyncClient(base_url=API_BASE_URL, timeout=TIMEOUT_SECONDS)
        self.socket_client = socketio.AsyncClient()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.api_client:
            await self.api_client.aclose()
        if self.socket_client and self.socket_client.connected:
            await self.socket_client.disconnect()
    
    async def check_api_health(self) -> Tuple[bool, Dict[str, Any]]:
        """Check if API is healthy."""
        try:
            response = await self.api_client.get("/health")
            if response.status_code == 200:
                data = response.json()
                return True, {
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds(),
                    "services": data.get("services", {}),
                    "version": data.get("version", "unknown")
                }
            else:
                return False, {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}",
                    "response": response.text
                }
        except Exception as e:
            return False, {
                "status": "unreachable",
                "error": str(e)
            }
    
    async def check_api_status(self) -> Tuple[bool, Dict[str, Any]]:
        """Check system status endpoint."""
        try:
            response = await self.api_client.get("/api/status")
            if response.status_code == 200:
                data = response.json()
                return True, {
                    "status": data.get("status", "unknown"),
                    "services": data.get("services", {}),
                    "orchestrator": data.get("orchestrator", False),
                    "message": data.get("message", "")
                }
            else:
                return False, {
                    "status": "error",
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return False, {
                "status": "unreachable",
                "error": str(e)
            }
    
    async def check_agents(self) -> Tuple[bool, Dict[str, Any]]:
        """Check if agents are available."""
        try:
            response = await self.api_client.get("/api/agents/status")
            if response.status_code == 200:
                data = response.json()
                agents = data.get("agents", {})
                
                # Check for required agents
                required_agents = {
                    "ai_futurist", "trend_scanner", "customer_insight",
                    "tech_impact", "org_transformation", "synthesis"
                }
                
                available_agents = set(agents.keys())
                missing_agents = required_agents - available_agents
                
                return len(missing_agents) == 0, {
                    "total_agents": len(agents),
                    "available": list(available_agents),
                    "missing": list(missing_agents),
                    "all_required_present": len(missing_agents) == 0
                }
            else:
                return False, {
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return False, {
                "error": str(e)
            }
    
    async def check_websocket(self) -> Tuple[bool, Dict[str, Any]]:
        """Check WebSocket connectivity."""
        try:
            # Use simple WebSocket test
            import websockets
            
            ws_url = f"{WEBSOCKET_URL.replace('ws://', 'ws://')}/simple-ws"
            async with websockets.connect(ws_url) as websocket:
                await websocket.send('{"type": "ping"}')
                response = await websocket.recv()
                return True, {
                    "status": "connected",
                    "response": response[:100] + "..." if len(response) > 100 else response
                }
                
        except Exception as e:
            return False, {
                "status": "error",
                "error": str(e)
            }
    
    async def test_simple_workflow(self) -> Tuple[bool, Dict[str, Any]]:
        """Test a simple workflow execution."""
        try:
            # Start a quick analysis
            request_data = {
                "topic": "Health check test analysis",
                "depth": "quick",
                "timeframe": "1-2 years"
            }
            
            response = await self.api_client.post("/api/analysis/", json=request_data)
            if response.status_code == 200:
                data = response.json()
                request_id = data.get("request_id")
                
                # Wait a moment and check status
                await asyncio.sleep(2)
                
                status_response = await self.api_client.get(f"/api/analysis/{request_id}")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    return True, {
                        "request_id": request_id,
                        "status": status_data.get("status", "unknown"),
                        "workflow_initiated": True
                    }
                else:
                    return False, {
                        "error": f"Status check failed: HTTP {status_response.status_code}"
                    }
            else:
                return False, {
                    "error": f"Failed to start workflow: HTTP {response.status_code}"
                }
        except Exception as e:
            return False, {
                "error": str(e)
            }
    
    async def check_external_services(self) -> Dict[str, Tuple[bool, Dict[str, Any]]]:
        """Check external service connectivity."""
        results = {}
        
        # Check OpenAI API (by checking if orchestrator is running)
        try:
            response = await self.api_client.get("/api/status")
            if response.status_code == 200:
                data = response.json()
                openai_status = data.get("services", {}).get("openai", False)
                results["openai"] = (openai_status, {"configured": openai_status})
            else:
                results["openai"] = (False, {"error": "Could not check status"})
        except Exception as e:
            results["openai"] = (False, {"error": str(e)})
        
        # Check Pinecone (vector DB)
        results["pinecone"] = await self._check_service_status("pinecone")
        
        # Check Redis
        results["redis"] = await self._check_service_status("redis")
        
        return results
    
    async def _check_service_status(self, service: str) -> Tuple[bool, Dict[str, Any]]:
        """Check status of a specific service."""
        try:
            response = await self.api_client.get("/api/status")
            if response.status_code == 200:
                data = response.json()
                service_status = data.get("services", {}).get(service, False)
                return (service_status, {"available": service_status})
            else:
                return (False, {"error": "Could not check status"})
        except Exception as e:
            return (False, {"error": str(e)})
    
    async def run_all_checks(self) -> Dict[str, Dict[str, Any]]:
        """Run all health checks."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # API Health
            task = progress.add_task("Checking API health...", total=1)
            success, result = await self.check_api_health()
            self.results["api_health"] = {"success": success, "details": result}
            progress.update(task, completed=1)
            
            # System Status
            task = progress.add_task("Checking system status...", total=1)
            success, result = await self.check_api_status()
            self.results["system_status"] = {"success": success, "details": result}
            progress.update(task, completed=1)
            
            # Agents
            task = progress.add_task("Checking agents...", total=1)
            success, result = await self.check_agents()
            self.results["agents"] = {"success": success, "details": result}
            progress.update(task, completed=1)
            
            # WebSocket
            task = progress.add_task("Checking WebSocket...", total=1)
            success, result = await self.check_websocket()
            self.results["websocket"] = {"success": success, "details": result}
            progress.update(task, completed=1)
            
            # Workflow
            task = progress.add_task("Testing workflow...", total=1)
            success, result = await self.test_simple_workflow()
            self.results["workflow"] = {"success": success, "details": result}
            progress.update(task, completed=1)
            
            # External Services
            task = progress.add_task("Checking external services...", total=1)
            external_results = await self.check_external_services()
            self.results["external_services"] = {
                service: {"success": result[0], "details": result[1]}
                for service, result in external_results.items()
            }
            progress.update(task, completed=1)
        
        return self.results


def create_results_table(results: Dict[str, Dict[str, Any]]) -> Table:
    """Create a rich table showing health check results."""
    table = Table(title="System Health Check Results", show_header=True)
    table.add_column("Component", style="cyan", width=20)
    table.add_column("Status", width=10)
    table.add_column("Details", style="dim")
    
    # API Health
    api_health = results.get("api_health", {})
    status = "✅ OK" if api_health.get("success") else "❌ FAIL"
    details = api_health.get("details", {})
    if api_health.get("success"):
        detail_text = f"v{details.get('version', '?')} - {details.get('response_time', 0):.2f}s"
    else:
        detail_text = details.get("error", "Unknown error")
    table.add_row("API Health", status, detail_text)
    
    # System Status
    system_status = results.get("system_status", {})
    status = "✅ OK" if system_status.get("success") else "❌ FAIL"
    details = system_status.get("details", {})
    detail_text = details.get("status", "unknown").upper()
    table.add_row("System Status", status, detail_text)
    
    # Agents
    agents = results.get("agents", {})
    status = "✅ OK" if agents.get("success") else "❌ FAIL"
    details = agents.get("details", {})
    if agents.get("success"):
        detail_text = f"{details.get('total_agents', 0)} agents ready"
    else:
        missing = details.get("missing", [])
        detail_text = f"Missing: {', '.join(missing)}" if missing else "Error"
    table.add_row("Agents", status, detail_text)
    
    # WebSocket
    websocket = results.get("websocket", {})
    status = "✅ OK" if websocket.get("success") else "❌ FAIL"
    details = websocket.get("details", {})
    detail_text = details.get("status", "unknown")
    table.add_row("WebSocket", status, detail_text)
    
    # Workflow
    workflow = results.get("workflow", {})
    status = "✅ OK" if workflow.get("success") else "❌ FAIL"
    details = workflow.get("details", {})
    if workflow.get("success"):
        detail_text = f"Status: {details.get('status', 'unknown')}"
    else:
        detail_text = details.get("error", "Failed")
    table.add_row("Workflow Test", status, detail_text)
    
    # External Services
    external = results.get("external_services", {})
    for service, data in external.items():
        status = "✅ OK" if data.get("success") else "⚠️  N/A"
        details = data.get("details", {})
        if data.get("success"):
            detail_text = "Available"
        else:
            detail_text = "Not configured" if not details.get("available") else "Error"
        table.add_row(f"  - {service.title()}", status, detail_text)
    
    return table


async def main():
    """Run system health checks."""
    console.print(Panel.fit(
        "[bold cyan]CX Futurist AI System Health Check[/bold cyan]\n" +
        f"Target: {API_BASE_URL}",
        border_style="cyan"
    ))
    console.print()
    
    # Run health checks
    async with SystemHealthChecker() as checker:
        try:
            results = await checker.run_all_checks()
            
            # Display results
            console.print()
            table = create_results_table(results)
            console.print(table)
            
            # Overall status
            all_core_ok = all(
                results.get(check, {}).get("success", False)
                for check in ["api_health", "system_status", "agents", "workflow"]
            )
            
            console.print()
            if all_core_ok:
                console.print("[bold green]✅ System is HEALTHY and ready for use![/bold green]")
                
                # Note about optional services
                external = results.get("external_services", {})
                unavailable = [
                    service for service, data in external.items()
                    if not data.get("success")
                ]
                if unavailable:
                    console.print(f"[yellow]Note: Optional services not available: {', '.join(unavailable)}[/yellow]")
                    console.print("[dim]The system will run with reduced functionality.[/dim]")
                
                return 0
            else:
                console.print("[bold red]❌ System has CRITICAL issues![/bold red]")
                
                # List critical failures
                failures = []
                for check in ["api_health", "system_status", "agents", "workflow"]:
                    if not results.get(check, {}).get("success", False):
                        failures.append(check)
                
                if failures:
                    console.print(f"[red]Failed checks: {', '.join(failures)}[/red]")
                
                return 1
                
        except Exception as e:
            console.print(f"[bold red]❌ Health check failed with error: {e}[/bold red]")
            return 1


if __name__ == "__main__":
    # Run the health check
    exit_code = asyncio.run(main())
    sys.exit(exit_code)