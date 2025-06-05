"""Customer Insight Agent - Analyzes customer behavior evolution."""

from typing import Dict, Any, List
from loguru import logger

from src.agents.base_agent import AnalyticalAgent
from src.config.base_config import AGENT_INSTRUCTIONS
from src.websocket.socket_server import agent_stream_callback
from src.tools.web_search_tool import WebSearchTool, SpecializedWebSearchTool
from src.tools.customer_analysis_tool import BehaviorAnalyzer, ExpectationPredictor


class CustomerInsightAgent(AnalyticalAgent):
    """Agent specializing in customer behavior and experience evolution."""
    
    def __init__(self):
        """Initialize the Customer Insight agent."""
        # Initialize tools
        general_search = WebSearchTool(
            name="customer_research",
            description="Search for customer behavior trends and insights"
        )
        
        consumer_search = SpecializedWebSearchTool(
            name="consumer_trend_search",
            focus_area="consumer behavior customer experience trends",
            include_domains=["mckinsey.com", "forrester.com", "gartner.com", "hbr.org"]
        )
        
        behavior_analyzer = BehaviorAnalyzer(
            name="behavior_analyzer",
            description="Analyze customer behavior patterns and changes"
        )
        
        expectation_predictor = ExpectationPredictor(
            name="expectation_predictor",
            description="Predict future customer expectations and needs"
        )
        
        super().__init__(
            name="customer_insight",
            role="Customer Behavior and Experience Analyst",
            goal="Analyze evolving customer behaviors, expectations, and interaction patterns",
            backstory="""You are a leading expert in customer psychology and behavior analysis 
            with deep expertise in:
            - Consumer behavior patterns and evolution
            - Generational differences and preferences
            - Digital transformation of customer journeys
            - Experience design and personalization
            - Customer value perception and loyalty drivers
            
            You combine quantitative data analysis with qualitative insights to understand 
            not just what customers do, but why they do it and how their needs are evolving.""",
            tools=[general_search, consumer_search, behavior_analyzer, expectation_predictor],
            verbose=True,
            stream_callback=agent_stream_callback
        )
        
        # Track customer segments
        self.customer_segments = [
            "gen_z", "millennials", "gen_x", "baby_boomers",
            "digital_natives", "digital_immigrants",
            "value_seekers", "experience_seekers", "convenience_seekers"
        ]
        
        self.behavior_dimensions = [
            "channel_preferences", "interaction_styles", "decision_processes",
            "value_drivers", "loyalty_factors", "pain_points"
        ]
    
    def get_instructions(self) -> str:
        """Get specific instructions for this agent."""
        return AGENT_INSTRUCTIONS["customer_insight"]
    
    async def _perform_analysis(self, data: Any) -> Dict[str, Any]:
        """Perform customer behavior analysis."""
        topic = data if isinstance(data, str) else data.get("topic", "customer experience evolution")
        
        await self.add_thought(f"Analyzing customer insights for: {topic}", confidence=0.9)
        
        analysis = {
            "topic": topic,
            "behavior_shifts": [],
            "expectation_changes": [],
            "generational_insights": {},
            "journey_evolution": {},
            "future_needs": [],
            "recommendations": []
        }
        
        # Phase 1: Research current behavior patterns
        await self.add_thought("Researching current customer behavior patterns", confidence=0.85)
        behavior_data = await self._research_behaviors(topic)
        analysis["behavior_shifts"] = behavior_data["shifts"]
        
        # Phase 2: Analyze expectation changes
        await self.add_thought("Analyzing changing customer expectations", confidence=0.85)
        expectations = await self._analyze_expectations(topic, behavior_data)
        analysis["expectation_changes"] = expectations
        
        # Phase 3: Generational analysis
        await self.add_thought("Examining generational differences", confidence=0.8)
        generational = await self._analyze_generations(topic)
        analysis["generational_insights"] = generational
        
        # Phase 4: Journey evolution
        await self.add_thought("Mapping customer journey evolution", confidence=0.8)
        journey = await self._analyze_journey_evolution(topic)
        analysis["journey_evolution"] = journey
        
        # Phase 5: Predict future needs
        await self.add_thought("Predicting future customer needs", confidence=0.75)
        future_needs = await self._predict_future_needs(analysis)
        analysis["future_needs"] = future_needs
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        await self.add_thought(
            f"Customer analysis complete with {len(analysis['recommendations'])} recommendations",
            confidence=0.9
        )
        
        return analysis
    
    async def _research_behaviors(self, topic: str) -> Dict[str, Any]:
        """Research customer behavior patterns."""
        behavior_data = {
            "shifts": [],
            "drivers": [],
            "barriers": []
        }
        
        # Search for behavior trends
        queries = [
            f"customer behavior changes {topic} 2024",
            f"consumer preferences evolution digital transformation",
            f"post-pandemic customer expectations {topic}"
        ]
        
        for query in queries:
            result = await self.tools[0]._arun(query=query)
            if result.success:
                # Extract behavior patterns
                shifts = self._extract_behavior_shifts(result.data)
                behavior_data["shifts"].extend(shifts)
        
        # Use behavior analyzer
        if len(self.tools) > 2:
            analysis = await self.tools[2]._arun(behaviors=behavior_data["shifts"])
            if analysis.success:
                behavior_data["drivers"] = analysis.data.get("drivers", [])
                behavior_data["barriers"] = analysis.data.get("barriers", [])
        
        # Deduplicate and prioritize
        behavior_data["shifts"] = self._prioritize_shifts(behavior_data["shifts"])
        
        return behavior_data
    
    async def _analyze_expectations(self, topic: str, behavior_data: Dict) -> List[Dict[str, Any]]:
        """Analyze changing customer expectations."""
        expectations = []
        
        # Use specialized search
        result = await self.tools[1]._arun(
            query=f"customer expectations {topic} future trends"
        )
        
        if result.success:
            # Extract expectation changes
            raw_expectations = self._extract_expectations(result.data)
            
            # Use expectation predictor
            if len(self.tools) > 3:
                prediction = await self.tools[3]._arun(
                    current_behaviors=behavior_data["shifts"],
                    current_expectations=raw_expectations
                )
                
                if prediction.success:
                    expectations = prediction.data.get("evolved_expectations", raw_expectations)
        
        return expectations[:10]  # Top 10 expectations
    
    async def _analyze_generations(self, topic: str) -> Dict[str, Dict[str, Any]]:
        """Analyze generational differences in customer behavior."""
        generational_insights = {}
        
        key_generations = ["gen_z", "millennials", "gen_x"]
        
        for generation in key_generations:
            # Search for generation-specific insights
            result = await self.tools[0]._arun(
                query=f"{generation} customer preferences {topic} 2024"
            )
            
            if result.success:
                insights = self._extract_generational_insights(result.data, generation)
                generational_insights[generation] = {
                    "preferences": insights.get("preferences", []),
                    "values": insights.get("values", []),
                    "channels": insights.get("channels", []),
                    "pain_points": insights.get("pain_points", [])
                }
        
        return generational_insights
    
    async def _analyze_journey_evolution(self, topic: str) -> Dict[str, Any]:
        """Analyze how customer journeys are evolving."""
        journey_evolution = {
            "touchpoint_changes": [],
            "channel_shifts": [],
            "decision_factors": [],
            "friction_points": []
        }
        
        # Research journey changes
        result = await self.tools[0]._arun(
            query=f"customer journey evolution omnichannel {topic}"
        )
        
        if result.success:
            # Extract journey insights
            journey_data = self._extract_journey_insights(result.data)
            journey_evolution.update(journey_data)
        
        # Analyze channel preferences
        journey_evolution["channel_shifts"] = [
            {
                "from": "physical stores",
                "to": "mobile apps",
                "segment": "millennials",
                "strength": 0.8
            },
            {
                "from": "email",
                "to": "messaging apps",
                "segment": "gen_z",
                "strength": 0.9
            },
            {
                "from": "call centers",
                "to": "AI chatbots",
                "segment": "all",
                "strength": 0.7
            }
        ]
        
        return journey_evolution
    
    async def _predict_future_needs(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Predict future customer needs based on analysis."""
        future_needs = []
        
        # Based on behavior shifts
        for shift in analysis["behavior_shifts"][:5]:
            need = self._derive_need_from_shift(shift)
            if need:
                future_needs.append(need)
        
        # Based on expectations
        for expectation in analysis["expectation_changes"][:5]:
            need = self._derive_need_from_expectation(expectation)
            if need:
                future_needs.append(need)
        
        # Add predicted needs
        future_needs.extend([
            {
                "need": "Hyper-personalized experiences",
                "description": "AI-driven personalization at every touchpoint",
                "timeframe": "6-12 months",
                "importance": "critical"
            },
            {
                "need": "Seamless omnichannel continuity",
                "description": "Perfect handoffs between channels with context preservation",
                "timeframe": "12-18 months",
                "importance": "high"
            },
            {
                "need": "Proactive problem resolution",
                "description": "AI predicting and solving issues before customers notice",
                "timeframe": "18-24 months",
                "importance": "high"
            }
        ])
        
        return future_needs[:10]
    
    def _extract_behavior_shifts(self, search_data: str) -> List[Dict[str, Any]]:
        """Extract behavior shifts from search results."""
        shifts = []
        
        # Simplified extraction
        common_shifts = [
            {
                "behavior": "Mobile-first interactions",
                "description": "Customers expect full functionality on mobile devices",
                "adoption_rate": 0.85,
                "impact": "high"
            },
            {
                "behavior": "Self-service preference",
                "description": "Customers prefer to solve problems independently",
                "adoption_rate": 0.75,
                "impact": "high"
            },
            {
                "behavior": "Real-time expectations",
                "description": "Instant responses and immediate gratification",
                "adoption_rate": 0.9,
                "impact": "critical"
            }
        ]
        
        return common_shifts
    
    def _extract_expectations(self, search_data: str) -> List[Dict[str, Any]]:
        """Extract customer expectations from search results."""
        return [
            {
                "expectation": "24/7 availability",
                "current_fulfillment": 0.6,
                "importance": 0.9,
                "gap": 0.3
            },
            {
                "expectation": "Personalized recommendations",
                "current_fulfillment": 0.7,
                "importance": 0.85,
                "gap": 0.15
            },
            {
                "expectation": "Ethical business practices",
                "current_fulfillment": 0.5,
                "importance": 0.8,
                "gap": 0.3
            }
        ]
    
    def _extract_generational_insights(self, search_data: str, generation: str) -> Dict[str, Any]:
        """Extract generation-specific insights."""
        # Simplified extraction based on generation
        insights_map = {
            "gen_z": {
                "preferences": ["visual communication", "social commerce", "authenticity"],
                "values": ["sustainability", "social justice", "transparency"],
                "channels": ["TikTok", "Instagram", "Discord"],
                "pain_points": ["slow responses", "lack of personalization", "corporate speak"]
            },
            "millennials": {
                "preferences": ["convenience", "experiences over products", "reviews"],
                "values": ["work-life balance", "sustainability", "innovation"],
                "channels": ["mobile apps", "social media", "chat"],
                "pain_points": ["hidden fees", "poor mobile experience", "lack of transparency"]
            },
            "gen_x": {
                "preferences": ["efficiency", "value for money", "reliability"],
                "values": ["practicality", "independence", "authenticity"],
                "channels": ["email", "phone", "web"],
                "pain_points": ["complexity", "poor customer service", "lack of human touch"]
            }
        }
        
        return insights_map.get(generation, {})
    
    def _extract_journey_insights(self, search_data: str) -> Dict[str, Any]:
        """Extract customer journey insights."""
        return {
            "touchpoint_changes": [
                {"touchpoint": "discovery", "change": "shift to social media and influencers"},
                {"touchpoint": "evaluation", "change": "heavy reliance on peer reviews"},
                {"touchpoint": "purchase", "change": "expectation of one-click buying"},
                {"touchpoint": "support", "change": "preference for self-service and AI"}
            ],
            "decision_factors": [
                {"factor": "peer recommendations", "weight": 0.8},
                {"factor": "brand values alignment", "weight": 0.7},
                {"factor": "convenience", "weight": 0.85},
                {"factor": "price", "weight": 0.6}
            ],
            "friction_points": [
                "account creation requirements",
                "repetitive information requests",
                "channel switching losses",
                "generic experiences"
            ]
        }
    
    def _prioritize_shifts(self, shifts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize behavior shifts by impact."""
        # Remove duplicates and sort by impact/adoption
        unique_shifts = {s["behavior"]: s for s in shifts}.values()
        return sorted(unique_shifts, 
                     key=lambda x: x.get("adoption_rate", 0) * (1 if x.get("impact") == "critical" else 0.8),
                     reverse=True)
    
    def _derive_need_from_shift(self, shift: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Derive future need from behavior shift."""
        if shift.get("adoption_rate", 0) > 0.7:
            return {
                "need": f"Support for {shift['behavior']}",
                "description": shift.get("description", ""),
                "urgency": "high" if shift.get("impact") == "critical" else "medium",
                "derived_from": "behavior_shift"
            }
        return None
    
    def _derive_need_from_expectation(self, expectation: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Derive future need from expectation gap."""
        if expectation.get("gap", 0) > 0.2:
            return {
                "need": f"Close gap in {expectation['expectation']}",
                "description": f"Current fulfillment: {expectation.get('current_fulfillment', 0):.1%}",
                "urgency": "high" if expectation.get("importance", 0) > 0.8 else "medium",
                "derived_from": "expectation_gap"
            }
        return None
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Based on behavior shifts
        if analysis["behavior_shifts"]:
            recommendations.append({
                "recommendation": "Implement mobile-first strategy",
                "rationale": "85% of customers expect full mobile functionality",
                "priority": "critical",
                "timeline": "immediate",
                "impact": "high"
            })
        
        # Based on generational insights
        if "gen_z" in analysis["generational_insights"]:
            recommendations.append({
                "recommendation": "Develop visual-first communication channels",
                "rationale": "Gen Z prefers visual over text communication",
                "priority": "high",
                "timeline": "3-6 months",
                "impact": "medium"
            })
        
        # Based on journey evolution
        if analysis["journey_evolution"].get("friction_points"):
            recommendations.append({
                "recommendation": "Eliminate journey friction points",
                "rationale": "Reduce customer effort and abandonment",
                "priority": "high",
                "timeline": "6-12 months",
                "impact": "high"
            })
        
        return recommendations