from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool,ScrapeWebsiteTool
from marketing_crew.src.market_research_team.tools.task_status import TaskStatusUpdate
from dotenv import load_dotenv
from typing import Optional
from pydantic import BaseModel,Field
import marketing_crew.src.market_research_team.main as main
 # Import task_callback from main.py
import marketing_crew.src.market_research_team.schema as market_schema
load_dotenv()




@CrewBase
class MarketResearchTeam():
	"""MarketResearchTeam crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'


	@agent
	def review_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['review_analyst'],
			tools=[SerperDevTool(),],
			verbose=True
		)

	@agent
	def survey_designer(self) -> Agent:
		return Agent(
			config=self.agents_config['survey_designer'],
			verbose=True,
			tools=[]
		)
	
	@agent
	def trend_spotter(self) -> Agent:
		return Agent(
			config=self.agents_config['trend_spotter'],
			tools=[SerperDevTool(),ScrapeWebsiteTool(),],
			verbose=True
		)

	@agent
	def competitor_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['competitor_analyst'],
			tools=[SerperDevTool(),ScrapeWebsiteTool(),],
			verbose=True
		)

	@agent
	def demographic_specialist(self) -> Agent:
		return Agent(
			config=self.agents_config['demographic_specialist'],
			tools=[SerperDevTool(),],
			verbose=True
		)
	
	@agent
	def persona_creator(self) -> Agent:
		return Agent(
			config=self.agents_config['persona_creator'],
			tools=[SerperDevTool(),],
			verbose=True
		)
	
	@agent
	def geo_market_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['geo_market_analyst'],
			tools=[SerperDevTool(),],
			verbose=True
		)

	@agent
	def sentiment_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['sentiment_analyst'],
			tools=[SerperDevTool(),ScrapeWebsiteTool(),],
			verbose=True
		)
	
	@agent
	def gap_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['gap_analyst'],
			tools=[SerperDevTool(),ScrapeWebsiteTool(),],
			verbose=True
		)
	
	@agent
	def strategic_planner(self) -> Agent:
		return Agent(
			config=self.agents_config['strategic_planner'],
			tools=[SerperDevTool(),],
			verbose=True
		)
	
	@task
	def review_analyst_task(self) -> Task:
		return Task(
			config=self.tasks_config['review_analyst_task'],
			output_json=market_schema.ReviewAnalysisOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Review Analysis",formate="competitor analyst"),

		)

	@task
	def survey_designer_task(self) -> Task:
		return Task(
			config=self.tasks_config['survey_designer_task'],
			output_json=market_schema.SurveyOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Survey Design",formate="survey out"),

		)
	
	@task
	def trend_spotter_task(self) -> Task:
		return Task(
			config=self.tasks_config['trend_spotter_task'],
			output_json=market_schema.TrendSpotterOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Trend Spotting",formate="Analysis report"),

		)

	@task
	def competitor_analyst_task(self) -> Task:
		return Task(
			config=self.tasks_config['competitor_analyst_task'],
			output_json=market_schema.CompetitorAnalysisOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Competitor Analysis",formate="competitor analyst"),

		)
	
	@task
	def demographic_specialist_task(self) -> Task:
		return Task(
			config=self.tasks_config['demographic_specialist_task'],
			output_json=market_schema.DemographicSpecialistOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Demographic Analysis",formate="sales pitch"),

		)
	
	@task
	def persona_creator_task(self) -> Task:
		return Task(
			config=self.tasks_config['persona_creator_task'],
			output_json=market_schema.PersonaCreationOutput,
						callback=lambda result: main.task_callback(result=result, task_name="Persona Creation",formate="sales pitch"),
		)
	
	@task
	def geo_market_analyst_task(self) -> Task:
		return Task(
			config=self.tasks_config['geo_market_analyst_task'],
			output_json=market_schema.GeoMarketAnalysisOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Geographical Market Analysis",formate="Analysis report"),

		)
	
	@task
	def sentiment_analyst_task(self) -> Task:
		return Task(
			config=self.tasks_config['sentiment_analyst_task'],
			output_json=market_schema.SentimentAnalysisOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Sentiment Analysis",formate="Analysis report"),
		)
	
	@task
	def gap_analyst_task(self) -> Task:
		return Task(
			config=self.tasks_config['gap_analyst_task'],
			output_json=market_schema.GapAnalysisOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Gap Analysis",formate="competitor analyst"),
		)
	
	@task
	def strategic_planner_task(self) -> Task:
		return Task(
			config=self.tasks_config['strategic_planner_task'],
			output_json=market_schema.StrategicPlannerOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Strategic Planning",formate='price report'),

		)
	

	@crew
	def crew(self) -> Crew:
		"""Creates the MarketResearchTeam crew"""

		return Crew(
			agents=self.agents,
			tasks=self.tasks,
			rocess=Process.sequential,
			verbose=True,
		)

    