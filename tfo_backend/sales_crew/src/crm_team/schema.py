from pydantic import BaseModel, Field
from typing import Optional, List

class FollowUpEmail(BaseModel):
    subject: str  # Subject line for the email
    body: str  # Email content with placeholders for personalization
    call_to_action: str  # Action the recipient should take

class FollowUpEmailOutput(BaseModel):
    response: str  # e.g., "Email templates created successfully"
    templates: List[FollowUpEmail]  # List of generated email templates

class FeedbackInsight(BaseModel):
    trend: str = Field(..., description="Description of the market trend")
    impact: str = Field(..., description="Potential impact on the industry or business")
    confidence_level: Optional[float] = Field(None, description="Confidence level (0-1) indicating trend reliability")

class FeedbackAnalysisDetails(BaseModel):
    industry_sector: str = Field(..., description="The industry sector analyzed")
    trends_summary: List[FeedbackInsight] = Field(default_factory=list, description="List of identified market trends")
    data_sources: Optional[List[str]] = Field(default_factory=list, description="Sources of the market analysis")

class FeedbackAnalysisOutput(BaseModel):
    response: str = Field(..., description="Status message for market analysis")
    details: FeedbackAnalysisDetails = Field(..., description="Detailed market trends analysis")


class CustomerSegment(BaseModel):
    competitor_name: str = Field(..., description="Name of the competitor")
    differentiating_strategy: str = Field(..., description="Key strategy used by the competitor")
    market_positioning: Optional[str] = Field(None, description="How the competitor positions itself in the market")

class CustomerSegmentationDetails(BaseModel):
    competitors: List[CustomerSegment] = Field(default_factory=list, description="Competitor strategies analyzed")
    recommendations: str = Field(..., description="Strategic moves based on competitor analysis")
    risk_factors: Optional[List[str]] = Field(default_factory=list, description="Potential risks in competing strategies")

class CustomerSegmentationOutput(BaseModel):
    response: str = Field(..., description="Status message for competitor analysis")
    details: CustomerSegmentationDetails = Field(..., description="Detailed competitor analysis insights")


class CrossSellRecommendation(BaseModel):
    competitor_name: str = Field(..., description="Name of the competitor")
    differentiating_strategy: str = Field(..., description="Key strategy used by the competitor")
    market_positioning: Optional[str] = Field(None, description="How the competitor positions itself in the market")

class CrossSellStrategistDetails(BaseModel):
    competitors: List[CrossSellRecommendation] = Field(default_factory=list, description="Competitor strategies analyzed")
    recommendations: str = Field(..., description="Strategic moves based on competitor analysis")
    risk_factors: Optional[List[str]] = Field(default_factory=list, description="Potential risks in competing strategies")

class CrossSellStrategistOutput(BaseModel):
    response: str = Field(..., description="Status message for competitor analysis")
    details: CrossSellStrategistDetails = Field(..., description="Detailed competitor analysis insights")


class SurveyQuestion(BaseModel):
    question: str = Field(..., description="Survey question")
    question_type: str = Field(..., description="Type of question (e.g., Multiple Choice, Open-Ended, Likert Scale)")

class SurveySpecialistDetails(BaseModel):
    topic: str = Field(..., description="Main topic or context for survey development")
    survey_title: str = Field(..., description="Title of the customer satisfaction survey")
    target_audience: str = Field(..., description="Target respondents for the survey (e.g., New Customers, Returning Clients)")
    questions: List[SurveyQuestion] = Field(default_factory=list, description="List of survey questions")
    deployment_plan: Optional[str] = Field(None, description="Proposed strategy for deploying the survey")

class SurveySpecialistOutput(BaseModel):
    response: str = Field(..., description="Status message for survey creation")
    details: SurveySpecialistDetails = Field(..., description="Finalized survey template and deployment plan")
