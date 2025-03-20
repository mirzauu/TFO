      
from pydantic import BaseModel, Field
from typing import Optional, List

class KeywordData(BaseModel):
    trend: str = Field(..., description="Description of the market trend")
    impact: str = Field(..., description="Potential impact on the industry or business")
    confidence_level: Optional[float] = Field(None, description="Confidence level (0-1) indicating trend reliability")
class KeywordResearchDetails(BaseModel):
    industry_sector: str = Field(..., description="The industry sector analyzed")
    trends_summary: List[KeywordData] = Field(default_factory=list, description="List of identified market trends")
    data_sources: Optional[List[str]] = Field(default_factory=list, description="Sources of the market analysis")
class KeywordResearchOutput(BaseModel):
    response: str = Field(..., description="Status message for market analysis")
    details: KeywordResearchDetails = Field(..., description="Detailed market trends analysis")


class OptimizedPage(BaseModel):
    trend: str = Field(..., description="Description of the market trend")
    impact: str = Field(..., description="Potential impact on the industry or business")
    confidence_level: Optional[float] = Field(None, description="Confidence level (0-1) indicating trend reliability")

class ContentOptimizationDetails(BaseModel):
    industry_sector: str = Field(..., description="The industry sector analyzed")
    trends_summary: List[OptimizedPage] = Field(default_factory=list, description="List of identified market trends")
    data_sources: Optional[List[str]] = Field(default_factory=list, description="Sources of the market analysis")

class ContentOptimizationOutput(BaseModel):
    response: str = Field(..., description="Status message for market analysis")
    details: ContentOptimizationDetails = Field(..., description="Detailed market trends analysis")

# 🔗 Backlink Analysis
class BacklinkData(BaseModel):
    trend: str = Field(..., description="Description of the market trend")
    impact: str = Field(..., description="Potential impact on the industry or business")
    confidence_level: Optional[float] = Field(None, description="Confidence level (0-1) indicating trend reliability")
class BacklinkAnalysisDetails(BaseModel):
    industry_sector: str = Field(..., description="The industry sector analyzed")
    trends_summary: List[BacklinkData] = Field(default_factory=list, description="List of identified market trends")
    data_sources: Optional[List[str]] = Field(default_factory=list, description="Sources of the market analysis")
class BacklinkAnalysisOutput(BaseModel):
    response: str = Field(..., description="Status message for market analysis")
    details: BacklinkAnalysisDetails = Field(..., description="Detailed market trends analysis")

# 📊 Analytics Monitoring
class AnalyticsReport(BaseModel):
    competitor_name: str = Field(..., description="Name of the competitor")
    differentiating_strategy: str = Field(..., description="Key strategy used by the competitor")
    market_positioning: Optional[str] = Field(None, description="How the competitor positions itself in the market")
class AnalyticsMonitoringDetails(BaseModel):
    competitors: List[AnalyticsReport] = Field(default_factory=list, description="Competitor strategies analyzed")
    recommendations: str = Field(..., description="Strategic moves based on competitor analysis")
    risk_factors: Optional[List[str]] = Field(default_factory=list, description="Potential risks in competing strategies")

class AnalyticsMonitoringOutput(BaseModel):
    response: str = Field(..., description="Status message for competitor analysis")
    details: AnalyticsMonitoringDetails = Field(..., description="Detailed competitor analysis insights")

# 📈 SEO Reporting
class SEOReportMetrics(BaseModel):
    point: str = Field(..., description="A key persuasion point used in the pitch")
    supporting_evidence: Optional[str] = Field(None, description="Evidence or rationale supporting this point")
class SEOReportingDetails(BaseModel):
    target_demographic: str = Field(..., description="Intended audience for the pitch")
    pitch_content: str = Field(..., description="Full sales pitch text")
    key_persuasion_points: List[SEOReportMetrics] = Field(default_factory=list, description="Highlighted persuasion techniques")
    call_to_action: str = Field(..., description="Final call to action for the audience")
    estimated_conversion_rate: Optional[float] = Field(None, description="Predicted conversion rate impact (0-1)")
class SEOReportingOutput(BaseModel):
    response: str = Field(..., description="Status message for sales pitch creation")
    details: SEOReportingDetails = Field(..., description="Detailed sales pitch breakdown")

# 🏷 Meta Description & Titles
class MetaData(BaseModel):
    competitor_name: str = Field(..., description="Name of the competitor")
    differentiating_strategy: str = Field(..., description="Key strategy used by the competitor")
    market_positioning: Optional[str] = Field(None, description="How the competitor positions itself in the market")
