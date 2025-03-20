from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import urllib.parse


# WebsiteSearchTool (Scrape competitor sites)
class WebsiteSearchSchema(BaseModel):
    competitors: str = Field(..., description="Comma-separated list of competitors to analyze.")
    platform: str = Field(..., description="The social media platform (e.g., Twitter, Instagram, LinkedIn).")

class WebsiteSearchTool(BaseTool):
    name: str = "website_search"
    description: str = "Generates search URLs to analyze competitor social media strategies."
    args_schema: Type[BaseModel] = WebsiteSearchSchema

    def _run(self, competitors: str, platform: str) -> str:
        competitor_list = [comp.strip() for comp in competitors.split(",")]
        search_urls = []

        for competitor in competitor_list:
            search_url = f"https://www.google.com/search?q={competitor}+social+media+strategy+site:{platform}.com"
            search_urls.append(search_url)
        
        return "\n".join(search_urls)

# Example usage
if __name__ == "__main__":
    tool = WebsiteSearchTool()
    result = tool._run("Nike, Adidas", "Twitter")
    print(result)


# CSVTool (Create and manage calendars)
class CalendarManagementSchema(BaseModel):
    campaign_theme: str = Field(..., description="The theme of the campaign.")
    target_audience: str = Field(..., description="The target audience.")

class CSVTool(BaseTool):
    name: str = "csv_calendar"
    description: str = "Creates and manages social media content calendars."
    args_schema: Type[BaseModel] = CalendarManagementSchema

    def _run(self, campaign_theme: str, target_audience: str) -> str:
        return f"Content calendar created for {campaign_theme}, targeting {target_audience}."

# SerperDevTool (Google Alerts Integration)
class GoogleAlertsSchema(BaseModel):
    campaign_theme: str = Field(..., description="Theme of the marketing campaign.")
    platform: str = Field(..., description="Social media platform for the campaign.")
    goal: str = Field(..., description="Marketing objective of the campaign.")

class GoogleAlertsTool(BaseTool):
    name: str = "google_search"
    description: str = "Searches the web for relevant social media content ideas and best practices."
    args_schema: Type[BaseModel] = GoogleAlertsSchema

    def _run(self, campaign_theme: str, platform: str, goal: str) -> str:
        query = f"{campaign_theme} Content Planner {platform} structured social media content calendar best practices for {goal}"
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        return f"Perform your search here: {search_url}"

# Example usage:
if __name__ == "__main__":
    tool = GoogleAlertsTool()
    print(tool._run("Holiday Marketing", "Instagram", "increase engagement"))

# TwitterSearchTool
class TwitterSearchSchema(BaseModel):
    campaign_theme: str = Field(..., description="The campaign theme to find relevant influencers.")

class TwitterSearchTool(BaseTool):
    name: str = "twitter_search"
    description: str = "Generates a Twitter search URL based on the campaign theme to find relevant influencers."
    args_schema: Type[BaseModel] = TwitterSearchSchema

    def _run(self, campaign_theme: str) -> str:
        formatted_theme = campaign_theme.replace(' ', '%20')
        search_url = f"https://twitter.com/search?q={formatted_theme}%20influencer&src=typed_query"
        return f"Search for {campaign_theme} influencers on Twitter: {search_url}"

# InstagramScraper
class InstagramScraperSchema(BaseModel):
    campaign_theme: str = Field(..., description="The campaign theme to find relevant influencers.")

class InstagramScraperTool(BaseTool):
    name: str = "instagram_scraper"
    description: str = "Generates an Instagram search URL based on the campaign theme to find relevant influencers."
    args_schema: Type[BaseModel] = InstagramScraperSchema

    def _run(self, campaign_theme: str) -> str:
        formatted_theme = campaign_theme.replace(' ', '')
        search_url = f"https://www.instagram.com/explore/tags/{formatted_theme}influencer/"
        return f"Explore Instagram influencers related to {campaign_theme}: {search_url}"


# OpenAIAgentTool (AI-Generated Messages)
class AIGeneratedMessageSchema(BaseModel):
    campaign_theme: str = Field(..., description="The theme of the customer engagement campaign.")
    platform: str = Field(..., description="The social media platform where engagement will take place.")
    goal: str = Field(..., description="The specific engagement goal, e.g., responding to inquiries, thanking customers, promoting campaigns.")

