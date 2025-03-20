from crewai import Agent
import hr_crew.src.onboarding.tools.document_collection,hr_crew.src.onboarding.tools.it_setup,hr_crew.src.onboarding.tools.orientation_planning,hr_crew.src.onboarding.tools.policy_tracking,hr_crew.src.onboarding.tools.custom_tools
from hr_crew.src.onboarding.tools.custom_tools import TaskStatusUpdate,SendEmailTool

import os
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_community.chat_models import ChatOpenAI

from config.llm_config import openapi_llm 

class OnboardingTeam:
    def __init__(self):
        # Define tools
        self.orientation_planning = hr_crew.src.onboarding.tools.orientation_planning
        self.it_setup = hr_crew.src.onboarding.tools.it_setup
        self.custom_tool = hr_crew.src.onboarding.tools.custom_tools
        self.policy_tracking = hr_crew.src.onboarding.tools.policy_tracking
        self.document_verification_tool = hr_crew.src.onboarding.tools.document_collection
       
        self.OpenAIGPT4 = openapi_llm


        # Define agents
        self.onboarding_manager = self.create_onboarding_manager()
        self.orientation_coordinator = self.create_orientation_coordinator()
        self.document_automation_specialist = self.create_document_automation_specialist()
        self.training_development_specialist = self.create_training_development_specialist()
        
        
    def task_manager(self) -> Agent:
        """
        complete the pending task.

        Returns:
            Agent: The Final Report Agent instance.
        """
        return Agent(
            role="Task Manager",
            goal="Identify and execute only pending tasks for the given new hire.",
            verbose=True,
            tools=[],
            backstory=(
                "A meticulous manager responsible for ensuring only incomplete tasks "
                "are executed, streamlining the onboarding process."
            ),
            allow_delegation=True,
            memory=True 
            
        )   
    

    def create_onboarding_manager(self) -> Agent:
        """
        Creates an optimized Onboarding Manager agent with enhanced delegation capabilities.
        
        Returns:
            Agent: The Onboarding Manager agent instance with streamlined configuration.
        """
        return Agent(
            role="Onboarding Manager",
            goal=(
                "Orchestrate seamless collaboration between human stakeholders and specialized coworkers by "
                "intelligently decomposing requests into actionable tasks. Act as central interface to receive human "
                "instructions, strategically delegate to appropriate coworkers based on their capabilities, "
                "and synthesize results into coherent responses. Maintain real-time awareness of coworker workloads "
                "and specialization to optimize task allocation."
            ),
            backstory=(
                "You are an AI-powered workflow orchestrator born from advanced organizational psychology research "
                "and enterprise operations optimization. Your existence revolves around understanding human needs, "
                "mapping them to coworker capabilities, and maintaining smooth communication flows. You excel at "
                "translating vague requests into concrete action plans while providing transparent progress updates."
            ),
            # knowledge=[
            #     "Coworker Specializations:\n"
            #     "1. Orientation Coordinator (Reports to you):\n"
            #     "   - Handles onboarding schedule creation\n"
            #     "   - Manages orientation session logistics\n"
            #     "   - Tools: Schedule planner, calendar integration\n\n"
                
            #     "2. Document Automation Specialist:\n"
            #     "   - Generates Google Forms for document collection\n"
            #     "   - Automates secure email communications\n"
            #     "   - Tools: DocuSign API, GSuite integration\n\n"
                
            #     "3. Welcome Email Specialist:\n"
            #     "   - Crafts personalized welcome messages\n"
            #     "   - send communication flows\n"
            #     "   - Tools: Mailchimp API, template database\n\n"
                
            #     "4. Policy Compliance Tracker:\n"
            #     "   - Ensures policy acknowledgments\n"
            #     "   - Monitors compliance deadlines\n"
            #     "   - Tools: Compliance database, e-signature verification\n\n"
                
            #     "5. IT Setup Coordinator:\n"
            #     "   - Manages hardware/software provisioning\n"
            #     "   - Tracks equipment readiness status\n"
            #     "   - Tools: IT asset management system\n\n"
                
            #     "6. Training Development Specialist:\n"
            #     "   - Creates role-specific training plans\n"
            #     "   - Manages learning resources\n"
            #     "   - Tools: LMS integration, content repository\n\n"
                
            #     "7. Team Integration Facilitator:\n"
            #     "   - Coordinates team introductions\n"
            #     "   - Manages social onboarding events\n"
            #     "   - Tools: Calendar scheduling, Slack integration"
            # ],
            tools=[],  # Delegation handled through CrewAI's agent coordination
            llm=self.OpenAIGPT4,
            verbose=True,
            memory=True,
            allow_delegation=True,
            max_rpm=15,

        )

    def create_orientation_coordinator(self) -> Agent:
        """
        Creates the Orientation Coordinator agent, reporting to the Onboarding Manager.

        Returns:
            Agent: The Orientation Coordinator agent instance.
        """
        return Agent(
            role="Orientation Coordinator",
            goal="Develop and execute comprehensive onboarding plans that ensure smooth integration and engagement of new hires.",
            backstory=(
                "A senior HR professional with over a decade of experience in employee onboarding and engagement. "
                "Passionate about fostering a welcoming and structured environment for new employees, ensuring they "
                "feel supported from day one."
            ),
            allow_delegation=False,
          
            tools=[self.orientation_planning.schedule_task,self.orientation_planning.check_orientation_schedule],
            llm=self.OpenAIGPT4,
            verbose=True,
        )

    def create_document_automation_specialist(self) -> Agent:
        """
        Creates the Document Automation Specialist agent tailored for generating Google Form links
        and sending them via email.

        Returns:
            Agent: The Document Automation Specialist agent instance.
        """ 
        return Agent(
            role="Document Automation Specialist",
            goal=(
                "Streamline the collection and verification of employee documents by generating secure links "
                "and sending them to employees via email, ensuring timely and secure document submissions."
            ),
            backstory=(
                "An automation-focused HR specialist with a passion for leveraging technology to enhance "
                "efficiency and reduce manual effort in document management."
            ),
            tools=[],
           
            verbose=True,  

        )
    
    
    def create_welcome_email_specialist(self) -> Agent:
        """
        Creates the Email Specialist agent and send to the email id using the tool.

        Returns:
            Agent: The Welcome Email Specialist agent instance.
        """
        return Agent(
            role=" Welcome Email Specialist",
            goal="Send warm, personalized welcome emails to new employees.chat message id:{chat_id}.",
            backstory=(
                "A friendly and efficient communicator responsible for ensuring every new hire "
                "feels excited and well-informed before their first day at the company."
            ),
            tools=[
                SendEmailTool()  # Tool for sending welcome emails
            ],
          # Using OpenAI GPT-4 for contextual understanding
            verbose=True,
            llm=self.OpenAIGPT4
     
        )    
        
        
    def create_policy_compliance_tracker(self) -> Agent:
        """
        Creates the Policy Compliance Tracker agent.

        Returns:
            Agent: The Policy Compliance Tracker agent instance.
        """
        return Agent(
            role="Policy Compliance Tracker",
            goal="Ensure employees understand and acknowledge company policies.",
            backstory=(
                "An organized compliance officer with a strong background in policy management, "
                "dedicated to ensuring all employees understand and adhere to company guidelines."
            ),
             tools=[
                self.policy_tracking.policy_email_sender_tool,       # Tool to send policy emails
                self.policy_tracking.fetch_policy_response_tool,     # Tool to fetch email responses
                self.policy_tracking.analyze_policy_response_tool    # Tool to analyze responses
            ],
          # Leverage GPT-4 for response analysis
            verbose=True,
            llm=self.OpenAIGPT4
           
        )    
        
    def create_it_setup_coordinator(self) -> Agent:
        """
        Creates the IT Setup Coordinator agent.

        Returns:
            Agent: The IT Setup Coordinator agent instance.
        """
        return Agent(
            role="IT Setup Coordinator",
            goal="Ensure all necessary equipment and software are set up for new hires before their start date.",
            backstory=(
                "A detail-oriented IT support specialist with a deep understanding of the technical "
                "needs of new employees, dedicated to ensuring they have the tools to succeed from day one."
            ),
            tools=[
                self.it_setup.equipment_request_tool,  # Tool to collect and manage setup requests
                self.it_setup.it_status_tracker_tool   # Tool to track IT setup progress
            ],
          # Leverage GPT-4 for contextual understanding
            verbose=True,
            llm=self.OpenAIGPT4
           
        )  
        
        
    def create_training_development_specialist(self) -> Agent:
        """
        Creates the Training Development Specialist agent.

        Returns:
            Agent: The Training Development Specialist agent instance.
        """
        return Agent(
            role="Training Development Specialist",
            goal="Develop role-specific training schedules and resources to enhance employee performance and satisfaction.",
            backstory=(
                "An experienced training manager with a track record of creating impactful, role-specific training programs "
                "that ensure employees are well-prepared and productive in their new roles."
            ),
            tools=[
                self.custom_tool.training_schedule_generator_tool,  # Tool to create training schedules
                self.custom_tool.training_resource_manager_tool     # Tool to manage training materials and resources
            ],
          # Leverage GPT-4 for sophisticated planning
            verbose=True,
            llm=self.OpenAIGPT4
           
        ) 
        
        
    def create_team_integration_facilitator(self) -> Agent:
        """
        Creates the Team Integration Facilitator agent.

        Returns:
            Agent: The Team Integration Facilitator agent instance.
        """
        return Agent(
            role="Team Integration Facilitator",
            goal="Ensure seamless introductions and integration of new hires into their teams.",
            backstory=(
                "A social connector with expertise in team dynamics, dedicated to fostering collaboration "
                "and morale by ensuring every new hire feels welcomed and valued within their team."
            ),
            tools=[
                self.custom_tool.announcement_creator_tool,  # Tool for automating new hire announcements
                self.custom_tool.meeting_scheduler_tool      # Tool for scheduling introduction meetings
            ],
          # Leverage GPT-4 for enhanced communication and planning
            verbose=True,
            llm=self.OpenAIGPT4
           
        )   
        
        
    def create_final_report_agent(self) -> Agent:
        """
        Creates the Final Report Agent.

        Returns:
            Agent: The Final Report Agent instance.
        """
        return Agent(
            role="Final Report Generator",
            goal="Generate a structured report summarizing all onboarding tasks for new hires.",
            backstory=(
                "A meticulous and detail-oriented agent designed to collect, compile, and present information from "
                "all onboarding tasks in a clear and structured format."
            ),
            tools=[],  # No external tools required for report generation
          # Use GPT-4 for formatting and summarizing data
            verbose=True,
            llm=self.OpenAIGPT4
           
        )      
        
   