class MetaDescriptionDetails(BaseModel):
    competitors: List[MetaData] = Field(default_factory=list, description="Competitor strategies analyzed")
    recommendations: str = Field(..., description="Strategic moves based on competitor analysis")
    risk_factors: Optional[List[str]] = Field(default_factory=list, description="Potential risks in competing strategies")
class MetaDescriptionOutput(BaseModel):
    response: str = Field(..., description="Status message for competitor analysis")
    details: MetaDescriptionDetails = Field(..., description="Detailed competitor analysis insights")

# 📢 Ad Copywriting
class AdCopy(BaseModel):
    trend: str = Field(..., description="Description of the market trend")
    impact: str = Field(..., description="Potential impact on the industry or business")
    confidence_level: Optional[float] = Field(None, description="Confidence level (0-1) indicating trend reliability")
class AdCopyDetails(BaseModel):
    industry_sector: str = Field(..., description="The industry sector analyzed")
    trends_summary: List[AdCopy] = Field(default_factory=list, description="List of identified market trends")
    data_sources: Optional[List[str]] = Field(default_factory=list, description="Sources of the market analysis")
class AdCopyOutput(BaseModel):
    response: str = Field(..., description="Status message for market analysis")
    details: AdCopyDetails = Field(..., description="Detailed market trends analysis")

# 🎯 SEM Campaign Management
class SEMCampaignUpdate(BaseModel):
    trend: str = Field(..., description="Description of the market trend")
    impact: str = Field(..., description="Potential impact on the industry or business")
    confidence_level: Optional[float] = Field(None, description="Confidence level (0-1) indicating trend reliability")
class SEMCampaignManagementDetails(BaseModel):
    industry_sector: str = Field(..., description="The industry sector analyzed")
    trends_summary: List[SEMCampaignUpdate] = Field(default_factory=list, description="List of identified market trends")
    data_sources: Optional[List[str]] = Field(default_factory=list, description="Sources of the market analysis")
class SEMCampaignManagementOutput(BaseModel):
    response: str = Field(..., description="Status message for market analysis")
    details: SEMCampaignManagementDetails = Field(..., description="Detailed market trends analysis")

# 🏆 Competitor Analysis
class CompetitorInsight(BaseModel):
    competitor_name: str = Field(..., description="Name of the competitor")
    differentiating_strategy: str = Field(..., description="Key strategy used by the competitor")
    market_positioning: Optional[str] = Field(None, description="How the competitor positions itself in the market")
class CompetitorAnalysisDetails(BaseModel):
    competitors: List[CompetitorInsight] = Field(default_factory=list, description="Competitor strategies analyzed")
    recommendations: str = Field(..., description="Strategic moves based on competitor analysis")
    risk_factors: Optional[List[str]] = Field(default_factory=list, description="Potential risks in competing strategies")
class CompetitorAnalysisOutput(BaseModel):
    response: str = Field(..., description="Status message for competitor analysis")
    details: CompetitorAnalysisDetails = Field(..., description="Detailed competitor analysis insights")

# 🏗 SEO Audit
class SEOAuditIssue(BaseModel):
    competitor_name: str = Field(..., description="Name of the competitor")
    differentiating_strategy: str = Field(..., description="Key strategy used by the competitor")
    market_positioning: Optional[str] = Field(None, description="How the competitor positions itself in the market")
class SEOAuditDetails(BaseModel):
    competitors: List[SEOAuditIssue] = Field(default_factory=list, description="Competitor strategies analyzed")
    recommendations: str = Field(..., description="Strategic moves based on competitor analysis")
    risk_factors: Optional[List[str]] = Field(default_factory=list, description="Potential risks in competing strategies")
class SEOAuditOutput(BaseModel):
    response: str = Field(..., description="Status message for competitor analysis")
    details: SEOAuditDetails = Field(..., description="Detailed competitor analysis insights")


class InternalLinkingDetails(BaseModel):
    post_title: str  # Title or headline of the post
    caption: str  # Engaging caption
    hashtags: List[str]  # Relevant hashtags for the post
    call_to_action: str  # Encouraged action for engagement
class InternalLinkingOutput(BaseModel):
    response: str  # e.g., "Social media content created successfully"
    posts: List[InternalLinkingDetails]  # List of LinkedIn posts

    