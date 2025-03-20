from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

from dotenv import load_dotenv
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

load_dotenv()

@CrewBase
class SocialMediaCrew:
    """Social Media Manager crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def competitor_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['competitor_analyst'],
            tools=[SerperDevTool(), WebsiteSearchTool(), SocialMediaAnalyticsTool(), TaskStatusUpdate()],
            verbose=True
        )

    @agent
    def content_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['content_planner'],
            tools=[CSVTool(), CalendarPlannerTool(), TaskStatusUpdate()],
            verbose=True
        )

    @agent
    def brand_monitor(self) -> Agent:
        return Agent(
            config=self.agents_config['brand_monitor'],
            tools=[SocialMediaListeningTool(), GoogleAlertsTool(), TaskStatusUpdate()],
            verbose=True
        )

    @agent
    def influencer_scout(self) -> Agent:
        return Agent(
            config=self.agents_config['influencer_scout'],
            tools=[TwitterSearchTool(), InstagramScraperTool(), InfluencerFinderTool(), TaskStatusUpdate()],
            verbose=True
        )

    @agent
    def customer_engagement_expert(self) -> Agent:
        return Agent(
            config=self.agents_config['customer_engagement_expert'],
            tools=[OpenAIAgentMessageTool(), DirectMessageTemplateTool(), TaskStatusUpdate()],
            verbose=True
        )

    @agent
    def metrics_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['metrics_analyst'],
            tools=[OpenAIAgentMessageTool(), DirectMessageTemplateTool(), TaskStatusUpdate(), SocialMediaMetricsTool()],
            verbose=True
        )

    @agent
    def hashtag_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['hashtag_strategist'],
            tools=[KeywordResearchTool(), HashtagGeneratorTool(), TaskStatusUpdate()],
            verbose=True
        )

    @agent
    def campaign_designer(self) -> Agent:
        return Agent(
            config=self.agents_config['campaign_designer'],
            tools=[CampaignDesignerTool(), TaskStatusUpdate()],
            verbose=True
        )

    @agent
    def caption_creator(self) -> Agent:
        return Agent(
            config=self.agents_config['caption_creator'],
            tools=[OpenAIAgentCaptionTool(), CaptionRepositoryTool(), TaskStatusUpdate()],
            verbose=True
        )

    @agent
    def script_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['script_writer'],
            tools=[VideoScriptTool(), OpenAIAgentScriptTool(), TaskStatusUpdate()],
            verbose=True
        )

    @task
    def competitor_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['competitor_analysis_task'],
            output_file='competitor_analysis_task_report.md'
        )

    @task
    def content_planner_task(self) -> Task:
        return Task(
            config=self.tasks_config['content_planner_task'],
            output_file='content_planner_task_report.md'
        )

    @task
    def brand_monitor_task(self) -> Task:
        return Task(
            config=self.tasks_config['brand_monitor_task'],
            output_file='brand_monitor_task_report.md'
        )

    @task
    def influencer_scout_task(self) -> Task:
        return Task(
            config=self.tasks_config['influencer_scout_task'],
            output_file='influencer_scout_task_report.md'
        )

    @task
    def customer_engagement_task(self) -> Task:
        return Task(
            config=self.tasks_config['customer_engagement_task'],
            output_file='customer_engagement_task_report.md'
        )

    @task
    def metrics_analyst_task(self) -> Task:
        return Task(
            config=self.tasks_config['metrics_analyst_task'],
            output_file='metrics_analyst_task_report.md'
        )

    @task
    def hashtag_strategy_task(self) -> Task:
        return Task(
            config=self.tasks_config['hashtag_strategy_task'],
            output_file='hashtag_strategy_task_report.md'
        )

    @task
    def campaign_design_task(self) -> Task:
        return Task(
            config=self.tasks_config['campaign_design_task'],
            output_file='campaign_design_task_report.md'
        )

    @task
    def caption_creation_task(self) -> Task:
        return Task(
            config=self.tasks_config['caption_creation_task'],
            output_file='caption_creation_task_report.md'
        )

    @task
    def scriptwriting_task(self) -> Task:
        return Task(
            config=self.tasks_config['scriptwriting_task'],
            output_file='scriptwriting_task_report.md'
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
                """
            ),
            expected_output="""
            The task provided by the user should be executed by the appropriate agent, and the results obtained by the agent should be shown to the user.
            If the task cannot be executed, the user should be informed with a clear explanation.
            """,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[
                self.competitor_analyst(), self.content_planner(), self.brand_monitor(),
                self.influencer_scout(), self.customer_engagement_expert(), self.metrics_analyst(),
                self.hashtag_strategist(), self.campaign_designer(), self.caption_creator(),
                self.script_writer()
            ],
            tasks=[self.process_pending_tasks_task()],
            process=Process.hierarchical,
            verbose=True,
            manager_agent=self.manager()
        )
