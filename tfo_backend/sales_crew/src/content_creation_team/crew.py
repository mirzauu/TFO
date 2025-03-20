from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool,EXASearchTool,DirectoryReadTool
from sales_crew.src.content_creation_team.tools.task_status import TaskStatusUpdate
from dotenv import load_dotenv
import sales_crew.src.content_creation_team.main as main
from sales_crew.src.content_creation_team.schema import SalesBrochure,PresentationOutput,EmailTemplateOutput,ProductDescriptionOutput,SocialMediaContentOutput
load_dotenv()

@CrewBase
class ContentCreationTeam():
	"""ContentCreationTeam crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def sales_brochure_specialist(self) -> Agent:
		return Agent(
			config=self.agents_config['sales_brochure_specialist'],
			verbose=True,
			tools=[SerperDevTool(),TaskStatusUpdate()]
		)

	@agent
	def email_template_creator(self) -> Agent:
		return Agent(
			config=self.agents_config['email_template_creator'],
			verbose=True,
			tools=[SerperDevTool(),TaskStatusUpdate()]
		)
	
	@agent
	def product_description_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['product_description_writer'],
			verbose=True,
			tools=[SerperDevTool(),TaskStatusUpdate()]
		)
	
	@agent
	def presentation_designer(self) -> Agent:
		return Agent(
			config=self.agents_config['presentation_designer'],
			verbose=True,
			tools=[SerperDevTool(),TaskStatusUpdate()]
		)
	
	@agent
	def social_media_content_creator(self) -> Agent:
		return Agent(
			config=self.agents_config['social_media_content_creator'],
			verbose=True,
			tools=[SerperDevTool(),TaskStatusUpdate()]
		)

	@task
	def sales_brochure_specialist_task(self) -> Task:
		return Task(
			config=self.tasks_config['sales_brochure_specialist_task'],
			output_json=SalesBrochure,
			callback=lambda result: main.task_callback(result=result, task_name="Sales Brochure Specialist",formate="brochure"),

		)

	@task
	def email_template_creator_task(self) -> Task:
		return Task(
			config=self.tasks_config['email_template_creator_task'],
			output_pydantic=EmailTemplateOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Email Template Creation",formate="email templates"),

		)
	
	@task
	def product_description_writer_task(self) -> Task:
		return Task(
			config=self.tasks_config['product_description_writer_task'],
			output_pydantic=ProductDescriptionOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Product Description Writing",formate="discription"),

		)
	
	@task
	def presentation_designer_task(self) -> Task:
		return Task(
			config=self.tasks_config['presentation_designer_task'],
			output_pydantic=PresentationOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Presentation Design",formate="slides"),

		)
	
	@task
	def social_media_content_creator_task(self) -> Task:
		return Task(
			config=self.tasks_config['social_media_content_creator_task'],
			output_pydantic=SocialMediaContentOutput,
		    callback=lambda result: main.task_callback(result=result, task_name="Social Media Content Creation",formate="posts"),


		)

	@crew
	def crew(self) -> Crew:
		"""Creates the ContentCreationTeam crew"""

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			verbose=True,
			process=Process.sequential, 
		)
# Agent: Sales Pitch Specialist
## Final Answer:
