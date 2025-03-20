      
from pydantic import BaseModel, Field
from typing import Optional, List


# 🔍 Competitor Analysis
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

# 📅 Content Planning
class ContentCalendarEntry(BaseModel):
    point: str = Field(..., description="A key persuasion point used in the pitch")
    supporting_evidence: Optional[str] = Field(None, description="Evidence or rationale supporting this point")
class ContentPlannerDetails(BaseModel):
    target_demographic: str = Field(..., description="Intended audience for the pitch")
    pitch_content: str = Field(..., description="Full sales pitch text")
    key_persuasion_points: List[ContentCalendarEntry] = Field(default_factory=list, description="Highlighted persuasion techniques")
    call_to_action: str = Field(..., description="Final call to action for the audience")
    estimated_conversion_rate: Optional[float] = Field(None, description="Predicted conversion rate impact (0-1)")
class ContentPlannerOutput(BaseModel):
    response: str = Field(..., description="Status message for sales pitch creation")
    details: ContentPlannerDetails = Field(..., description="Detailed sales pitch breakdown")

# 📢 Brand Monitoring
class BrandMention(BaseModel):
    competitor_name: str = Field(..., description="Name of the competitor")
    differentiating_strategy: str = Field(..., description="Key strategy used by the competitor")
    market_positioning: Optional[str] = Field(None, description="How the competitor positions itself in the market")

class BrandMonitorDetails(BaseModel):
    competitors: List[BrandMention] = Field(default_factory=list, description="Competitor strategies analyzed")
    recommendations: str = Field(..., description="Strategic moves based on competitor analysis")
    risk_factors: Optional[List[str]] = Field(default_factory=list, description="Potential risks in competing strategies")
class BrandMonitorOutput(BaseModel):
    response: str = Field(..., description="Status message for competitor analysis")
    details: BrandMonitorDetails = Field(..., description="Detailed competitor analysis insights")

# 🎭 Influencer Research
class InfluencerProfile(BaseModel):
    name: str = Field(..., description="Influencer’s name or handle")
    platform: str = Field(..., description="Social media platform")
    follower_count: int = Field(..., description="Total followers")
    engagement_rate: float = Field(..., description="Average engagement rate (%)")
    relevance_score: Optional[int] = Field(None, description="Relevance to the brand (Scale of 1-10)")
    contact_info: Optional[str] = Field(None, description="Email or direct message contact")

class InfluencerScoutDetails(BaseModel):
    post_title: str  # Title or headline of the post
    caption: str  # Engaging caption
    hashtags: List[str]  # Relevant hashtags for the post
    call_to_action: str  # Encouraged action for engagement
class InfluencerScoutOutput(BaseModel):
    response: str  # e.g., "Social media content created successfully"
    posts: List[InfluencerScoutDetails]  # List of LinkedIn posts


class CustomerEngagementDetails(BaseModel):
    subject: str  # Subject line for the email
    body: str  # Email content with placeholders for personalization
    call_to_action: str  # Action the recipient should take

class CustomerEngagementOutput(BaseModel):
    response: str  # e.g., "Email templates created successfully"
    templates: List[CustomerEngagementDetails]  # List of generated email templates

# 📊 Social Media Metrics Analysis
class SocialMetric(BaseModel):
    trend: str = Field(..., description="Description of the market trend")
    impact: str = Field(..., description="Potential impact on the industry or business")
    confidence_level: Optional[float] = Field(None, description="Confidence level (0-1) indicating trend reliability")

class MetricsAnalysisDetails(BaseModel):
    industry_sector: str = Field(..., description="The industry sector analyzed")
    trends_summary: List[SocialMetric] = Field(default_factory=list, description="List of identified market trends")
    data_sources: Optional[List[str]] = Field(default_factory=list, description="Sources of the market analysis")

class MetricsAnalysisOutput(BaseModel):
    response: str = Field(..., description="Status message for market analysis")
    details: MetricsAnalysisDetails = Field(..., description="Detailed market trends analysis")



class HashtagStrategyDetails(BaseModel):
    subject: str  # Subject line for the email
    body: str  # Email content with placeholders for personalization
    call_to_action: str  # Action the recipient should take

class HashtagStrategyOutput(BaseModel):
    response: str  # e.g., "Email templates created successfully"
    templates: List[HashtagStrategyDetails]  # List of generated email templates



class CampaignDesignDetails(BaseModel):
    product_name: str  # Name of the product
    description: str  # Detailed, engaging product description
    key_features: List[str]  # List of key features highlighted in the description
    pain_points_addressed: List[str]  # Problems solved by the product

class CampaignDesignOutput(BaseModel):
    response: str  # e.g., "Product descriptions generated successfully"
    descriptions: List[CampaignDesignDetails]  # List of generated product descriptions



class CaptionCreationDetails(BaseModel):
    product_name: str  # Name of the product
    description: str  # Detailed, engaging product description
    key_features: List[str]  # List of key features highlighted in the description
    pain_points_addressed: List[str]  # Problems solved by the product

class CaptionCreationOutput(BaseModel):
    response: str  # e.g., "Product descriptions generated successfully"
    descriptions: List[CaptionCreationDetails]  # List of generated product descriptions

# 🎬 Short-Form Video Scriptwriting
class ShortFormScript(BaseModel):
    platform: str = Field(..., description="Platform for the video (e.g., TikTok, YouTube Shorts)")
    script_text: str = Field(..., description="Full script content")
    duration: int = Field(..., description="Estimated duration in seconds")

class ScriptWritingDetails(BaseModel):
    product_name: str  # Name of the product
    description: str  # Detailed, engaging product description
    key_features: List[str]  # List of key features highlighted in the description
    pain_points_addressed: List[str]  # Problems solved by the product

class ScriptWritingOutput(BaseModel):
    response: str  # e.g., "Product descriptions generated successfully"
    descriptions: List[ScriptWritingDetails]  # List of generated product descriptions

    