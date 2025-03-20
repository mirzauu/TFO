      
from pydantic import BaseModel, Field
from typing import Optional, List



class MarketTrend(BaseModel):
    trend: str = Field(..., description="Description of the market trend")
    impact: str = Field(..., description="Potential impact on the industry or business")
    confidence_level: Optional[float] = Field(None, description="Confidence level (0-1) indicating trend reliability")

class MarketAnalystDetails(BaseModel):
    industry_sector: str = Field(..., description="The industry sector analyzed")
    trends_summary: List[MarketTrend] = Field(default_factory=list, description="List of identified market trends")
    data_sources: Optional[List[str]] = Field(default_factory=list, description="Sources of the market analysis")

class MarketAnalystOutput(BaseModel):
    response: str = Field(..., description="Status message for market analysis")
    details: MarketAnalystDetails = Field(..., description="Detailed market trends analysis")



class SWOTFactor(BaseModel):
    name: str = Field(..., description="Name of the SWOT factor")
    description: str = Field(..., description="Detailed explanation of the factor")
    implications: Optional[str] = Field(None, description="Potential business implications")

class SWOTDetails(BaseModel):
    strengths: List[SWOTFactor] = Field(default_factory=list, description="Key strengths identified")
    weaknesses: List[SWOTFactor] = Field(default_factory=list, description="Key weaknesses identified")
    opportunities: List[SWOTFactor] = Field(default_factory=list, description="Potential opportunities")
    threats: List[SWOTFactor] = Field(default_factory=list, description="Potential threats")
    strategic_insights: str = Field(..., description="Overall SWOT insights and recommendations")

class SWOTAnalysisOutput(BaseModel):
    response: str = Field(..., description="Status message for SWOT analysis")
    details: SWOTDetails = Field(..., description="Comprehensive SWOT breakdown")


# 🏢 Competitor Analysis
class CompetitorStrategy(BaseModel):
    competitor_name: str = Field(..., description="Name of the competitor")
    differentiating_strategy: str = Field(..., description="Key strategy used by the competitor")
    market_positioning: Optional[str] = Field(None, description="How the competitor positions itself in the market")

class CompetitorAnalysisDetails(BaseModel):
    competitors: List[CompetitorStrategy] = Field(default_factory=list, description="Competitor strategies analyzed")
    recommendations: str = Field(..., description="Strategic moves based on competitor analysis")
    risk_factors: Optional[List[str]] = Field(default_factory=list, description="Potential risks in competing strategies")

class CompetitorAnalysisOutput(BaseModel):
    response: str = Field(..., description="Status message for competitor analysis")
    details: CompetitorAnalysisDetails = Field(..., description="Detailed competitor analysis insights")


# 💰 Pricing Strategy
class PricingFactor(BaseModel):
    factor: str = Field(..., description="A key element influencing pricing decisions")
    influence: str = Field(..., description="How this factor impacts pricing strategies")
    data_source: Optional[str] = Field(None, description="Source of the pricing factor data")

class PricingModelDetails(BaseModel):
    model_description: str = Field(..., description="Detailed overview of the pricing model")
    factors_considered: List[PricingFactor] = Field(default_factory=list, description="Key factors affecting pricing")
    pricing_strategy: str = Field(..., description="Suggested pricing strategy based on analysis")
    profitability_forecast: Optional[str] = Field(None, description="Estimated profitability impact of this model")

class PricingModelOutput(BaseModel):
    response: str = Field(..., description="Status message for pricing model generation")
    details: PricingModelDetails = Field(..., description="Comprehensive pricing strategy analysis")


# 🎤 Sales Pitch
class SalesPitchPoint(BaseModel):
    point: str = Field(..., description="A key persuasion point used in the pitch")
    supporting_evidence: Optional[str] = Field(None, description="Evidence or rationale supporting this point")

class SalesPitchDetails(BaseModel):
    target_demographic: str = Field(..., description="Intended audience for the pitch")
    pitch_content: str = Field(..., description="Full sales pitch text")
    key_persuasion_points: List[SalesPitchPoint] = Field(default_factory=list, description="Highlighted persuasion techniques")
    call_to_action: str = Field(..., description="Final call to action for the audience")
    estimated_conversion_rate: Optional[float] = Field(None, description="Predicted conversion rate impact (0-1)")

class SalesPitchOutput(BaseModel):
    response: str = Field(..., description="Status message for sales pitch creation")
    details: SalesPitchDetails = Field(..., description="Detailed sales pitch breakdown")

    