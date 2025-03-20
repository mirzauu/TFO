
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import requests


class SocialMediaAnalyticsSchema(BaseModel):
    competitors: str = Field(..., description="Comma-separated list of competitor names.")
    platform: str = Field(..., description="Social media platform to analyze (e.g., Twitter, Instagram, Facebook, LinkedIn).")

class SocialMediaAnalyticsTool(BaseTool):
    name: str = "social_media_analytics"
    description: str = "Fetches competitor analysis data from a social media analytics website."
    args_schema: Type[BaseModel] = SocialMediaAnalyticsSchema
    
    def _run(self, competitors: str, platform: str) -> str:
        url = f"https://socialblade.com/{platform}/search/{competitors.replace(',', '%2C')}"  # Using SocialBlade for competitor analysis
        
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise exception for HTTP errors
            
            return f"Fetched competitor analysis data for {competitors} on {platform}. Visit {url} for details."
        except requests.exceptions.RequestException as e:
            return f"Failed to fetch competitor analysis: {str(e)}"

class CalendarPlannerSchema(BaseModel):
    campaign_theme: str = Field(..., description="The theme of the campaign.")
    platform: str = Field(..., description="Platform for the calendar.")
    goal: str = Field(..., description="Marketing goal for the campaign.")
    competitor_url: str = Field(..., description="URL of a competitor's social media page to analyze.")

class CalendarPlannerTool(BaseTool):
    name: str = "calendar_planner"
    description: str = "Generates and organizes a visual social media calendar with competitor analysis."
    args_schema: Type[BaseModel] = CalendarPlannerSchema

    def _run(self, campaign_theme: str, platform: str, goal: str, competitor_url: str):
        try:
            # Simulating competitor analysis by scraping (basic HTML fetch)
            response = requests.get(competitor_url, timeout=10)
            if response.status_code != 200:
                return f"Failed to analyze competitor content from {competitor_url}"
            
            competitor_content = response.text[:1000]  # Extract a preview for basic analysis
            
            # Generate a sample structured calendar
            calendar = {
                "campaign_theme": campaign_theme,
                "platform": platform,
                "goal": goal,
                "competitor_insights": f"Analyzed competitor content from {competitor_url}.",
                "posting_schedule": [
                    {"day": "Monday", "post_type": "Image", "theme": campaign_theme, "time": "10 AM"},
                    {"day": "Wednesday", "post_type": "Video", "theme": campaign_theme, "time": "2 PM"},
                    {"day": "Friday", "post_type": "Story", "theme": campaign_theme, "time": "6 PM"}
                ]
            }
            return calendar
        except Exception as e:
            return f"Error generating calendar: {str(e)}"

    


class SocialMediaListeningSchema(BaseModel):
    brand_name: str = Field(..., description="Brand name to monitor.")
    platform: str = Field(..., description="Platform to track mentions on (Twitter, Reddit, etc.).")

class SocialMediaListeningTool(BaseTool):
    name: str = "social_media_listening"
    description: str = "Tracks sentiment and mentions of a brand on social media."
    args_schema: Type[BaseModel] = SocialMediaListeningSchema
    
    def _run(self, brand_name: str, platform: str) -> str:
        search_urls = {
            "twitter": f"https://twitter.com/search?q={brand_name}&src=typed_query",
            "reddit": f"https://www.reddit.com/search/?q={brand_name}",
            "google": f"https://www.google.com/search?q={brand_name}+site:{platform}.com"
        }
        
        platform = platform.lower()
        if platform in search_urls:
            return f"Track mentions here: {search_urls[platform]}"
        else:
            return "Platform not supported. Try Twitter, Reddit, or Google search."



class InfluencerFinderSchema(BaseModel):
    campaign_theme: str = Field(..., description="The campaign theme to find influencers in.")
    platform: str = Field(..., description="Social media platform.")

