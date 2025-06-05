"""Trend Scanner Agent - Simplified implementation."""

from typing import Dict, Any, List, Optional
import json
from enum import Enum
from loguru import logger

from src.agents.simple_agent import ResearchSimpleAgent
from src.config.base_config import settings, AGENT_INSTRUCTIONS


class SignalStrength(Enum):
    """Enum for signal strength classification."""
    WEAK = "weak"
    EMERGING = "emerging"
    STRENGTHENING = "strengthening"
    STRONG = "strong"
    MAINSTREAM = "mainstream"


class SimpleTrendScannerAgent(ResearchSimpleAgent):
    """Agent specializing in identifying and tracking weak signals and emerging trends."""
    
    def __init__(self, stream_callback: Optional[callable] = None):
        super().__init__(
            name="Trend_Scanner",
            role="Emerging Trends and Weak Signal Scanner",
            goal="Identify weak signals and emerging patterns that will shape future customer experiences",
            backstory="""You are a pattern recognition specialist with expertise in identifying 
            weak signals before they become mainstream trends. You have a unique ability to 
            connect disparate data points and see patterns others miss. Your track record 
            includes early identification of major shifts in consumer behavior and technology adoption.""",
            model="gpt-4.1-mini",
            temperature=0.1,  # Slightly higher for creative pattern recognition
            stream_callback=stream_callback,
            research_depth="exhaustive"
        )
        
        # Signal detection parameters
        self.signal_sources = [
            "Academic research papers",
            "Patent filings",
            "Startup activity",
            "Social media conversations",
            "Industry reports",
            "Government policies",
            "Cultural movements",
            "Technology forums"
        ]
        
        # Pattern recognition framework
        self.pattern_types = {
            "convergence": "Multiple trends coming together",
            "divergence": "Splitting or fragmentation of existing patterns",
            "acceleration": "Rapid increase in adoption or intensity",
            "reversal": "Opposite direction from current trends",
            "emergence": "Completely new phenomena",
            "recurrence": "Historical patterns repeating"
        }
    
    def get_instructions(self) -> str:
        """Get specific instructions for the Trend Scanner agent."""
        return AGENT_INSTRUCTIONS["trend_scanner"]
    
    async def scan_for_signals(self, domains: List[str], timeframe: str = "last_month") -> Dict[str, Any]:
        """Scan multiple domains for weak signals and emerging patterns."""
        await self.add_thought(
            f"Initiating comprehensive signal scan across {len(domains)} domains",
            confidence=0.95,
            reasoning=[
                "Setting up multi-domain scanning parameters",
                "Calibrating signal detection thresholds",
                "Preparing pattern recognition algorithms"
            ]
        )
        
        signals = {}
        
        for domain in domains:
            prompt = f"""Scan for weak signals and emerging patterns in {domain} over the {timeframe}:

Sources to consider: {', '.join(self.signal_sources)}

For each signal found, provide:
1. Signal description and source
2. Current strength (weak/emerging/strengthening/strong)
3. Pattern type ({', '.join(self.pattern_types.keys())})
4. Supporting evidence (with sources)
5. Potential evolution trajectory
6. CX implications if signal strengthens
7. Confidence level in detection

THOUGHT: Look for non-obvious connections and outliers.
CONFIDENCE: Be conservative with signal validation."""
            
            response = await self.think(prompt)
            signals[domain] = response
            
            # Stream progress update
            await self.add_thought(
                f"Completed signal scan for {domain}",
                confidence=0.9
            )
        
        return {
            "domains": domains,
            "timeframe": timeframe,
            "signals": signals,
            "agent": self.name,
            "scan_type": "comprehensive"
        }
    
    async def analyze_signal_evolution(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how a specific signal might evolve over time."""
        await self.add_thought(
            f"Analyzing evolution trajectory for signal: {signal.get('name', 'Unknown')}",
            confidence=0.85
        )
        
        prompt = f"""Analyze the evolution trajectory of this signal:

Signal: {json.dumps(signal, indent=2)}

Provide:
1. Current state assessment
2. Evolution scenarios (pessimistic, realistic, optimistic)
3. Key inflection points to watch
4. Amplifying factors (what could accelerate this)
5. Dampening factors (what could slow/stop this)
6. Cross-domain impacts
7. Timeline with probability milestones

THOUGHT: Consider both linear and non-linear evolution paths.
CONFIDENCE: Assign probabilities to each scenario."""
        
        response = await self.think(prompt)
        
        # Collaborate with other agents for deeper analysis
        await self.collaborate_with(
            "Tech_Impact_Agent",
            "Analyzing technology factors affecting signal evolution",
            signal
        )
        
        return {
            "signal": signal,
            "evolution_analysis": response,
            "agent": self.name,
            "analysis_depth": "comprehensive"
        }
    
    async def find_pattern_connections(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find connections and relationships between multiple patterns."""
        await self.add_thought(
            f"Searching for connections between {len(patterns)} patterns",
            confidence=0.8,
            reasoning=[
                "Mapping pattern characteristics",
                "Identifying common drivers",
                "Looking for causal relationships"
            ]
        )
        
        prompt = f"""Find connections between these patterns:

Patterns: {json.dumps(patterns, indent=2)}

Analyze:
1. Direct connections (clear cause-effect)
2. Indirect relationships (shared drivers)
3. Reinforcing loops (patterns that amplify each other)
4. Conflicting dynamics (patterns that oppose each other)
5. Emergent possibilities (what new patterns might emerge)
6. System-level impacts

Create a connection map with strength indicators.

THOUGHT: Think in terms of complex systems and feedback loops.
CONFIDENCE: Rate the strength of each connection found."""
        
        response = await self.think(prompt)
        
        return {
            "patterns": patterns,
            "connections": response,
            "agent": self.name,
            "analysis_type": "pattern_synthesis"
        }
    
    async def assess_signal_strength(self, signal: Dict[str, Any], 
                                   criteria: Dict[str, float] = None) -> Dict[str, Any]:
        """Assess the strength of a signal using multiple criteria."""
        if criteria is None:
            criteria = {
                "frequency": 0.2,      # How often the signal appears
                "distribution": 0.2,   # How widely it's distributed
                "acceleration": 0.2,   # Rate of change
                "impact_potential": 0.2,  # Potential impact if realized
                "credibility": 0.2    # Source credibility
            }
        
        await self.add_thought(
            "Performing multi-criteria signal strength assessment",
            confidence=0.9
        )
        
        prompt = f"""Assess the strength of this signal using weighted criteria:

Signal: {json.dumps(signal, indent=2)}

Criteria weights: {json.dumps(criteria, indent=2)}

For each criterion:
1. Score (0-100)
2. Evidence supporting the score
3. Key indicators used

Calculate:
- Individual criterion scores
- Weighted overall strength score
- Classification: {', '.join([s.value for s in SignalStrength])}
- Confidence in assessment

THOUGHT: Be rigorous in scoring methodology.
CONFIDENCE: Indicate measurement reliability."""
        
        response = await self.think(prompt)
        
        return {
            "signal": signal,
            "assessment": response,
            "criteria": criteria,
            "agent": self.name
        }
    
    async def generate_trend_report(self, focus_area: str, 
                                  horizon: str = "18_months") -> Dict[str, Any]:
        """Generate a comprehensive trend report for a specific area."""
        await self.add_thought(
            f"Generating comprehensive trend report for {focus_area}",
            confidence=0.85,
            reasoning=[
                "Synthesizing detected signals",
                "Analyzing pattern interactions",
                "Projecting future states"
            ]
        )
        
        # First scan for current signals
        signals_prompt = f"""Identify current signals and trends in {focus_area}:

Categories:
- Technology enablers
- Behavioral shifts  
- Cultural movements
- Economic factors
- Regulatory changes
- Environmental pressures

Classify by strength and trajectory."""
        
        signals_response = await self.think(signals_prompt)
        
        # Then create projections
        projection_prompt = f"""Based on identified signals, project the {focus_area} landscape in {horizon}:

Include:
1. Dominant trends by then
2. Emerging wildcards
3. Convergence scenarios
4. Disruption possibilities
5. Key uncertainties
6. Strategic implications

THOUGHT: Balance trend extrapolation with discontinuous change.
CONFIDENCE: Provide confidence ranges for projections."""
        
        projection_response = await self.think(projection_prompt)
        
        return {
            "focus_area": focus_area,
            "horizon": horizon,
            "current_signals": signals_response,
            "projections": projection_response,
            "agent": self.name,
            "report_type": "trend_synthesis"
        }
    
    async def scan_adoption_patterns(self, technology: str, focus_areas: List[str] = None) -> Dict[str, Any]:
        """Scan for adoption patterns of a specific technology."""
        await self.add_thought(
            f"Scanning adoption patterns for {technology}",
            confidence=0.85
        )
        
        focus_areas = focus_areas or ["enterprise", "consumer", "developer"]
        
        prompt = f"""Scan for adoption patterns of {technology} across these focus areas: {', '.join(focus_areas)}

For each focus area, identify:
1. Current adoption level (percentage/stage)
2. Adoption velocity (accelerating/steady/slowing)
3. Key adopter segments
4. Barriers to adoption
5. Enablers and catalysts
6. Geographic patterns
7. Use case evolution
8. Network effects observed

Pattern Analysis:
- Adoption curve stage (innovators/early adopters/early majority/etc)
- Comparison to similar technology adoptions
- Tipping point indicators
- Critical mass requirements

Future Projection:
- Expected adoption timeline
- Potential adoption ceiling
- Disruption scenarios

THOUGHT: Look for both obvious and subtle adoption signals.
CONFIDENCE: Base confidence on data availability and pattern clarity."""
        
        response = await self.think(prompt)
        
        return {
            "technology": technology,
            "focus_areas": focus_areas,
            "adoption_analysis": response,
            "agent": self.name,
            "scan_type": "adoption_patterns"
        }