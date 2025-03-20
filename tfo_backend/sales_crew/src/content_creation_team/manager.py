from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool,EXASearchTool,DirectoryReadTool
from sales_crew.src.content_creation_team.tools.task_status import TaskStatusUpdate,PresentationDesignerTool
from dotenv import load_dotenv

load_dotenv()

@CrewBase
class ContentCreationTeam():
	"""ContentCreationTeam crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def conversational_agent(self) -> Agent:
		return Agent(
			role="Conversational Assistant",
			goal="Engage users in friendly and informative conversations while guiding them to the right services.",
			verbose=True,
			memory=True,
			allow_delegation=False,  # This agent won't handle task execution but will guide users.
			tools=[],
			backstory=(
				"""
				You are a friendly and knowledgeable assistant designed to engage in natural conversations with users. 
				You provide a warm and professional experience, ensuring users feel heard and guided in the right direction. 
				You excel at handling greetings, small talk, and general inquiries about the team's capabilities.
				If a user requests something outside the team's expertise, you respond in a polite and helpful way, offering suggestions where appropriate.
				"""
			),
		)

	@agent
	def sales_brochure_specialist(self) -> Agent:
		"""Sales Brochure agent"""
		return Agent(
			config=self.agents_config['sales_brochure_specialist'],
			verbose=True,
			tools=[SerperDevTool(),TaskStatusUpdate()]
		)

	@agent
	def email_template_creator(self) -> Agent:
		"""Email Template agent"""
		return Agent(
			config=self.agents_config['email_template_creator'],
			verbose=True,
			tools=[SerperDevTool(),TaskStatusUpdate()]
		)
	
	@agent
	def product_description_writer(self) -> Agent:
		"""Product Description Writer"""
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
			tools=[PresentationDesignerTool()]
		)
	
	@agent
	def social_media_content_creator(self) -> Agent:
		""""""
		return Agent(
			config=self.agents_config['social_media_content_creator'],
			verbose=True,
			tools=[SerperDevTool(),TaskStatusUpdate()]
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
			description = (
				 """
			chat history: {context}
			last conversation: {last_conversation}

			**Task Overview:**
			- If the input is a greeting or a casual conversation, delegate it to the Conversational Assistant and return its output.  
			- If the user asks for help understanding what the team does, delegate to the Conversational Assistant.
			- Perform semantic analysis on the chat history ({context}) and the last conversation ({last_conversation}) to extract key topics, intents, and sentiments related to the human task ({human_task}).
			- Analyze the user's request ({human_task}), considering insights from past conversations, to determine if it aligns with the team's specialties:
				- Sales brochures  
				- Email templates  
				- Product descriptions  
				- Sales presentations  
				- Social media content  
			- If the request is outside this scope, politely decline while maintaining a friendly tone.

			### **Steps to Follow:**
			1. Check if the input is a greeting, casual conversation, or general inquiry. If so, delegate it to the Conversational Assistant and return an appropriate response.
			2. If the user asks for help understanding what the team does, have the Conversational Assistant explain the team's expertise.
			3. Perform semantic analysis on the chat history and last conversation to uncover nuances, correlations, or additional details related to the human task.
			- Identify key topics, intents, and sentiments.
			- Look for patterns or recurring themes.
			4. Evaluate whether the analyzed request falls within the team's specialties. If it does, assign the task to the appropriate specialist and **wait for their output**.
			5. If the request is determined to be outside the team's capabilities, respond with:
			"I’m sorry, but this request falls outside our team's expertise. We specialize in sales brochures, email templates, product descriptions, sales presentations, and social media content. Let me know if there’s anything else I can assist you with!"
			6. If the user's request is unclear or incomplete, ask follow-up questions to gather more information before proceeding.
			7. For requests related to sales brochures, email templates, product descriptions, sales presentations, or social media content:
				- Analyze the chat history for context (e.g., brand voice, past projects, user preferences)
				- Cross-reference the last conversation for continuity
				- If critical details are missing (e.g., audience, tone, platform, content specifics), ask follow-up questions using this format:
					"To help create your [task type], I need some additional details: 
					- What's the target audience? 
					- Preferred tone (professional/friendly/casual)? 
					- Any specific requirements or examples to follow?"

			### **Expected Output:**
			- For delegated tasks: Return the **final output generated by the specialist** (e.g., the Instagram post content).
			- For out-of-scope requests: Politely decline with a predefined message.
			- For unclear requests: Ask follow-up questions to clarify the user's intent.
			"""
			),
			expected_output="""
				- For delegated tasks: Return the **final output generated by the specialist** (e.g., the Instagram post content).
				- For out-of-scope requests: Politely decline with a predefined message.
				- For unclear requests: Ask follow-up questions to clarify the user's intent.
			"""
		)
	
	@crew
	def crew(self) -> Crew:
		"""Creates the ProjectPlanner crew"""
		return Crew(
            agents=[self.conversational_agent(),
					self.sales_brochure_specialist(),
                    self.email_template_creator(),
                    self.product_description_writer(),
                    self.presentation_designer(),
                    self.social_media_content_creator(),],
            tasks=[self.process_pending_tasks_task(),],
            process=Process.hierarchical,
            verbose=True,
            manager_agent=self.manager(),
    )