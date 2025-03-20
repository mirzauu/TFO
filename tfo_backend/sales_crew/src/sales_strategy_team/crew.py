from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool,ScrapeWebsiteTool,FileReadTool,CodeInterpreterTool
from sales_crew.src.sales_strategy_team.tools.task_status import TaskStatusUpdate 
from dotenv import load_dotenv
import sales_crew.src.sales_strategy_team.main as main
load_dotenv()
import sales_crew.src.sales_strategy_team.schema as sales_schema



@CrewBase
class SalesStrategyTeam():
	"""SalesStrategyTeam crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'


	@agent
	def market_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['market_analyst'],
			verbose=True,
			tools=[SerperDevTool()],
		)
	

	@agent
	def swot_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['swot_analyst'],
			verbose=True,
			tools=[SerperDevTool()]
		)
	
	@agent
	def competitor_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['competitor_analyst'],
			verbose=True,
			tools=[SerperDevTool()]
		)
	
	@agent
	def pricing_strategist(self) -> Agent:
		return Agent(
			config=self.agents_config['pricing_strategist'],
			verbose=True,
			tools=[SerperDevTool()]
		)
	
	@agent
	def sales_pitch_specialist(self) -> Agent:
		return Agent(
			config=self.agents_config['sales_pitch_specialist'],
			verbose=True,
			tools=[SerperDevTool()]
		)


	@task
	def market_research_analyst_task(self) -> Task:
		return Task(
			config=self.tasks_config['market_analyst_task'],
			output_json=sales_schema.MarketAnalystOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Market Research Analyst",formate="Analysis report"),
		)
	

	@task
	def SWOT_analysis_evaluator_task(self) -> Task:
		return Task(
			config=self.tasks_config['swot_analyst_task'],
			output_json=sales_schema.SWOTAnalysisOutput,
			callback=lambda result: main.task_callback(result=result, task_name="SWOT Analysis Evaluator",formate="swot analysis"),
		)
	
	@task
	def competitor_analyst_task(self) -> Task:
		return Task(
			config=self.tasks_config['competitor_analyst_task'],
			output_json=sales_schema.CompetitorAnalysisOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Competitor Analyst",formate="competitor analyst"),
		)

	@task
	def pricing_strategist_task(self) -> Task:
		return Task(
			config=self.tasks_config['pricing_strategist_task'],
			output_json=sales_schema.PricingModelOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Pricing Strategist",formate="price report"),
		)
	
	@task
	def tailored_sales_pitch_specialist_task(self) -> Task:
		return Task(
			config=self.tasks_config['sales_pitch_specialist_task'],
			output_json=sales_schema.SalesPitchOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Tailored Sales Pitch Specialist",formate="sales pitch"),
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the SalesStrategyTeam crew"""

		return Crew(
			agents=self.agents,
			tasks=self.tasks,
			process=Process.sequential,
			verbose=True,
		)



