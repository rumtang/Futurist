#!/usr/bin/env python3
"""
Run all tests for the CX Futurist AI system.

This script runs:
1. System health checks
2. Integration tests
3. Unit tests (if available)

And provides a comprehensive report on system readiness.
"""

import asyncio
import subprocess
import sys
import os
import time
from datetime import datetime
from typing import Dict, List, Tuple, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.syntax import Syntax
import json


# Configuration
console = Console()
PYTHON = sys.executable


class TestRunner:
    """Orchestrate running all system tests."""
    
    def __init__(self):
        self.results: Dict[str, Dict[str, Any]] = {}
        self.start_time = None
        self.end_time = None
    
    async def check_dependencies(self) -> bool:
        """Check if required dependencies are installed."""
        required_packages = [
            "httpx",
            "pytest",
            "python-socketio",
            "rich",
            "loguru"
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing.append(package)
        
        if missing:
            console.print(f"[red]Missing dependencies: {', '.join(missing)}[/red]")
            console.print("[yellow]Please install with: pip install httpx pytest python-socketio rich loguru[/yellow]")
            return False
        
        return True
    
    async def check_server_running(self) -> bool:
        """Check if the CX Futurist AI server is running."""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8000/health", timeout=5)
                return response.status_code == 200
        except Exception:
            return False
    
    async def run_health_check(self) -> Tuple[bool, str]:
        """Run system health check."""
        console.print("[cyan]Running system health check...[/cyan]")
        
        try:
            # Import and run health check
            from test_system_health import SystemHealthChecker, create_results_table
            
            async with SystemHealthChecker() as checker:
                results = await checker.run_all_checks()
                
                # Check if all core components are healthy
                all_core_ok = all(
                    results.get(check, {}).get("success", False)
                    for check in ["api_health", "system_status", "agents", "workflow"]
                )
                
                # Create summary
                summary = {
                    "all_core_healthy": all_core_ok,
                    "results": results
                }
                
                self.results["health_check"] = summary
                
                # Create output
                output = []
                for component, data in results.items():
                    status = "✅" if data.get("success") else "❌"
                    output.append(f"{status} {component}")
                
                return all_core_ok, "\n".join(output)
                
        except Exception as e:
            self.results["health_check"] = {
                "error": str(e),
                "all_core_healthy": False
            }
            return False, f"Health check failed: {e}"
    
    async def run_integration_tests(self) -> Tuple[bool, str]:
        """Run integration tests."""
        console.print("[cyan]Running integration tests...[/cyan]")
        
        try:
            # Run integration tests using subprocess to capture output
            result = subprocess.run(
                [PYTHON, "test_integration.py"],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            success = result.returncode == 0
            output = result.stdout if success else result.stderr
            
            # Parse output for test results
            passed_tests = output.count("✅")
            failed_tests = output.count("❌")
            
            self.results["integration_tests"] = {
                "success": success,
                "passed": passed_tests,
                "failed": failed_tests,
                "output": output
            }
            
            summary = f"Passed: {passed_tests}, Failed: {failed_tests}"
            return success, summary
            
        except subprocess.TimeoutExpired:
            self.results["integration_tests"] = {
                "success": False,
                "error": "Timeout"
            }
            return False, "Integration tests timed out"
        except Exception as e:
            self.results["integration_tests"] = {
                "success": False,
                "error": str(e)
            }
            return False, f"Integration tests failed: {e}"
    
    async def run_unit_tests(self) -> Tuple[bool, str]:
        """Run unit tests if available."""
        console.print("[cyan]Running unit tests...[/cyan]")
        
        # Check if tests directory exists
        if not os.path.exists("tests"):
            self.results["unit_tests"] = {
                "success": True,
                "skipped": True,
                "reason": "No tests directory found"
            }
            return True, "No unit tests found (skipped)"
        
        try:
            # Run pytest
            result = subprocess.run(
                [PYTHON, "-m", "pytest", "tests/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            # Parse pytest output
            import re
            passed_match = re.search(r"(\d+) passed", output)
            failed_match = re.search(r"(\d+) failed", output)
            
            passed = int(passed_match.group(1)) if passed_match else 0
            failed = int(failed_match.group(1)) if failed_match else 0
            
            self.results["unit_tests"] = {
                "success": success,
                "passed": passed,
                "failed": failed
            }
            
            summary = f"Passed: {passed}, Failed: {failed}"
            return success, summary
            
        except subprocess.TimeoutExpired:
            self.results["unit_tests"] = {
                "success": False,
                "error": "Timeout"
            }
            return False, "Unit tests timed out"
        except Exception as e:
            self.results["unit_tests"] = {
                "success": False,
                "error": str(e)
            }
            return False, f"Unit tests failed: {e}"
    
    def create_summary_table(self) -> Table:
        """Create a summary table of all test results."""
        table = Table(title="Test Results Summary", show_header=True)
        table.add_column("Test Suite", style="cyan", width=20)
        table.add_column("Status", width=10)
        table.add_column("Details", style="dim")
        
        # Health Check
        health = self.results.get("health_check", {})
        if "error" in health:
            status = "❌ FAIL"
            details = health["error"]
        elif health.get("all_core_healthy"):
            status = "✅ PASS"
            details = "All core components healthy"
        else:
            status = "⚠️  WARN"
            details = "Some components unhealthy"
        table.add_row("Health Check", status, details)
        
        # Integration Tests
        integration = self.results.get("integration_tests", {})
        if integration.get("success"):
            status = "✅ PASS"
            details = f"Passed: {integration.get('passed', 0)}"
        else:
            status = "❌ FAIL"
            details = integration.get("error", f"Failed: {integration.get('failed', 0)}")
        table.add_row("Integration Tests", status, details)
        
        # Unit Tests
        unit = self.results.get("unit_tests", {})
        if unit.get("skipped"):
            status = "⏭️  SKIP"
            details = unit.get("reason", "Skipped")
        elif unit.get("success"):
            status = "✅ PASS"
            details = f"Passed: {unit.get('passed', 0)}"
        else:
            status = "❌ FAIL"
            details = unit.get("error", f"Failed: {unit.get('failed', 0)}")
        table.add_row("Unit Tests", status, details)
        
        return table
    
    async def run_all_tests(self):
        """Run all test suites."""
        self.start_time = time.time()
        
        # Header
        console.print(Panel.fit(
            "[bold cyan]CX Futurist AI - Comprehensive Test Suite[/bold cyan]\n" +
            f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            border_style="cyan"
        ))
        console.print()
        
        # Check dependencies
        console.print("[yellow]Checking dependencies...[/yellow]")
        if not await self.check_dependencies():
            console.print("[red]❌ Missing required dependencies[/red]")
            return False
        console.print("[green]✅ All dependencies installed[/green]")
        console.print()
        
        # Check if server is running
        console.print("[yellow]Checking if server is running...[/yellow]")
        if not await self.check_server_running():
            console.print("[red]❌ Server is not running![/red]")
            console.print("[yellow]Please start the server with: python -m src.main[/yellow]")
            return False
        console.print("[green]✅ Server is running[/green]")
        console.print()
        
        # Run tests with progress tracking
        all_passed = True
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            
            # Health Check
            task = progress.add_task("[cyan]System Health Check[/cyan]", total=1)
            success, summary = await self.run_health_check()
            all_passed &= success
            progress.update(task, completed=1)
            console.print(f"  → {summary}")
            console.print()
            
            # Integration Tests
            task = progress.add_task("[cyan]Integration Tests[/cyan]", total=1)
            success, summary = await self.run_integration_tests()
            all_passed &= success
            progress.update(task, completed=1)
            console.print(f"  → {summary}")
            console.print()
            
            # Unit Tests
            task = progress.add_task("[cyan]Unit Tests[/cyan]", total=1)
            success, summary = await self.run_unit_tests()
            # Don't fail overall if unit tests are skipped
            if not self.results.get("unit_tests", {}).get("skipped"):
                all_passed &= success
            progress.update(task, completed=1)
            console.print(f"  → {summary}")
            console.print()
        
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        # Summary
        console.print()
        console.print(self.create_summary_table())
        console.print()
        
        # Final verdict
        if all_passed:
            console.print(Panel.fit(
                "[bold green]✅ ALL TESTS PASSED![/bold green]\n" +
                f"Duration: {duration:.2f} seconds\n\n" +
                "[green]System is ready for deployment![/green]",
                border_style="green"
            ))
        else:
            console.print(Panel.fit(
                "[bold red]❌ SOME TESTS FAILED![/bold red]\n" +
                f"Duration: {duration:.2f} seconds\n\n" +
                "[red]Please fix the issues before deployment.[/red]",
                border_style="red"
            ))
        
        # Save results to file
        self.save_results()
        
        return all_passed
    
    def save_results(self):
        """Save test results to a JSON file."""
        results_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": self.end_time - self.start_time if self.end_time and self.start_time else 0,
            "results": self.results
        }
        
        with open(results_file, "w") as f:
            json.dump(report, f, indent=2)
        
        console.print(f"[dim]Results saved to: {results_file}[/dim]")


async def main():
    """Main entry point."""
    runner = TestRunner()
    success = await runner.run_all_tests()
    
    # Return appropriate exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Tests interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        sys.exit(1)