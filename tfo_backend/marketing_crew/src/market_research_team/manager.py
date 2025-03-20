from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool,ScrapeWebsiteTool
from dotenv import load_dotenv
from typing import Optional
from pydantic import BaseModel,Field

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
			tools=[SerperDevTool()],
			verbose=True
		)

	@agent
	def survey_designer(self) -> Agent:
		return Agent(
			config=self.agents_config['survey_designer'],
			verbose=True
		)
	
	@agent
	def trend_spotter(self) -> Agent:
		return Agent(
			config=self.agents_config['trend_spotter'],
			tools=[SerperDevTool(),ScrapeWebsiteTool()],
			verbose=True
		)

	@agent
	def competitor_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['competitor_analyst'],
			tools=[SerperDevTool(),ScrapeWebsiteTool()],
			verbose=True
		)

	@agent
	def demographic_specialist(self) -> Agent:
		return Agent(
			config=self.agents_config['demographic_specialist'],
			tools=[SerperDevTool()],
			verbose=True
		)
	
	@agent
	def persona_creator(self) -> Agent:
		return Agent(
			config=self.agents_config['persona_creator'],
			tools=[SerperDevTool()],
			verbose=True
		)
	
	@agent
	def geo_market_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['geo_market_analyst'],
			tools=[SerperDevTool()],
			verbose=True
		)

	@agent
	def sentiment_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['sentiment_analyst'],
			tools=[SerperDevTool(),ScrapeWebsiteTool()],
			verbose=True
		)
	
	@agent
	def gap_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['gap_analyst'],
			tools=[SerperDevTool(),ScrapeWebsiteTool()],
			verbose=True
		)
	
	@agent
	def strategic_planner(self) -> Agent:
		return Agent(
			config=self.agents_config['strategic_planner'],
			tools=[SerperDevTool()],
			verbose=True
		)

	
	@task
	def review_analyst_task(self) -> Task:
		return Task(
			config=self.tasks_config['review_analyst_task'],
			#output_file='review.md'
		)

	@task
	def survey_designer_task(self) -> Task:
		return Task(
			config=self.tasks_config['survey_designer_task'],
			#output_file='survey.md'
		)
	
	@task
	def trend_spotter_task(self) -> Task:
		return Task(
			config=self.tasks_config['trend_spotter_task'],
			#output_file='trends.md'
		)

	@task
	def competitor_analyst_task(self) -> Task:
		return Task(
			config=self.tasks_config['competitor_analyst_task'],
			#output_file='competitors.md'
		)
	
	@task
	def demographic_specialist_task(self) -> Task:
		return Task(
			config=self.tasks_config['demographic_specialist_task'],
			#output_file='demographics.md'
		)
	
	@task
	def persona_creator_task(self) -> Task:
		return Task(
			config=self.tasks_config['persona_creator_task'],
			#output_file='personas.md'
		)
	
	@task
	def geo_market_analyst_task(self) -> Task:
		return Task(
			config=self.tasks_config['geo_market_analyst_task'],
			#output_file='market_analysis.md'
		)
	
	@task
	def sentiment_analyst_task(self) -> Task:
		return Task(
			config=self.tasks_config['sentiment_analyst_task'],
			#output_file='sentiment_analysis.md'
		)
	
	@task
	def gap_analyst_task(self) -> Task:
		return Task(
			config=self.tasks_config['gap_analyst_task'],
			#output_file='gap_analysis.md'
		)
	
	@task
	def strategic_planner_task(self) -> Task:
		return Task(
			config=self.tasks_config['strategic_planner_task'],
			#output_file='strategy_planner.md'
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
				**Task Overview:**  
				Analyze the user's input (`{human_task}`) within the context of previous messages (`{context}`).  
				Respond as a human would, ensuring continuity and relevance in the conversation.  

				### **Steps to Follow:**  
				1. **Understand User Input**: Identify whether the user is asking a question, making a request, or greeting.  
				2. **Review Conversation Context**: Use `{context}` to understand past interactions and provide a relevant, coherent response.  
				3. **Generate a Thoughtful Reply**:  
				- If the user is greeting, respond in a natural and friendly manner.  
				- If the user asks a question, answer it using previous context when relevant.  
				- If more details are needed to complete the request, ask a **follow-up question**.  
				4. **Ensure a Human-Like Response**: The response should be clear, natural, and engaging, as if a human is responding.  
				"""
			),
			expected_output="""
			- A **natural, human-like response** considering the context of previous messages.  
			- If the user asks a question, the answer should integrate relevant information from past messages.  
			- If additional details are needed, ask a **follow-up question** to clarify before proceeding.  
			
			**Example Responses:**  

			**Case 1: Greeting**  
			**User:** "Hi"  
			**Response:** "Hey there! How's your day going?"  

			**Case 2: Context-Based Answer**  
			**User:** "Can you remind me of the agent’s capabilities?"  
			**Context:** "User previously discussed AI avatars answering questions on their website."  
			**Response:** "Sure! The agent can handle AI-driven avatars that answer customer queries on a website. Let me know if you need specifics!"  

			**Case 3: Follow-Up Required**  
			**User:** "How do I integrate it?"  
			**Context:** "User asked about AI avatars but didn't specify the platform."  
			**Response:** "Are you looking to integrate the AI avatar into a website, mobile app, or another platform?"  
			"""
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the ProjectPlanner crew"""
		return Crew(
            agents=[self.review_analyst(),
					self.survey_designer(),
					self.trend_spotter(),
					self.competitor_analyst(),
                    self.demographic_specialist(),
                    self.persona_creator(),
                    self.geo_market_analyst(),
                    self.sentiment_analyst(),
                    self.gap_analyst(),
                    self.strategic_planner(),],
			tasks=[self.process_pending_tasks_task(),],
			process=Process.hierarchical,
			verbose=True,
			manager_agent=self.manager(),
    )

