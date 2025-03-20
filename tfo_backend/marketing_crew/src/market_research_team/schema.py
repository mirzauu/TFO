      
from pydantic import BaseModel, Field
from typing import Optional, List

class ReviewInsight(BaseModel):
    competitor_name: str = Field(..., description="Name of the competitor")
    differentiating_strategy: str = Field(..., description="Key strategy used by the competitor")
    market_positioning: Optional[str] = Field(None, description="How the competitor positions itself in the market")

class ReviewAnalysisDetails(BaseModel):
    competitors: List[ReviewInsight] = Field(default_factory=list, description="Competitor strategies analyzed")
    recommendations: str = Field(..., description="Strategic moves based on competitor analysis")
    risk_factors: Optional[List[str]] = Field(default_factory=list, description="Potential risks in competing strategies")

class ReviewAnalysisOutput(BaseModel):
    response: str = Field(..., description="Status message for competitor analysis")
    details: ReviewAnalysisDetails = Field(..., description="Detailed competitor analysis insights")


class SurveyQuestion(BaseModel):
    question: str = Field(..., description="Survey question")
    question_type: str = Field(..., description="Type of question (e.g., Multiple Choice, Open-Ended, Likert Scale)")

class SurveyDetails(BaseModel):
    topic: str = Field(..., description="The focus of the survey")
    target_audience: str = Field(..., description="Target respondents (e.g., Existing Customers, Prospective Buyers)")
    questions: List[SurveyQuestion] = Field(default_factory=list, description="List of survey questions")
    recommendations: Optional[str] = Field(None, description="Product or service recommendations based on survey analysis")

class SurveyOutput(BaseModel):
    response: str = Field(..., description="Status message for survey design and analysis")
    details: SurveyDetails = Field(..., description="Finalized survey template and analysis results")


class TrendInsight(BaseModel):
    trend: str = Field(..., description="Description of the market trend")
    impact: str = Field(..., description="Potential impact on the industry or business")
    confidence_level: Optional[float] = Field(None, description="Confidence level (0-1) indicating trend reliability")

class TrendSpotterDetails(BaseModel):
    industry_sector: str = Field(..., description="The industry sector analyzed")
    trends_summary: List[TrendInsight] = Field(default_factory=list, description="List of identified market trends")
    data_sources: Optional[List[str]] = Field(default_factory=list, description="Sources of the market analysis")

class TrendSpotterOutput(BaseModel):
    response: str = Field(..., description="Status message for market analysis")
    details: TrendSpotterDetails = Field(..., description="Detailed market trends analysis")

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

class DemographicBreakdown(BaseModel):
    point: str = Field(..., description="A key persuasion point used in the pitch")
    supporting_evidence: Optional[str] = Field(None, description="Evidence or rationale supporting this point")

class DemographicSpecialistDetails(BaseModel):
    target_demographic: str = Field(..., description="Intended audience for the pitch")
    pitch_content: str = Field(..., description="Full sales pitch text")
    key_persuasion_points: List[DemographicBreakdown] = Field(default_factory=list, description="Highlighted persuasion techniques")
    call_to_action: str = Field(..., description="Final call to action for the audience")
    estimated_conversion_rate: Optional[float] = Field(None, description="Predicted conversion rate impact (0-1)")

class DemographicSpecialistOutput(BaseModel):
    response: str = Field(..., description="Status message for sales pitch creation")
    details: DemographicSpecialistDetails = Field(..., description="Detailed sales pitch breakdown")


class CustomerPersona(BaseModel):
    point: str = Field(..., description="A key persuasion point used in the pitch")
    supporting_evidence: Optional[str] = Field(None, description="Evidence or rationale supporting this point")

class PersonaCreationDetails(BaseModel):
    target_demographic: str = Field(..., description="Intended audience for the pitch")
    pitch_content: str = Field(..., description="Full sales pitch text")
    key_persuasion_points: List[CustomerPersona] = Field(default_factory=list, description="Highlighted persuasion techniques")
    call_to_action: str = Field(..., description="Final call to action for the audience")
    estimated_conversion_rate: Optional[float] = Field(None, description="Predicted conversion rate impact (0-1)")

class PersonaCreationOutput(BaseModel):
    response: str = Field(..., description="Status message for sales pitch creation")
    details: PersonaCreationDetails = Field(..., description="Detailed sales pitch breakdown")

class GeoMarketInsight(BaseModel):
    trend: str = Field(..., description="Description of the market trend")
    impact: str = Field(..., description="Potential impact on the industry or business")
    confidence_level: Optional[float] = Field(None, description="Confidence level (0-1) indicating trend reliability")

class GeoMarketAnalysisDetails(BaseModel):
    industry_sector: str = Field(..., description="The industry sector analyzed")
    trends_summary: List[GeoMarketInsight] = Field(default_factory=list, description="List of identified market trends")
    data_sources: Optional[List[str]] = Field(default_factory=list, description="Sources of the market analysis")

class GeoMarketAnalysisOutput(BaseModel):
    response: str = Field(..., description="Status message for market analysis")
    details: GeoMarketAnalysisDetails = Field(..., description="Detailed market trends analysis")


class SentimentInsight(BaseModel):
    trend: str = Field(..., description="Description of the market trend")
    impact: str = Field(..., description="Potential impact on the industry or business")
    confidence_level: Optional[float] = Field(None, description="Confidence level (0-1) indicating trend reliability")

class SentimentAnalysisDetails(BaseModel):
    industry_sector: str = Field(..., description="The industry sector analyzed")
    trends_summary: List[SentimentInsight] = Field(default_factory=list, description="List of identified market trends")
    data_sources: Optional[List[str]] = Field(default_factory=list, description="Sources of the market analysis")

class SentimentAnalysisOutput(BaseModel):
    response: str = Field(..., description="Status message for market analysis")
    details: SentimentAnalysisDetails = Field(..., description="Detailed market trends analysis")

class MarketGap(BaseModel):
    competitor_name: str = Field(..., description="Name of the competitor")
    differentiating_strategy: str = Field(..., description="Key strategy used by the competitor")
    market_positioning: Optional[str] = Field(None, description="How the competitor positions itself in the market")

class GapAnalysisDetails(BaseModel):
    competitors: List[MarketGap] = Field(default_factory=list, description="Competitor strategies analyzed")
    recommendations: str = Field(..., description="Strategic moves based on competitor analysis")
    risk_factors: Optional[List[str]] = Field(default_factory=list, description="Potential risks in competing strategies")

class GapAnalysisOutput(BaseModel):
    response: str = Field(..., description="Status message for competitor analysis")
    details: GapAnalysisDetails = Field(..., description="Detailed competitor analysis insights")    


class StrategicRecommendation(BaseModel):
    factor: str = Field(..., description="A key element influencing pricing decisions")
    influence: str = Field(..., description="How this factor impacts pricing strategies")
    data_source: Optional[str] = Field(None, description="Source of the pricing factor data")

class StrategicPlannerDetails(BaseModel):
    model_description: str = Field(..., description="Detailed overview of the pricing model")
    factors_considered: List[StrategicRecommendation] = Field(default_factory=list, description="Key factors affecting pricing")
    pricing_strategy: str = Field(..., description="Suggested pricing strategy based on analysis")
    profitability_forecast: Optional[str] = Field(None, description="Estimated profitability impact of this model")

class StrategicPlannerOutput(BaseModel):
    response: str = Field(..., description="Status message for pricing model generation")
    details: StrategicPlannerDetails = Field(..., description="Comprehensive pricing strategy analysis")

    