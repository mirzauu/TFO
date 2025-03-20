from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
import sales_crew.src.crm_team.main as main
load_dotenv()
import sales_crew.src.crm_team.schema as crm_schema

@CrewBase
class CrmTeam():
	"""CrmTeam crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def follow_up_manager(self) -> Agent:
		return Agent(
			config=self.agents_config['follow_up_manager'],
			verbose=True,
			tools=[SerperDevTool()]
		)

	@agent
	def feedback_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['feedback_analyst'],
			verbose=True,
			tools=[SerperDevTool()]
		)

	@agent
	def customer_segmentation_expert(self) -> Agent:
		return Agent(
			config=self.agents_config['customer_segmentation_expert'],
			verbose=True,
			tools=[SerperDevTool()]
		)
	
	@agent
	def cross_sell_strategist(self) -> Agent:
		return Agent(
			config=self.agents_config['cross_sell_strategist'],
			verbose=True
		)
	
	@agent
	def survey_specialist(self) -> Agent:
		return Agent(
			config=self.agents_config['survey_specialist'],
			verbose=True
		)
	
	@task
	def follow_up_manager_task(self) -> Task:
		return Task(
			config=self.tasks_config['follow_up_manager_task'],
			output_json=crm_schema.FollowUpEmailOutput,
		)

	@task
	def feedback_analyst_task(self) -> Task:
		return Task(
			config=self.tasks_config['feedback_analyst_task'],
			output_json=crm_schema.FeedbackAnalysisOutput,
		)
	
	@task
	def customer_segmentation_task(self) -> Task:
		return Task(
			config=self.tasks_config['customer_segmentation_task'],
			output_json=crm_schema.CustomerSegmentationOutput,
		)
	
	@task
	def cross_sell_strategist_task(self) -> Task:
		return Task(
			config=self.tasks_config['cross_sell_strategist_task'],
			output_json=crm_schema.CrossSellStrategistOutput,
		)
	
	@task
	def survey_specialist_task(self) -> Task:
		return Task(
			config=self.tasks_config['survey_specialist_task'],
			output_json=crm_schema.SurveySpecialistOutput,
		
		)


	@crew
	def crew(self) -> Crew:
		"""Creates the CrmTeam crew"""

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
		)
