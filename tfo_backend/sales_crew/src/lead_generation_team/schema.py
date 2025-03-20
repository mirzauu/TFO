from pydantic import BaseModel, Field
from typing import Optional, List

class Lead(BaseModel):
    trend: str = Field(..., description="Description of the market trend")
    impact: str = Field(..., description="Potential impact on the industry or business")
    confidence_level: Optional[float] = Field(None, description="Confidence level (0-1) indicating trend reliability")

class LeadIdentifierDetails(BaseModel):
    industry_sector: str = Field(..., description="The industry sector analyzed")
    trends_summary: List[Lead] = Field(default_factory=list, description="List of identified market trends")
    data_sources: Optional[List[str]] = Field(default_factory=list, description="Sources of the market analysis")

class LeadIdentifierOutput(BaseModel):
    response: str = Field(..., description="Status message for lead identification")
    details: LeadIdentifierDetails = Field(..., description="Comprehensive lead identification results")

class LeadProfile(BaseModel):
    trend: str = Field(..., description="Description of the market trend")
    impact: str = Field(..., description="Potential impact on the industry or business")
    confidence_level: Optional[float] = Field(None, description="Confidence level (0-1) indicating trend reliability")

class ResearchAnalystDetails(BaseModel):
    industry_sector: str = Field(..., description="The industry sector analyzed")
    trends_summary: List[LeadProfile] = Field(default_factory=list, description="List of identified market trends")
    data_sources: Optional[List[str]] = Field(default_factory=list, description="Sources of the market analysis")

class ResearchAnalystOutput(BaseModel):
    response: str = Field(..., description="Status message for lead research and enrichment")
    details: ResearchAnalystDetails = Field(..., description="Comprehensive lead research output")

class SocialMediaProfile(BaseModel):
    platform: str = Field(..., description="Social media platform (e.g., LinkedIn, Twitter)")
    profile_url: str = Field(..., description="URL to the lead's social media profile")
    engagement_score: Optional[float] = Field(None, description="Engagement score based on social interactions (0-1)")
    activity_summary: Optional[str] = Field(None, description="Summary of recent activity relevant to lead interest")

class SocialMediaExtractorDetails(BaseModel):
    leads_social_media: List[SocialMediaProfile] = Field(default_factory=list, description="List of social media profiles extracted")

class SocialMediaExtractorOutput(BaseModel):
    response: str = Field(..., description="Status message for social media extraction")
    details: SocialMediaExtractorDetails = Field(..., description="Comprehensive social media engagement analysis")

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
