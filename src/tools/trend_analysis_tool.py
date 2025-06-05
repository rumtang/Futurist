"""Trend analysis tools for identifying and analyzing trends."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import math
from loguru import logger

from src.tools.base_tool import AnalysisToolBase, ToolResult


class TrendAnalysisTool(AnalysisToolBase):
    """Analyzes trend strength, trajectory, and interconnections."""
    
    name: str = "trend_analyzer"
    description: str = "Analyze trend strength, trajectory, lifecycle stage, and interconnections"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Trend lifecycle stages
        self.lifecycle_stages = [
            "innovation", "early_adoption", "early_majority", 
            "late_majority", "laggards", "decline"
        ]
        
        # Trajectory patterns
        self.trajectory_patterns = {
            "exponential": lambda x: x ** 2,
            "linear": lambda x: x,
            "logarithmic": lambda x: math.log(x + 1),
            "s_curve": lambda x: 1 / (1 + math.exp(-10 * (x - 0.5))),
            "cyclical": lambda x: 0.5 + 0.5 * math.sin(2 * math.pi * x)
        }
    
    async def _arun(self, signals: List[Dict[str, Any]], **kwargs) -> ToolResult:
        """Analyze trend signals."""
        try:
            analysis = {
                "analyzed_signals": [],
                "trend_clusters": [],
                "lifecycle_distribution": {},
                "trajectory_analysis": {},
                "convergence_points": []
            }
            
            # Analyze each signal
            for signal in signals:
                analyzed = await self._analyze_signal(signal)
                analysis["analyzed_signals"].append(analyzed)
            
            # Cluster related trends
            analysis["trend_clusters"] = self._cluster_trends(analysis["analyzed_signals"])
            
            # Analyze lifecycle distribution
            analysis["lifecycle_distribution"] = self._analyze_lifecycle_distribution(
                analysis["analyzed_signals"]
            )
            
            # Analyze trajectories
            analysis["trajectory_analysis"] = self._analyze_trajectories(
                analysis["analyzed_signals"]
            )
            
            # Find convergence points
            analysis["convergence_points"] = self._find_convergence_points(
                analysis["analyzed_signals"]
            )
            
            return ToolResult(
                success=True,
                data=analysis,
                metadata={
                    "signals_analyzed": len(signals),
                    "clusters_found": len(analysis["trend_clusters"])
                }
            )
            
        except Exception as e:
            logger.error(f"Trend analysis error: {str(e)}")
            return ToolResult(
                success=False,
                error=f"Analysis failed: {str(e)}"
            )
    
    async def _analyze_signal(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze individual trend signal."""
        analyzed = signal.copy()
        
        # Calculate trend strength
        strength = self._calculate_trend_strength(signal)
        analyzed["strength"] = strength
        
        # Determine lifecycle stage
        lifecycle = self._determine_lifecycle_stage(signal, strength)
        analyzed["lifecycle_stage"] = lifecycle
        
        # Predict trajectory
        trajectory = self._predict_trajectory(signal, strength)
        analyzed["trajectory"] = trajectory["pattern"]
        analyzed["momentum"] = trajectory["momentum"]
        
        # Estimate maturity timeline
        maturity = self._estimate_maturity_timeline(lifecycle, trajectory)
        analyzed["maturity_timeline"] = maturity
        
        # Add metadata
        analyzed["name"] = signal.get("title", "Unknown Trend")
        analyzed["confidence"] = self._calculate_confidence(signal)
        analyzed["impact_potential"] = self._assess_impact_potential(signal, strength)
        
        return analyzed
    
    def _calculate_trend_strength(self, signal: Dict[str, Any]) -> float:
        """Calculate overall trend strength from multiple factors."""
        factors = {
            "mention_frequency": min(signal.get("mentions", 1) / 10, 1.0) * 0.3,
            "source_diversity": min(len(signal.get("sources", [])) / 5, 1.0) * 0.2,
            "raw_strength": signal.get("raw_strength", 0.5) * 0.3,
            "category_relevance": 0.7 * 0.2  # Default relevance
        }
        
        # Time decay factor
        first_seen = signal.get("first_seen", "2024-01")
        try:
            first_date = datetime.strptime(first_seen, "%Y-%m")
            months_old = (datetime.now() - first_date).days / 30
            time_factor = 1.0 if months_old < 6 else 0.8 if months_old < 12 else 0.6
        except:
            time_factor = 0.8
        
        strength = sum(factors.values()) * time_factor
        return round(min(max(strength, 0.0), 1.0), 3)
    
    def _determine_lifecycle_stage(self, signal: Dict[str, Any], strength: float) -> str:
        """Determine which lifecycle stage the trend is in."""
        # Simple heuristic based on strength and other factors
        mentions = signal.get("mentions", 1)
        sources = len(signal.get("sources", []))
        
        if strength < 0.3:
            return "innovation"
        elif strength < 0.5 and mentions < 5:
            return "early_adoption"
        elif strength < 0.7 and sources > 3:
            return "early_majority"
        elif strength < 0.85:
            return "late_majority"
        elif strength >= 0.85:
            return "laggards"
        else:
            return "unknown"
    
    def _predict_trajectory(self, signal: Dict[str, Any], strength: float) -> Dict[str, Any]:
        """Predict trend trajectory pattern."""
        # Analyze historical data if available
        category = signal.get("category", "general")
        
        # Category-based trajectory patterns
        trajectory_map = {
            "technology": "exponential" if strength < 0.5 else "s_curve",
            "social_patterns": "s_curve",
            "consumer_behavior": "cyclical" if "seasonal" in signal.get("title", "").lower() else "s_curve",
            "economic_indicators": "linear",
            "regulatory_changes": "logarithmic"
        }
        
        pattern = trajectory_map.get(category, "linear")
        
        # Calculate momentum
        momentum = "accelerating" if strength > 0.6 else "steady" if strength > 0.3 else "emerging"
        
        return {
            "pattern": pattern,
            "momentum": momentum,
            "confidence": 0.7 if category in trajectory_map else 0.5
        }
    
    def _estimate_maturity_timeline(self, lifecycle: str, trajectory: Dict[str, Any]) -> Dict[str, str]:
        """Estimate timeline to reach maturity."""
        timelines = {
            "innovation": {
                "to_early_adoption": "3-6 months",
                "to_mainstream": "12-24 months",
                "to_maturity": "24-36 months"
            },
            "early_adoption": {
                "to_mainstream": "6-12 months",
                "to_maturity": "18-24 months"
            },
            "early_majority": {
                "to_maturity": "6-12 months"
            },
            "late_majority": {
                "to_maturity": "0-6 months"
            }
        }
        
        # Adjust based on trajectory momentum
        if trajectory["momentum"] == "accelerating":
            # Reduce timelines by 25%
            return timelines.get(lifecycle, {"status": "mature"})
        
        return timelines.get(lifecycle, {"status": "unknown"})
    
    def _assess_impact_potential(self, signal: Dict[str, Any], strength: float) -> str:
        """Assess the potential impact of the trend."""
        category = signal.get("category", "general")
        
        # Category impact weights
        impact_weights = {
            "technology": 0.9,
            "consumer_behavior": 0.8,
            "economic_indicators": 0.85,
            "social_patterns": 0.7,
            "regulatory_changes": 0.95
        }
        
        weight = impact_weights.get(category, 0.7)
        impact_score = strength * weight
        
        if impact_score > 0.8:
            return "transformative"
        elif impact_score > 0.6:
            return "high"
        elif impact_score > 0.4:
            return "medium"
        else:
            return "low"
    
    def _cluster_trends(self, analyzed_signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Cluster related trends together."""
        clusters = []
        clustered = set()
        
        for i, signal1 in enumerate(analyzed_signals):
            if i in clustered:
                continue
                
            cluster = {
                "core_trend": signal1["name"],
                "members": [signal1],
                "combined_strength": signal1["strength"],
                "categories": {signal1.get("category", "general")}
            }
            
            # Find related trends
            for j, signal2 in enumerate(analyzed_signals[i+1:], i+1):
                if j in clustered:
                    continue
                    
                # Check similarity (simplified)
                if (signal1.get("category") == signal2.get("category") or
                    any(word in signal2["name"].lower() 
                        for word in signal1["name"].lower().split())):
                    
                    cluster["members"].append(signal2)
                    cluster["combined_strength"] = max(
                        cluster["combined_strength"],
                        signal2["strength"]
                    )
                    cluster["categories"].add(signal2.get("category", "general"))
                    clustered.add(j)
            
            if len(cluster["members"]) > 1:
                cluster["categories"] = list(cluster["categories"])
                clusters.append(cluster)
        
        return sorted(clusters, key=lambda x: x["combined_strength"], reverse=True)
    
    def _analyze_lifecycle_distribution(self, analyzed_signals: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze distribution of trends across lifecycle stages."""
        distribution = {stage: 0 for stage in self.lifecycle_stages}
        
        for signal in analyzed_signals:
            stage = signal.get("lifecycle_stage", "unknown")
            if stage in distribution:
                distribution[stage] += 1
        
        return distribution
    
    def _analyze_trajectories(self, analyzed_signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trajectory patterns across all trends."""
        trajectories = {
            "patterns": {},
            "momentum_distribution": {
                "accelerating": 0,
                "steady": 0,
                "emerging": 0,
                "declining": 0
            }
        }
        
        for signal in analyzed_signals:
            pattern = signal.get("trajectory", "unknown")
            momentum = signal.get("momentum", "unknown")
            
            # Count patterns
            if pattern not in trajectories["patterns"]:
                trajectories["patterns"][pattern] = 0
            trajectories["patterns"][pattern] += 1
            
            # Count momentum
            if momentum in trajectories["momentum_distribution"]:
                trajectories["momentum_distribution"][momentum] += 1
        
        return trajectories
    
    def _find_convergence_points(self, analyzed_signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find points where multiple trends converge."""
        convergence_points = []
        
        # Look for high-strength trends in different categories
        high_strength = [s for s in analyzed_signals if s["strength"] > 0.7]
        
        for i, trend1 in enumerate(high_strength):
            for trend2 in high_strength[i+1:]:
                if trend1.get("category") != trend2.get("category"):
                    convergence_points.append({
                        "trends": [trend1["name"], trend2["name"]],
                        "categories": [trend1.get("category"), trend2.get("category")],
                        "combined_impact": trend1["impact_potential"],
                        "convergence_timeline": "6-12 months",
                        "opportunity": f"Integration of {trend1.get('category')} and {trend2.get('category')}"
                    })
        
        return convergence_points[:5]  # Top 5 convergence points


class WeakSignalDetector(AnalysisToolBase):
    """Detects weak signals that could become major trends."""
    
    name: str = "weak_signal_detector"
    description: str = "Detect weak signals with high future potential"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.signal_indicators = [
            "first_mover", "research_breakthrough", "regulatory_change",
            "demographic_shift", "technology_enabler", "social_movement"
        ]
    
    async def _arun(self, data: Dict[str, Any], **kwargs) -> ToolResult:
        """Detect weak signals from various data sources."""
        try:
            detected_signals = []
            
            # Analyze different data types
            if "search_results" in data:
                signals = self._detect_from_search(data["search_results"])
                detected_signals.extend(signals)
            
            if "social_data" in data:
                signals = self._detect_from_social(data["social_data"])
                detected_signals.extend(signals)
            
            if "research_papers" in data:
                signals = self._detect_from_research(data["research_papers"])
                detected_signals.extend(signals)
            
            # Score and rank signals
            scored_signals = self._score_signals(detected_signals)
            
            # Filter by potential
            high_potential = [s for s in scored_signals if s["future_potential"] > 0.7]
            
            return ToolResult(
                success=True,
                data={
                    "weak_signals": high_potential,
                    "total_detected": len(detected_signals),
                    "high_potential_count": len(high_potential)
                },
                metadata={"detection_timestamp": datetime.now().isoformat()}
            )
            
        except Exception as e:
            logger.error(f"Weak signal detection error: {str(e)}")
            return ToolResult(
                success=False,
                error=f"Detection failed: {str(e)}"
            )
    
    def _detect_from_search(self, search_data: List[Dict]) -> List[Dict[str, Any]]:
        """Detect signals from search results."""
        signals = []
        
        # Look for specific patterns in search results
        for result in search_data:
            signal_score = 0
            indicators = []
            
            content = result.get("content", "").lower()
            title = result.get("title", "").lower()
            
            # Check for weak signal indicators
            if any(word in content for word in ["breakthrough", "first", "novel", "unprecedented"]):
                signal_score += 0.3
                indicators.append("first_mover")
            
            if any(word in content for word in ["research", "study", "paper", "findings"]):
                signal_score += 0.2
                indicators.append("research_breakthrough")
            
            if signal_score > 0.4:
                signals.append({
                    "type": "search_signal",
                    "title": result.get("title"),
                    "signal_score": signal_score,
                    "indicators": indicators,
                    "source": result.get("source"),
                    "raw_data": result
                })
        
        return signals
    
    def _detect_from_social(self, social_data: List[Dict]) -> List[Dict[str, Any]]:
        """Detect signals from social media data."""
        # Placeholder for social signal detection
        return []
    
    def _detect_from_research(self, research_data: List[Dict]) -> List[Dict[str, Any]]:
        """Detect signals from research papers."""
        # Placeholder for research signal detection
        return []
    
    def _score_signals(self, signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score signals for future potential."""
        scored = []
        
        for signal in signals:
            # Calculate future potential score
            base_score = signal.get("signal_score", 0.5)
            
            # Boost score based on indicators
            indicator_boost = len(signal.get("indicators", [])) * 0.1
            
            # Time relevance boost
            time_boost = 0.2  # Assume recent
            
            future_potential = min(base_score + indicator_boost + time_boost, 1.0)
            
            signal["future_potential"] = round(future_potential, 3)
            scored.append(signal)
        
        return sorted(scored, key=lambda x: x["future_potential"], reverse=True)