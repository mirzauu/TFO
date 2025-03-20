      
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
import marketing_crew.src.social_media_crew.schema as schema
import marketing_crew.src.social_media_crew.main as main 
from marketing_crew.src.social_media_crew.tools.lang_tools import (
    WebsiteSearchTool,
    CSVTool,
    GoogleAlertsTool,
    TwitterSearchTool,
    InstagramScraperTool,
    OpenAIAgentMessageTool,
    PDFTool,
    KeywordResearchTool,
    OpenAIAgentCaptionTool,
    OpenAIAgentScriptTool

)

from marketing_crew.src.social_media_crew.tools.custom_tool import (SocialMediaAnalyticsTool,
   CalendarPlannerTool,
   SocialMediaListeningTool,
   InfluencerFinderTool,
   DirectMessageTemplateTool,
   SocialMediaMetricsTool,
   HashtagGeneratorTool,
   CampaignDesignerTool,
   CaptionRepositoryTool,
   VideoScriptTool)

from marketing_crew.src.social_media_crew.tools.taskupdate_status import TaskStatusUpdate

from dotenv import load_dotenv

load_dotenv()

@CrewBase
class SocialMediaCrew():
	"""SocialMediaCrew crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	

	@agent
	def competitor_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['competitor_analyst'],
			tools=[SerperDevTool(),WebsiteSearchTool(),SocialMediaAnalyticsTool()],
			verbose=True
		)
	
	@agent
	def content_planner(self) -> Agent:
		return Agent(
			config=self.agents_config['content_planner'],
			tools=[CSVTool(),CalendarPlannerTool()],
			verbose=True
		)
	
	@agent
	def brand_monitor(self) -> Agent:
		return Agent(
			config=self.agents_config['brand_monitor'],
			tools=[SocialMediaListeningTool(),GoogleAlertsTool()],
			verbose=True
		)
	
	@agent
	def influencer_scout(self) -> Agent:
		return Agent(
			config=self.agents_config['influencer_scout'],
			tools=[TwitterSearchTool(),InstagramScraperTool(),InfluencerFinderTool()],
			verbose=True
		)
	
	@agent
	def customer_engagement_expert(self) -> Agent:
		return Agent(
			config=self.agents_config['customer_engagement_expert'],
			tools=[OpenAIAgentMessageTool(), DirectMessageTemplateTool()],
			verbose=True
		)
	
	@agent
	def metrics_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['metrics_analyst'],
			tools=[OpenAIAgentMessageTool(), DirectMessageTemplateTool(),SocialMediaMetricsTool()],
			verbose=True
		)
	
	@agent
	def hashtag_strategist(self) -> Agent:
		return Agent(
			config=self.agents_config['hashtag_strategist'],
			tools=[KeywordResearchTool(),HashtagGeneratorTool()],
			verbose=True
		)
	
	@agent
	def campaign_designer(self) -> Agent:
		return Agent(
			config=self.agents_config['campaign_designer'],
			tools=[CampaignDesignerTool()],
			verbose=True
		)
	
	@agent
	def caption_creator(self) -> Agent:
		return Agent(
			config=self.agents_config['caption_creator'],
			tools=[OpenAIAgentCaptionTool(), CaptionRepositoryTool()],
			verbose=True
		)
	
	@agent
	def script_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['script_writer'],
			tools=[VideoScriptTool(),OpenAIAgentScriptTool()],
			verbose=True
		)
	

	
	#Tasks

	@task
	def competitor_analysis_task(self) -> Task:
		return Task(
			config=self.tasks_config['competitor_analysis_task'],
			output_json=schema.CompetitorAnalysisOutput,
			
		)

	@task
	def content_planner_task(self) -> Task:
		return Task(
			config=self.tasks_config['content_planner_task'],
			output_json=schema.ContentPlannerOutput,
			
		)
	
	@task
	def brand_monitor_task(self) -> Task:
		return Task(
			config=self.tasks_config['brand_monitor_task'],
			output_json=schema.BrandMonitorOutput,
					
		)
	
	@task
	def influencer_scout_task(self) -> Task:
		return Task(
			config=self.tasks_config['influencer_scout_task'],
			output_json=schema.InfluencerScoutOutput,
		
		)
	
	@task
	def customer_engagement_task(self) -> Task:
		return Task(
			config=self.tasks_config['customer_engagement_task'],
			output_json=schema.CustomerEngagementOutput,
		
			
		)
	
	@task
	def metrics_analyst_task(self) -> Task:
		return Task(
			config=self.tasks_config['metrics_analyst_task'],
			output_json=schema.MetricsAnalysisOutput,
	
		)
	
	@task
	def hashtag_strategy_task(self) -> Task:
		return Task(
			config=self.tasks_config['hashtag_strategy_task'],
			output_json=schema.HashtagStrategyOutput,
	
			
		)
	
	@task
	def campaign_design_task(self) -> Task:
		return Task(
			config=self.tasks_config['campaign_design_task'],
			output_json=schema.CampaignDesignOutput,

		)
	
	@task
	def caption_creation_task(self) -> Task:
		return Task(
			config=self.tasks_config['caption_creation_task'],
			output_json=schema.CaptionCreationOutput,

		)
	
	@task
	def scriptwriting_task(self) -> Task:
		return Task(
			config=self.tasks_config['scriptwriting_task'],
			output_json=schema.ScriptWritingOutput,
			
		)
		
	@crew
	def crew(self) -> Crew:
		"""Creates the SocialMediaCrew crew"""
		

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			
		)
