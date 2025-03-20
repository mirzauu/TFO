from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
import marketing_crew.src.seo_sem_crew.main as main   
import marketing_crew.src.seo_sem_crew.schema as seo_schema
from marketing_crew.src.seo_sem_crew.tools.lang_tools import DataForSEOSerpTool
from marketing_crew.src.seo_sem_crew.tools.custom_tool import(
	 GoogleAnalyticsTool,
	 GoogleSearchConsoleTool,
	 SEMrushTool,
	 AhrefsTool,
	 MozProTool,
	 ScreamingFrogTool,
	 SitebulbAuditTool,
	 YoastOptimizationTool,
	 KWFinderTool
)
from marketing_crew.src.seo_sem_crew.tools.tasksupdate import TaskStatusUpdate
from dotenv import load_dotenv

load_dotenv()


@CrewBase
class SeoSemCrew():
	"""SeoSemCrew crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	
	@agent
	def keyword_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['keyword_researcher'],
			tools=[
				   DataForSEOSerpTool(),
		  		   SEMrushTool(),
				   AhrefsTool(),
				   KWFinderTool(),
		  		],
			verbose=True
		)

	@agent
	def competitor_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['competitor_analyst'],
			tools=[SerperDevTool(),
				   SEMrushTool(),
				   AhrefsTool(),

				   ],
			verbose=True
		)
	
	@agent
	def content_optimizer(self) -> Agent:
		return Agent(
			config=self.agents_config['content_optimizer'],
			tools=[
				YoastOptimizationTool(),
				MozProTool(),
				GoogleSearchConsoleTool(),
				
			],
			verbose=True
		)
	
	@agent
	def backlink_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['backlink_analyst'],
			tools=[
				AhrefsTool(),
				SEMrushTool(),
				MozProTool(),
			],
			verbose=True
		)
	
	@agent
	def analytics_specialist(self) -> Agent:
		return Agent(
			config=self.agents_config['analytics_specialist'],
			tools=[
				GoogleAnalyticsTool(),
				GoogleSearchConsoleTool(),
			],
			verbose=True
		)
	
	@agent
	def seo_reporter(self) -> Agent:
		return Agent(
			config=self.agents_config['seo_reporter'],
			tools=[
				SerperDevTool(),
				GoogleAnalyticsTool(),
				SEMrushTool(),
			],
			verbose=True
		)
	
	@agent
	def meta_description_creator(self) -> Agent:
		return Agent(
			config=self.agents_config['meta_description_creator'],
			tools=[
				YoastOptimizationTool(),
				MozProTool(),
			],
			verbose=True
		)
	
	@agent
	def ad_copywriter(self) -> Agent:
		return Agent(
			config=self.agents_config['ad_copywriter'],
			tools=[
				SEMrushTool(),
			],
			verbose=True
		)
	
	@agent
	def sem_campaign_manager(self) -> Agent:
		return Agent(
			config=self.agents_config['sem_campaign_manager'],
			tools=[
				GoogleAnalyticsTool(),
				SEMrushTool(),
				TaskStatusUpdate()
			],
			verbose=True
		)
	
	@agent
	def seo_auditor(self) -> Agent:
		return Agent(
			config=self.agents_config['seo_auditor'],
			tools=[
				ScreamingFrogTool(),
				SitebulbAuditTool(),
				GoogleSearchConsoleTool(),
				TaskStatusUpdate()
			],
			verbose=True
		)
	
	@agent
	def internal_link_strategist(self) -> Agent:
		return Agent(
			config=self.agents_config['internal_link_strategist'],
			tools=[
				ScreamingFrogTool(),
				MozProTool(),
				GoogleSearchConsoleTool(),
				TaskStatusUpdate()
			],
			verbose=True
		)
	
	@agent
	def content_strategist(self) -> Agent:
		return Agent(
			config=self.agents_config['content_strategist'],
			tools=[
				SEMrushTool(),
				AhrefsTool(),
				KWFinderTool(),
				TaskStatusUpdate()
			],
			verbose=True
		)

	
	@task
	def keyword_research_task(self) -> Task:
		return Task(
			config=self.tasks_config['keyword_research_task'],
			output_json=seo_schema.KeywordResearchOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Keyword Research",formate='Analysis report'),
		)

	@task
	def competitor_analysis_task(self) -> Task:
		return Task(
			config=self.tasks_config['competitor_analysis_task'],
			output_json=seo_schema.CompetitorAnalysisOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Competitor Analysis",formate='competitor analyst'),
		)
	
	@task
	def content_optimization_task(self) -> Task:
		return Task(
			config=self.tasks_config['content_optimization_task'],
			output_json=seo_schema.ContentOptimizationOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Content Optimization",formate='Analysis report'),
		)
	
	@task
	def backlink_analysis_task(self) -> Task:
		return Task(
			config=self.tasks_config['backlink_analysis_task'],
			output_json=seo_schema.BacklinkAnalysisOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Backlink Analysis",formate='Analysis report'),

		)
	
	@task
	def analytics_monitoring_task(self) -> Task:
		return Task(
			config=self.tasks_config['analytics_monitoring_task'],
			output_json=seo_schema.AnalyticsMonitoringOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Analytics Monitoring",formate='competitor analyst'),
		)
	
	@task
	def seo_reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['seo_reporting_task'],
			output_json=seo_schema.SEOReportingOutput,
			callback=lambda result: main.task_callback(result=result, task_name="SEO Reporting",formate='sales pitch'),

		)
	
	@task
	def meta_description_task(self) -> Task:
		return Task(
			config=self.tasks_config['meta_description_task'],
			output_json=seo_schema.MetaDescriptionOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Meta Description Optimization",formate='competitor analyst'),

		)
	
	@task
	def ad_copy_task(self) -> Task:
		return Task(
			config=self.tasks_config['ad_copy_task'],
			output_json=seo_schema.AdCopyOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Ad Copy Creation",formate='Analysis report'),

		)
	
	@task
	def sem_campaign_management_task(self) -> Task:
		return Task(
			config=self.tasks_config['sem_campaign_management_task'],
			output_json=seo_schema.SEMCampaignManagementOutput,
			callback=lambda result: main.task_callback(result=result, task_name="SEM Campaign Management",formate='Analysis report'),

		)
	
	@task
	def seo_audit_task(self) -> Task:
		return Task(
			config=self.tasks_config['seo_audit_task'],
			output_json=seo_schema.SEOAuditOutput,
			callback=lambda result: main.task_callback(result=result, task_name="SEO Audit",formate='competitor analyst'),

		)
	
	@task
	def internal_linking_task(self) -> Task:
		return Task(
			config=self.tasks_config['internal_linking_task'],
			output_json=seo_schema.InternalLinkingOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Internal Linking Strategy",formate='posts'),

		)
	
	@task
	def content_strategy_task(self) -> Task:
		return Task(
			config=self.tasks_config['content_strategy_task'],
			output_json=seo_schema.ContentOptimizationOutput,
			callback=lambda result: main.task_callback(result=result, task_name="Content Strategy",formate='Analysis report'),

		)
	

	@crew
	def crew(self) -> Crew:
		"""Creates the SeoSemCrew crew"""
		

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
		)

    