class OpenAIAgentMessageTool(BaseTool):
    name: str = "ai_generated_message"
    description: str = "Generates AI-powered direct messages for customer engagement."
    args_schema: Type[BaseModel] = AIGeneratedMessageSchema

    def _run(self, campaign_theme: str, platform: str, goal: str) -> str:
        message_templates = {
            "responding to inquiries": "Hello! Thanks for reaching out. We're happy to help with any questions about {campaign_theme}. Let us know how we can assist you!",
            "thanking customers": "Hey there! We truly appreciate your support for {campaign_theme}. Your engagement on {platform} means the world to us! ❤️",
            "promoting campaigns": "Exciting news! Our latest {campaign_theme} campaign is now live on {platform}. Check it out and let us know what you think! #StayConnected"
        }
        
        template = message_templates.get(goal.lower(), "Hello! Thank you for engaging with us on {platform}. We appreciate your support!")
        return template.format(campaign_theme=campaign_theme, platform=platform)

# PDFTool (Export Reports)
class PDFExportSchema(BaseModel):
    report_type: str = Field(..., description="Type of report to export (e.g., social media metrics, competitor analysis).")
    platform: str = Field(..., description="Social media platform (e.g., Twitter, Instagram, LinkedIn).")
    goal: str = Field(..., description="Campaign objective (e.g., increase engagement, boost followers, drive conversions).")
    campaign_theme: str = Field(..., description="The main theme or focus of the campaign (e.g., product launch, brand awareness).")

class PDFTool(BaseTool):
    name: str = "pdf_export"
    description: str = "Exports social media performance reports as PDFs."
    args_schema: Type[BaseModel] = PDFExportSchema

    def _run(self, report_type: str, platform: str, goal: str, campaign_theme: str) -> str:
        report_content = f"""
        # {campaign_theme} Social Media Performance Report

        ## Platform: {platform}
        ## Goal: {goal}

        ### Key Metrics
        - **Reach:** 1,200,000 users
        - **Engagement Rate:** 5.6%
        - **Impressions:** 3,400,000
        - **Conversion Rate:** 2.3%
        
        ### Insights & Recommendations
        - Posts with high-quality visuals had **30% more engagement**.
        - Engagement peaks occurred on **Wednesdays and Saturdays**.
        - Hashtag strategy improvement led to a **20% increase in reach**.
        
        ### Suggested Actions
        1. Increase video content to boost engagement further.
        2. Optimize posting schedule based on peak times.
        3. Experiment with interactive posts like polls and Q&A.
        
        ---
        Report generated by **Metrics Analyst**.
        """
        
        output_file = "report.md"
        with open(output_file, "w") as file:
            file.write(report_content)
        
        return f"PDF report generated for {report_type}. Saved to {output_file}."


# KeywordResearchTool
class KeywordResearchSchema(BaseModel):
    campaign_theme: str = Field(..., description="The campaign theme for keyword research.")

class KeywordResearchTool(BaseTool):
    name: str = "keyword_research"
    description: str = "Conducts keyword research for campaigns."
    args_schema: Type[BaseModel] = KeywordResearchSchema

    def _run(self, campaign_theme: str) -> str:
        return f"Keyword research completed for {campaign_theme}."

# OpenAIAgentTool (Caption Generation)
class CaptionGenerationSchema(BaseModel):
    campaign_theme: str = Field(..., description="The campaign theme for captions.")

class OpenAIAgentCaptionTool(BaseTool):
    name: str = "ai_generated_caption"
    description: str = "Generates AI-powered social media captions."
    args_schema: Type[BaseModel] = CaptionGenerationSchema

    def _run(self, campaign_theme: str) -> str:
        return f"AI-generated captions for {campaign_theme}."

# OpenAIAgentTool (Scriptwriting for TikTok/YouTube Shorts)
class ScriptWritingSchema(BaseModel):
    campaign_theme: str = Field(..., description="The campaign theme for the script.")
    platform: str = Field(..., description="Platform for the script (TikTok/YouTube Shorts).")

class OpenAIAgentScriptTool(BaseTool):
    name: str = "ai_script_writing"
    description: str = "Generates short-form video scripts for TikTok/YouTube Shorts."
    args_schema: Type[BaseModel] = ScriptWritingSchema

    def _run(self, campaign_theme: str, platform: str) -> str:
        return f"AI-generated {platform} script for {campaign_theme}."
