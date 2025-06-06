"""Simple analysis endpoint for Cloud Run - no WebSocket dependency."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from loguru import logger
import asyncio
from datetime import datetime
import json
from typing import Optional, Dict, Any

from src.api.base_api import AnalysisRequest
from src.orchestrator.simple_orchestrator import SimpleOrchestrator

router = APIRouter()

# In-memory results storage (consider Redis for production)
analysis_results: Dict[str, Any] = {}


class SimpleStreamCallback:
    """Simple callback that just logs messages."""
    
    def __init__(self, request_id: str):
        self.request_id = request_id
        self.messages = []
    
    async def __call__(self, data):
        """Log the stream data."""
        self.messages.append(data)
        logger.info(f"[{self.request_id}] Stream: {data}")


@router.post("/simple")
async def run_simple_analysis(request: AnalysisRequest):
    """Run analysis synchronously and return complete results."""
    request_id = f"simple_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    logger.info(f"Starting simple analysis {request_id} for topic: {request.topic}")
    
    try:
        # Create a simple callback that just logs
        callback = SimpleStreamCallback(request_id)
        
        # Initialize orchestrator without WebSocket
        orchestrator = SimpleOrchestrator(stream_callback=callback)
        
        # Run the analysis and wait for completion
        result = await orchestrator.analyze_trend(
            topic=request.topic,
            depth=request.depth or "comprehensive"
        )
        
        # Store the result
        analysis_results[request_id] = {
            "request_id": request_id,
            "topic": request.topic,
            "status": "completed",
            "created_at": datetime.now().isoformat(),
            "duration_seconds": result.duration,
            "results": result.results,
            "agent_outputs": result.agent_outputs,
            "stream_messages": callback.messages
        }
        
        logger.info(f"Analysis {request_id} completed successfully in {result.duration:.2f} seconds")
        
        # Return the complete result
        return {
            "request_id": request_id,
            "status": "completed",
            "topic": request.topic,
            "results": result.results,
            "duration_seconds": result.duration,
            "details_url": f"/api/simple-analysis/{request_id}",
            "html_url": f"/api/simple-analysis/{request_id}/html"
        }
        
    except Exception as e:
        logger.error(f"Analysis {request_id} failed: {str(e)}", exc_info=True)
        
        # Store the error
        analysis_results[request_id] = {
            "request_id": request_id,
            "topic": request.topic,
            "status": "failed",
            "created_at": datetime.now().isoformat(),
            "error": str(e)
        }
        
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/simple/{request_id}")
async def get_simple_analysis_result(request_id: str):
    """Get analysis result as JSON."""
    if request_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_results[request_id]


@router.get("/simple/{request_id}/html")
async def get_simple_analysis_html(request_id: str):
    """Get analysis result as HTML page."""
    if request_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    result = analysis_results[request_id]
    
    # Generate HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CX Futurist AI - Analysis Results</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
            }}
            .header p {{
                margin: 10px 0 0 0;
                opacity: 0.9;
            }}
            .section {{
                background: white;
                padding: 25px;
                margin-bottom: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .section h2 {{
                color: #667eea;
                margin-top: 0;
                border-bottom: 2px solid #f0f0f0;
                padding-bottom: 10px;
            }}
            .insight, .recommendation {{
                background: #f8f9fa;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #667eea;
                border-radius: 5px;
            }}
            .agent-output {{
                background: #f0f0f0;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
                white-space: pre-wrap;
                font-family: monospace;
                font-size: 0.9em;
                max-height: 300px;
                overflow-y: auto;
            }}
            .metadata {{
                color: #666;
                font-size: 0.9em;
            }}
            .error {{
                background: #fee;
                color: #c00;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #c00;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>CX Futurist AI Analysis</h1>
            <p>Multi-Agent Analysis Results</p>
        </div>
    """
    
    if result["status"] == "completed":
        results = result.get("results", {})
        
        # Metadata section
        html_content += f"""
        <div class="section">
            <h2>Analysis Overview</h2>
            <div class="metadata">
                <p><strong>Topic:</strong> {result['topic']}</p>
                <p><strong>Request ID:</strong> {result['request_id']}</p>
                <p><strong>Created:</strong> {result['created_at']}</p>
                <p><strong>Duration:</strong> {result.get('duration_seconds', 0):.2f} seconds</p>
                <p><strong>Status:</strong> {result['status']}</p>
            </div>
        </div>
        """
        
        # Executive Summary
        if results.get("summary"):
            html_content += f"""
            <div class="section">
                <h2>Executive Summary</h2>
                <p>{results['summary']}</p>
            </div>
            """
        
        # Key Insights
        if results.get("key_insights"):
            html_content += """
            <div class="section">
                <h2>Key Insights</h2>
            """
            for i, insight in enumerate(results["key_insights"], 1):
                html_content += f'<div class="insight">{i}. {insight}</div>'
            html_content += "</div>"
        
        # Recommendations
        if results.get("recommendations"):
            html_content += """
            <div class="section">
                <h2>Strategic Recommendations</h2>
            """
            for i, rec in enumerate(results["recommendations"], 1):
                html_content += f'<div class="recommendation">{i}. {rec}</div>'
            html_content += "</div>"
        
        # Agent Outputs (collapsed by default)
        if result.get("agent_outputs"):
            html_content += """
            <div class="section">
                <h2>Detailed Agent Outputs</h2>
                <p style="color: #666;">The following shows the raw analysis from each AI agent:</p>
            """
            
            for agent_name, output in result["agent_outputs"].items():
                html_content += f"""
                <details>
                    <summary style="cursor: pointer; font-weight: bold; margin: 10px 0;">
                        {agent_name.replace('_', ' ').title()}
                    </summary>
                    <div class="agent-output">
                        {json.dumps(output, indent=2)}
                    </div>
                </details>
                """
            
            html_content += "</div>"
    
    else:
        # Error state
        html_content += f"""
        <div class="section">
            <h2>Analysis Failed</h2>
            <div class="error">
                <p><strong>Error:</strong> {result.get('error', 'Unknown error')}</p>
                <p><strong>Request ID:</strong> {result['request_id']}</p>
                <p><strong>Topic:</strong> {result['topic']}</p>
            </div>
        </div>
        """
    
    html_content += """
        <div class="section" style="text-align: center; color: #666;">
            <p>Generated by CX Futurist AI - Multi-Agent Analysis System</p>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@router.get("/simple")
async def list_simple_analyses(limit: int = 20):
    """List recent analyses."""
    analyses = list(analysis_results.values())
    analyses.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return analyses[:limit]


@router.delete("/simple/{request_id}")
async def delete_simple_analysis(request_id: str):
    """Delete an analysis result."""
    if request_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    del analysis_results[request_id]
    return {"message": "Analysis deleted", "request_id": request_id}