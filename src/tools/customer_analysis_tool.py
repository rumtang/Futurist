"""Customer analysis tools for behavior and expectation analysis."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from src.tools.base_tool import AnalysisToolBase, ToolResult


class BehaviorAnalyzer(AnalysisToolBase):
    """Analyzes customer behavior patterns and changes."""
    
    name: str = "behavior_analyzer"
    description: str = "Analyze customer behavior patterns, drivers, and barriers"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Behavior categories
        self.behavior_categories = {
            "digital_adoption": ["online_shopping", "mobile_usage", "app_engagement"],
            "communication": ["chat_preference", "video_calls", "async_messaging"],
            "purchase_patterns": ["impulse_buying", "research_intensive", "subscription_preference"],
            "loyalty_indicators": ["repeat_purchase", "referral_behavior", "brand_advocacy"]
        }
        
        # Driver categories
        self.driver_categories = [
            "convenience", "personalization", "value", "experience",
            "social_proof", "sustainability", "innovation", "trust"
        ]
    
    async def _arun(self, behaviors: List[Dict[str, Any]], **kwargs) -> ToolResult:
        """Analyze customer behaviors."""
        try:
            analysis = {
                "behavior_patterns": self._identify_patterns(behaviors),
                "drivers": self._analyze_drivers(behaviors),
                "barriers": self._identify_barriers(behaviors),
                "segments": self._segment_behaviors(behaviors),
                "evolution_timeline": self._create_evolution_timeline(behaviors)
            }
            
            # Calculate insights
            analysis["key_insights"] = self._generate_insights(analysis)
            
            return ToolResult(
                success=True,
                data=analysis,
                metadata={
                    "behaviors_analyzed": len(behaviors),
                    "patterns_found": len(analysis["behavior_patterns"])
                }
            )
            
        except Exception as e:
            logger.error(f"Behavior analysis error: {str(e)}")
            return ToolResult(
                success=False,
                error=f"Analysis failed: {str(e)}"
            )
    
    def _identify_patterns(self, behaviors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify patterns in customer behaviors."""
        patterns = []
        
        # Group behaviors by category
        categorized = {}
        for behavior in behaviors:
            category = self._categorize_behavior(behavior)
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(behavior)
        
        # Identify patterns within categories
        for category, category_behaviors in categorized.items():
            if len(category_behaviors) >= 2:
                pattern = {
                    "category": category,
                    "pattern_type": self._determine_pattern_type(category_behaviors),
                    "strength": self._calculate_pattern_strength(category_behaviors),
                    "behaviors": [b.get("behavior", b.get("name", "")) for b in category_behaviors],
                    "adoption_rate": sum(b.get("adoption_rate", 0.5) for b in category_behaviors) / len(category_behaviors)
                }
                patterns.append(pattern)
        
        return sorted(patterns, key=lambda x: x["strength"], reverse=True)
    
    def _analyze_drivers(self, behaviors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze what drives customer behaviors."""
        driver_scores = {driver: 0 for driver in self.driver_categories}
        driver_examples = {driver: [] for driver in self.driver_categories}
        
        for behavior in behaviors:
            # Simple keyword matching (would be more sophisticated in production)
            behavior_text = str(behavior).lower()
            
            for driver in self.driver_categories:
                if driver in behavior_text:
                    driver_scores[driver] += behavior.get("adoption_rate", 0.5)
                    driver_examples[driver].append(behavior.get("behavior", ""))
        
        # Create driver analysis
        drivers = []
        for driver, score in driver_scores.items():
            if score > 0:
                drivers.append({
                    "driver": driver,
                    "influence_score": round(score / len(behaviors), 3),
                    "examples": driver_examples[driver][:3],
                    "category": self._categorize_driver(driver)
                })
        
        return sorted(drivers, key=lambda x: x["influence_score"], reverse=True)
    
    def _identify_barriers(self, behaviors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify barriers to behavior adoption."""
        barriers = [
            {
                "barrier": "Technology complexity",
                "impact": "high",
                "affected_segments": ["baby_boomers", "non_tech_savvy"],
                "mitigation": "Simplified interfaces and guided experiences"
            },
            {
                "barrier": "Privacy concerns",
                "impact": "medium",
                "affected_segments": ["all"],
                "mitigation": "Transparent data practices and user control"
            },
            {
                "barrier": "Cost sensitivity",
                "impact": "medium",
                "affected_segments": ["value_seekers", "gen_z"],
                "mitigation": "Clear value proposition and flexible pricing"
            },
            {
                "barrier": "Habit inertia",
                "impact": "high",
                "affected_segments": ["gen_x", "baby_boomers"],
                "mitigation": "Gradual transition and incentives"
            }
        ]
        
        return barriers
    
    def _segment_behaviors(self, behaviors: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Segment behaviors by customer type."""
        segments = {
            "early_adopters": [],
            "mainstream": [],
            "laggards": []
        }
        
        for behavior in behaviors:
            adoption_rate = behavior.get("adoption_rate", 0.5)
            behavior_name = behavior.get("behavior", behavior.get("name", ""))
            
            if adoption_rate > 0.8:
                segments["mainstream"].append(behavior_name)
            elif adoption_rate > 0.6:
                segments["early_adopters"].append(behavior_name)
            else:
                segments["laggards"].append(behavior_name)
        
        return segments
    
    def _create_evolution_timeline(self, behaviors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create timeline of behavior evolution."""
        timeline = [
            {
                "period": "2020-2021",
                "key_shift": "Rapid digital adoption",
                "trigger": "COVID-19 pandemic",
                "behaviors": ["online shopping", "video calls", "contactless payments"]
            },
            {
                "period": "2022-2023",
                "key_shift": "Hybrid experiences",
                "trigger": "Post-pandemic normalization",
                "behaviors": ["BOPIS", "virtual consultations", "hybrid events"]
            },
            {
                "period": "2024-2025",
                "key_shift": "AI-powered personalization",
                "trigger": "AI maturity",
                "behaviors": ["AI assistants", "predictive services", "automated preferences"]
            }
        ]
        
        return timeline
    
    def _generate_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate key insights from analysis."""
        insights = []
        
        # Pattern insights
        if analysis["behavior_patterns"]:
            top_pattern = analysis["behavior_patterns"][0]
            insights.append(
                f"Strong {top_pattern['pattern_type']} pattern in {top_pattern['category']} "
                f"with {top_pattern['adoption_rate']:.0%} adoption"
            )
        
        # Driver insights
        if analysis["drivers"]:
            top_drivers = [d["driver"] for d in analysis["drivers"][:3]]
            insights.append(f"Key behavior drivers: {', '.join(top_drivers)}")
        
        # Barrier insights
        high_impact_barriers = [b["barrier"] for b in analysis["barriers"] if b["impact"] == "high"]
        if high_impact_barriers:
            insights.append(f"Critical barriers to address: {', '.join(high_impact_barriers)}")
        
        return insights
    
    def _categorize_behavior(self, behavior: Dict[str, Any]) -> str:
        """Categorize a behavior."""
        behavior_text = str(behavior).lower()
        
        for category, keywords in self.behavior_categories.items():
            if any(keyword in behavior_text for keyword in keywords):
                return category
        
        return "general"
    
    def _determine_pattern_type(self, behaviors: List[Dict[str, Any]]) -> str:
        """Determine the type of pattern."""
        # Simplified pattern detection
        adoption_rates = [b.get("adoption_rate", 0.5) for b in behaviors]
        
        if all(rate > 0.7 for rate in adoption_rates):
            return "convergence"
        elif max(adoption_rates) - min(adoption_rates) > 0.3:
            return "divergence"
        else:
            return "stable"
    
    def _calculate_pattern_strength(self, behaviors: List[Dict[str, Any]]) -> float:
        """Calculate pattern strength."""
        # Based on consistency and adoption
        adoption_rates = [b.get("adoption_rate", 0.5) for b in behaviors]
        avg_adoption = sum(adoption_rates) / len(adoption_rates)
        consistency = 1 - (max(adoption_rates) - min(adoption_rates))
        
        return round((avg_adoption + consistency) / 2, 3)
    
    def _categorize_driver(self, driver: str) -> str:
        """Categorize driver type."""
        driver_categories = {
            "functional": ["convenience", "value", "efficiency"],
            "emotional": ["experience", "personalization", "trust"],
            "social": ["social_proof", "sustainability", "innovation"]
        }
        
        for category, drivers in driver_categories.items():
            if driver in drivers:
                return category
        
        return "other"


class ExpectationPredictor(AnalysisToolBase):
    """Predicts future customer expectations based on current trends."""
    
    name: str = "expectation_predictor"
    description: str = "Predict evolving customer expectations and needs"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.expectation_categories = [
            "service_quality", "response_time", "personalization",
            "transparency", "sustainability", "innovation",
            "value", "convenience", "experience"
        ]
    
    async def _arun(self, 
                   current_behaviors: List[Dict[str, Any]],
                   current_expectations: List[Dict[str, Any]],
                   **kwargs) -> ToolResult:
        """Predict future expectations."""
        try:
            predictions = {
                "evolved_expectations": self._evolve_expectations(
                    current_behaviors, 
                    current_expectations
                ),
                "emerging_expectations": self._identify_emerging_expectations(
                    current_behaviors
                ),
                "expectation_trajectory": self._predict_trajectory(
                    current_expectations
                ),
                "readiness_assessment": self._assess_readiness(
                    current_expectations
                )
            }
            
            return ToolResult(
                success=True,
                data=predictions,
                metadata={
                    "prediction_confidence": 0.75,
                    "time_horizon": "12-24 months"
                }
            )
            
        except Exception as e:
            logger.error(f"Expectation prediction error: {str(e)}")
            return ToolResult(
                success=False,
                error=f"Prediction failed: {str(e)}"
            )
    
    def _evolve_expectations(self, 
                           behaviors: List[Dict[str, Any]], 
                           expectations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evolve current expectations based on behaviors."""
        evolved = []
        
        for expectation in expectations:
            # Calculate evolution factor based on related behaviors
            evolution_factor = self._calculate_evolution_factor(expectation, behaviors)
            
            evolved_expectation = expectation.copy()
            evolved_expectation["importance"] = min(
                1.0, 
                expectation.get("importance", 0.7) * (1 + evolution_factor)
            )
            evolved_expectation["evolution_stage"] = self._determine_evolution_stage(
                evolved_expectation["importance"]
            )
            evolved_expectation["timeframe"] = self._estimate_timeframe(evolution_factor)
            
            evolved.append(evolved_expectation)
        
        # Add behavior-driven expectations
        behavior_expectations = self._derive_expectations_from_behaviors(behaviors)
        evolved.extend(behavior_expectations)
        
        return sorted(evolved, key=lambda x: x.get("importance", 0), reverse=True)
    
    def _identify_emerging_expectations(self, behaviors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify new expectations emerging from behaviors."""
        emerging = [
            {
                "expectation": "Predictive personalization",
                "description": "AI anticipating needs before customers express them",
                "emergence_strength": 0.8,
                "driven_by": ["AI adoption", "data availability"],
                "timeframe": "6-12 months"
            },
            {
                "expectation": "Zero-friction experiences",
                "description": "Completely seamless interactions with no barriers",
                "emergence_strength": 0.75,
                "driven_by": ["mobile adoption", "authentication evolution"],
                "timeframe": "12-18 months"
            },
            {
                "expectation": "Ethical AI transparency",
                "description": "Clear explanation of AI decision-making",
                "emergence_strength": 0.7,
                "driven_by": ["AI regulation", "trust concerns"],
                "timeframe": "12-24 months"
            }
        ]
        
        return emerging
    
    def _predict_trajectory(self, expectations: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Predict trajectory of expectations over time."""
        trajectories = {
            "accelerating": [],
            "steady": [],
            "plateauing": []
        }
        
        for expectation in expectations:
            importance = expectation.get("importance", 0.7)
            gap = expectation.get("gap", 0.2)
            
            if gap > 0.3 and importance > 0.8:
                trajectory = "accelerating"
            elif importance > 0.6:
                trajectory = "steady"
            else:
                trajectory = "plateauing"
            
            trajectories[trajectory].append({
                "expectation": expectation.get("expectation", "Unknown"),
                "current_importance": importance,
                "projected_importance": self._project_importance(importance, trajectory),
                "timeline": "12 months"
            })
        
        return trajectories
    
    def _assess_readiness(self, expectations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess organizational readiness for future expectations."""
        readiness = {
            "overall_score": 0,
            "gap_analysis": [],
            "priority_areas": [],
            "investment_needs": []
        }
        
        total_gap = 0
        critical_gaps = []
        
        for expectation in expectations:
            gap = expectation.get("gap", 0)
            importance = expectation.get("importance", 0.5)
            
            if gap > 0.2:
                readiness["gap_analysis"].append({
                    "area": expectation.get("expectation", "Unknown"),
                    "gap_size": gap,
                    "criticality": "high" if importance > 0.8 else "medium"
                })
                
                if importance > 0.8:
                    critical_gaps.append(expectation)
            
            total_gap += gap * importance
        
        # Calculate overall readiness
        readiness["overall_score"] = round(1 - (total_gap / len(expectations)), 2)
        
        # Identify priority areas
        readiness["priority_areas"] = [
            gap.get("expectation", "Unknown") 
            for gap in sorted(critical_gaps, key=lambda x: x.get("gap", 0), reverse=True)[:3]
        ]
        
        return readiness
    
    def _calculate_evolution_factor(self, expectation: Dict[str, Any], 
                                  behaviors: List[Dict[str, Any]]) -> float:
        """Calculate how much an expectation will evolve."""
        # Simplified calculation based on behavior adoption
        related_behaviors = [
            b for b in behaviors 
            if any(keyword in str(b).lower() 
                  for keyword in str(expectation.get("expectation", "")).lower().split())
        ]
        
        if not related_behaviors:
            return 0.1  # Default evolution
        
        avg_adoption = sum(b.get("adoption_rate", 0.5) for b in related_behaviors) / len(related_behaviors)
        return min(0.5, avg_adoption * 0.3)
    
    def _determine_evolution_stage(self, importance: float) -> str:
        """Determine evolution stage of expectation."""
        if importance > 0.9:
            return "universal"
        elif importance > 0.7:
            return "mainstream"
        elif importance > 0.5:
            return "emerging"
        else:
            return "niche"
    
    def _estimate_timeframe(self, evolution_factor: float) -> str:
        """Estimate timeframe for expectation evolution."""
        if evolution_factor > 0.3:
            return "3-6 months"
        elif evolution_factor > 0.2:
            return "6-12 months"
        elif evolution_factor > 0.1:
            return "12-18 months"
        else:
            return "18-24 months"
    
    def _derive_expectations_from_behaviors(self, behaviors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Derive new expectations from behavior patterns."""
        derived = []
        
        # Check for high-adoption behaviors
        for behavior in behaviors:
            if behavior.get("adoption_rate", 0) > 0.8:
                derived.append({
                    "expectation": f"Enhanced {behavior.get('behavior', 'service')}",
                    "importance": 0.7,
                    "current_fulfillment": 0.5,
                    "gap": 0.2,
                    "derived_from": "behavior_pattern"
                })
        
        return derived[:3]  # Limit to top 3
    
    def _project_importance(self, current: float, trajectory: str) -> float:
        """Project future importance based on trajectory."""
        projections = {
            "accelerating": min(1.0, current * 1.3),
            "steady": min(1.0, current * 1.1),
            "plateauing": current
        }
        
        return round(projections.get(trajectory, current), 2)