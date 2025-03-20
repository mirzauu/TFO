from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from sales_crew.src.lead_generation_team.tools.task_status import TaskStatusUpdate
from dotenv import load_dotenv
import sales_crew.src.lead_generation_team.main as main
import sales_crew.src.lead_generation_team.schema as lead_schema
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
            tools=[SerperDevTool()],
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
            tools=[SerperDevTool()],
            verbose=True
        )


    @task
    def lead_identifier_task(self) -> Task:
        return Task(
            config=self.tasks_config['lead_identifier_task'],
            output_json=lead_schema.LeadIdentifierOutput,
        )

    @task
    def research_analyst_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_analyst_task'],
            output_json=lead_schema.ResearchAnalystOutput,
        )

    @task
    def social_media_extractor_task(self) -> Task:
        return Task(
            config=self.tasks_config['social_media_extractor_task'],
            output_json=lead_schema.SocialMediaExtractorOutput,
        )

    @task
    def competitor_analyst_task(self) -> Task:
        return Task(
            config=self.tasks_config['competitor_analyst_task'],
            output_json=lead_schema.CompetitorAnalysisOutput,
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the LeadGenerationTeam crew"""
        
        return Crew(
            agents= self.agents,
            tasks=self.tasks,
            process=Process.sequential,  
            verbose=True,
        )