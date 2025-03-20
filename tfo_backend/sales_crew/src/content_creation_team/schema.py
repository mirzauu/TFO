from pydantic import BaseModel
from typing import List


class SalesBrochure(BaseModel):
    response: str  # e.g., "Sales brochure created", "Modifications applied"
    brochure: str  # Structured content of the sales brochure


class Slide(BaseModel):
    title: str
    content: str
    testimonials: List[str] = []


class PresentationOutput(BaseModel):
    topic: str
    slides: List[Slide]


class EmailTemplate(BaseModel):
    subject: str  # Subject line for the email
    body: str  # Email content with placeholders for personalization
    call_to_action: str  # Action the recipient should take


class EmailTemplateOutput(BaseModel):
    response: str  # e.g., "Email templates created successfully"
    templates: List[EmailTemplate]  # List of generated email templates


class ProductDescription(BaseModel):
    product_name: str  # Name of the product
    description: str  # Detailed, engaging product description
    key_features: List[str]  # List of key features highlighted in the description
    pain_points_addressed: List[str]  # Problems solved by the product


class ProductDescriptionOutput(BaseModel):
    response: str  # e.g., "Product descriptions generated successfully"
    descriptions: List[ProductDescription]  # List of generated product descriptions


class SocialMediaPost(BaseModel):
    post_title: str  # Title or headline of the post
    caption: str  # Engaging caption
    hashtags: List[str]  # Relevant hashtags for the post
    call_to_action: str  # Encouraged action for engagement


class SocialMediaContentOutput(BaseModel):
    response: str  # e.g., "Social media content created successfully"
    posts: List[SocialMediaPost]  # List of LinkedIn posts
