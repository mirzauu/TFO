from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from dotenv import load_dotenv

load_dotenv()

@CrewBase
class LeadGenerationTeam():
    """LeadGenerationTeam crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def lead_identifier(self) -> Agent:
        return Agent(
            config=self.agents_config['lead_identifier'],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            verbose=True
        )

    @agent
    def research_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['research_analyst'],
            tools=[SerperDevTool()],
            verbose=True
        )

    @agent
    def social_media_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config['social_media_extractor'],
            tools=[SerperDevTool()],
            verbose=True
        )

    @agent
    def competitor_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['competitor_analyst'],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            verbose=True
        )

    @task
    def lead_identifier_task(self) -> Task:
        return Task(
            config=self.tasks_config['lead_identifier_task'],
        )

    @task
    def research_analyst_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_analyst_task'],
        )

    @task
    def social_media_extractor_task(self) -> Task:
        return Task(
            config=self.tasks_config['social_media_extractor_task'],
        )

    @task
    def competitor_analyst_task(self) -> Task:
        return Task(
            config=self.tasks_config['competitor_analyst_task'],
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
            agents=[self.lead_identifier(),
					self.research_analyst(),
					self.social_media_extractor(),
					self.competitor_analyst(),],
			tasks=[self.process_pending_tasks_task(),],
			process=Process.hierarchical,
			verbose=True,
			manager_agent=self.manager(),
    )

