from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool,ScrapeWebsiteTool,FileReadTool,CodeInterpreterTool

from dotenv import load_dotenv

load_dotenv()

@CrewBase
class SalesStrategyTeam():
	"""SalesStrategyTeam crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'


	@agent
	def market_research_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['market_research_analyst'],
			verbose=True,
			tools=[SerperDevTool(),FileReadTool()]
		)
	
	@agent
	def Code_Interpreter_Tool(self) -> Agent:
		return Agent(
			config=self.agents_config['Code_Interpreter_Tool'],
			verbose=True,
			tools=[SerperDevTool(),CodeInterpreterTool()]
		)

	@agent
	def SWOT_analysis_evaluator(self) -> Agent:
		return Agent(
			config=self.agents_config['SWOT_analysis_evaluator'],
			verbose=True,
			tools=[SerperDevTool()]
		)
	
	@agent
	def competitor_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['competitor_analyst'],
			verbose=True,
			tools=[SerperDevTool(),FileReadTool()]
		)
	
	@agent
	def pricing_strategist(self) -> Agent:
		return Agent(
			config=self.agents_config['pricing_strategist'],
			verbose=True,
			tools=[SerperDevTool()]
		)
	
	@agent
	def tailored_sales_pitch_specialist(self) -> Agent:
		return Agent(
			config=self.agents_config['tailored_sales_pitch_specialist'],
			verbose=True,
			tools=[SerperDevTool()]
		)


	@task
	def market_research_analyst_task(self) -> Task:
		return Task(
			config=self.tasks_config['market_research_analyst_task'],
		)
	
	@task
	def Code_Interpreter_Tool_task(self) -> Task:
		return Task(
			config=self.tasks_config['Code_Interpreter_Tool_task'],
		)

	@task
	def SWOT_analysis_evaluator_task(self) -> Task:
		return Task(
			config=self.tasks_config['SWOT_analysis_evaluator_task'],
		)
	
	@task
	def competitor_analyst_task(self) -> Task:
		return Task(
			config=self.tasks_config['competitor_analyst_task'],
		)

	@task
	def pricing_strategist_task(self) -> Task:
		return Task(
			config=self.tasks_config['pricing_strategist_task'],
		)
	
	@task
	def tailored_sales_pitch_specialist_task(self) -> Task:
		return Task(
			config=self.tasks_config['tailored_sales_pitch_specialist_task'],
		)

	@agent
	def manager(self) -> Agent:
		return Agent(
			role="Task Manager",
            goal="Efficiently identify, delegate, and oversee the execution of tasks based on user input, ensuring timely and accurate completion while maintaining clear communication with the user.",
            verbose=True,
            tools=[],
            backstory=(
                """
                You are a highly organized and detail-oriented professional with extensive experience in task management and delegation. 
                Your expertise lies in understanding complex requirements, matching tasks to the right resources, and ensuring seamless execution.
                With a strong focus on efficiency and accountability, you thrive in dynamic environments where multiple tasks need to be managed simultaneously.
                Your ability to communicate clearly and monitor progress ensures that tasks are completed on time and meet the highest standards of quality.
                """
            ),
            allow_delegation=True,
            memory=True
        )
	@task
	def process_pending_tasks_task(self) -> Task:
		return Task(
            description=(
		"""
		Take the task provided by the user (`{human_task}`) and determine which agent is best suited to execute it based on the agent's role and capabilities.

		Steps to follow:
		1. **Analyze the Task**: Carefully read and understand the task provided by the user. Identify the key requirements and objectives of the task.
		2. **Match Task to Agent**: Review the roles and capabilities of all available agents. Match the task to the most appropriate agent based on their expertise and tools.
		3. **Delegate the Task**: If a suitable agent is found, delegate the task to that agent and ensure they execute it properly. Provide the agent with all necessary information and context.
		4. **Handle Unmatched Tasks**: If no suitable agent is available to handle the task, inform the user that the task cannot be executed and provide a reason why.
		5. **Monitor Progress**: Continuously monitor the progress of the task. If the task fails or encounters issues, update the task status accordingly and inform the user.
		6. **Ensure Completion**: Once the task is completed, verify that the output meets the user's expectations and update the task status to "COMPLETED".

		Ensure that all tasks are executed efficiently and that the user is kept informed of the progress and any issues that arise.
		"""
		),
		expected_output="""
		The task provided by the user should be executed by the appropriate agent, and the results obtained by the agent should be shown to the user.
		If the task cannot be executed, the user should be informed with a clear explanation.
		The task status should be updated dynamically based on the progress and outcome of the task.
		""",
        )
	@crew
	def crew(self) -> Crew:
		"""Creates the ProjectPlanner crew"""
		return Crew(
            agents=[self.market_research_analyst(),
					self.SWOT_analysis_evaluator(),
					self.competitor_analyst(),
					self.pricing_strategist(),
					self.tailored_sales_pitch_specialist()],
			tasks=[self.process_pending_tasks_task(),],
			process=Process.hierarchical,
			verbose=True,
			manager_agent=self.manager(),
    )