class InfluencerFinderTool(BaseTool):
    name: str = "influencer_finder"
    description: str = "Finds influencers based on engagement metrics. Uses real URLs for research."
    args_schema: Type[BaseModel] = InfluencerFinderSchema

    def _run(self, campaign_theme: str, platform: str) -> str:
        search_url = f"https://www.google.com/search?q=top+{campaign_theme}+influencers+on+{platform}"
        
        results = self._get_search_results(search_url)
        
        return results if results else f"No influencers found for {campaign_theme} on {platform}."
    
    def _get_search_results(self, url: str) -> str:
        """
        Fetch search results using requests (simulating an internet search).
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return f"Search for influencers here: {url}"
            else:
                return "Failed to fetch influencer data."
        except Exception as e:
            return f"Error occurred: {str(e)}"


class DirectMessageTemplateSchema(BaseModel):
    purpose: str = Field(..., description="Purpose of the direct message.")

class DirectMessageTemplateTool(BaseTool):
    name: str = "direct_message_template"
    description: str = "Stores and retrieves reusable DM templates for customer engagement."
    args_schema: Type[BaseModel] = DirectMessageTemplateSchema

    TEMPLATES: dict[str, str] = {
        "thank_you": "Hi, thank you for supporting our {campaign_theme} campaign on {platform}! We appreciate your involvement in {goal}.",
        "promotion": "Hey, don't miss out on our {campaign_theme} special offers on {platform}! Join us in achieving {goal}.",
        "inquiry_response": "Hello, thanks for reaching out about our {campaign_theme} initiative on {platform}. Here’s the information you need to support {goal}.",
        "feedback_request": "Hi, we’d love your feedback on our {campaign_theme} efforts on {platform}! Your input helps us improve and reach {goal}.",
    }

    def _run(self, purpose: str) -> str:
        """
        Retrieves a direct message template based on the provided purpose.
        """
        return self.TEMPLATES.get(purpose, f"No template found for {purpose}.")

class SocialMediaMetricsSchema(BaseModel):
    platform: str = Field(..., description="Social media platform to gather data from.")
    campaign_theme: str = Field(..., description="Theme of the campaign being analyzed.")
    goal: str = Field(..., description="Objective of tracking the social media performance.")

class SocialMediaMetricsTool(BaseTool):
    name: str = "social_media_metrics"
    description: str = "Gathers analytics from public social media sources."
    args_schema: Type[BaseModel] = SocialMediaMetricsSchema

    def _run(self, platform: str, campaign_theme: str, goal: str) -> str:
        platform_urls = {
            "instagram": "https://www.instagram.com/insights/",
            "tiktok": "https://www.tiktok.com/analytics",
            "facebook": "https://business.facebook.com/insights/",
            "twitter": "https://analytics.twitter.com/",
            "linkedin": "https://www.linkedin.com/analytics/"
        }
        
        url = platform_urls.get(platform.lower(), "Unknown platform")
        if url == "Unknown platform":
            return f"Metrics for {platform} are not available. Please use Instagram, TikTok, Facebook, Twitter, or LinkedIn."
        
        metrics_template = (f"\n===== Social Media Metrics Report =====\n"
                            f"Campaign Theme: {campaign_theme}\n"
                            f"Objective: {goal}\n"
                            f"Platform: {platform.capitalize()}\n"
                            f"Engagement Rate: TBD\n"
                            f"Reach: TBD\n"
                            f"Impressions: TBD\n"
                            f"Conversion Rate: TBD\n"
                            f"---------------------------------------\n"
                            f"Access public metrics here: {url}\n")
        
        print(metrics_template)
        return metrics_template


class HashtagGeneratorSchema(BaseModel):
    campaign_theme: str = Field(..., description="The campaign theme for hashtag generation.")

class HashtagGeneratorTool(BaseTool):
    name: str = "hashtag_generator"
    description: str = "Suggests trending hashtags based on the campaign theme."
    args_schema: Type[BaseModel] = HashtagGeneratorSchema

    def _run(self, campaign_theme: str) -> str:
        return f"Generated trending hashtags for {campaign_theme}."

class CampaignDesignerSchema(BaseModel):
    campaign_theme: str = Field(..., description="The theme of the campaign.")
    goal: str = Field(..., description="The goal of the campaign.")
    platform: str = Field(..., description="The social media platform (e.g., Instagram, Twitter, TikTok).")

class CampaignDesignerTool(BaseTool):
    name: str = "campaign_designer"
    description: str = "Outlines and structures social media campaigns with challenges or giveaways."
    args_schema: Type[BaseModel] = CampaignDesignerSchema

    def _run(self, campaign_theme: str, goal: str, platform: str) -> str:
        try:
            # Simulating campaign structure generation
            campaign_plan = {
                "title": f"{campaign_theme} Challenge",
                "goal": goal,
                "platform": platform,
                "rules": [
                    "Participants must follow the page",
                    "Use the campaign hashtag",
                    "Tag three friends to enter",
                ],
                "prizes": [
                    "Exclusive merchandise",
                    "Gift cards",
                    "Feature on our social media",
                ],
                "expected_outcome": "Increased engagement and brand awareness."
            }
            
            
            reference_url = "https://blog.hootsuite.com/social-media-contest-ideas/"
            return f"Designed campaign: {campaign_plan}. For inspiration, visit {reference_url}"
        except Exception as e:
            return f"Error generating campaign: {str(e)}"


class CaptionRepositorySchema(BaseModel):
    campaign_theme: str = Field(..., description="Campaign theme of captions to retrieve.")

class CaptionRepositoryTool(BaseTool):
    name: str = "caption_repository"
    description: str = "Stores and retrieves captions for reuse."
    args_schema: Type[BaseModel] = CaptionRepositorySchema

    def _run(self, campaign_theme: str) -> str:
        return f"Retrieved captions from campaign theme: {campaign_theme}."

class VideoScriptSchema(BaseModel):
    campaign_theme: str = Field(..., description="Theme of the video content.")
    platform: str = Field(..., description="Platform where the video will be posted.")

class VideoScriptTool(BaseTool):
    name: str = "video_script"
    description: str = "Helps in writing structured video scripts."
    args_schema: Type[BaseModel] = VideoScriptSchema

    def _run(self, campaign_theme: str, platform: str) -> str:
        # Example search URL for real script inspiration
        search_url = f"https://www.google.com/search?q={campaign_theme}+TikTok+script+examples"
        
        # Example script template
        script_template = f'''
        [Opening Scene]
        (Hook) "Did you know that {campaign_theme} can change your life in just 60 seconds?" 
        [Visual: Fast-paced engaging scene]
        
        [Main Content]
        - Briefly introduce the key concept of {campaign_theme}
        - Show a quick demo or highlight (if applicable)
        - Include a fun fact or surprising element
        
        [Call to Action]
        "Want to learn more? Follow for more {campaign_theme} tips!"
        '''
        
        return f"Created video script for {campaign_theme} on {platform}.\n\nResearch More: {search_url}\n\nExample Script:\n{script_template}"

