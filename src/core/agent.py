from src.core.model import ModelCore
from src.core.utils import Utils
from src.core.database import DatabaseCore
from src.core.logging_config import setup_logging
from src.core.prompts import Prompts

from smolagents import CodeAgent, OpenAIServerModel, DuckDuckGoSearchTool, Tool

from PIL import Image
import os
import logging

# Get logger for this module
logger = logging.getLogger(__name__)

class AgentCore:
    def __init__(self, model_instance: ModelCore, 
                       utils: Utils, 
                       tools: list[Tool], 
                       planning_interval: int, 
                       max_steps: int, 
                       verbosity_level: int, 
                       verbose: bool,
                       database: DatabaseCore,
                       prompts: Prompts):
        """
        Initialize the AgentCore class.

        Args:
            model_instance: The model instance to use.
            utils: The utils to use.
            tools: The tools to use.
            planning_interval: The planning interval of the agent.
            max_steps: The maximum number of steps the agent can take.
            verbosity_level: The verbosity level of the agent.
            verbose: The verbose level of the agent.
            database: The database to use.
        """
        # Configure logging based on verbosity level
        setup_logging(verbose=verbose)

        logger.info("Initializing AgentCore - - -")
        self.model_handler = model_instance
        self.serverModel = self.loadModel()
        self.tools = tools
        self.database = database
        self.utils = utils
        self.prompts = prompts
        self.managerAgent = self.agentManager(planning_interval, verbosity_level, max_steps)
        logger.info("AgentCore initialized successfully!")


    def agentManager(self, planning_interval: int, verbosity_level: int, max_steps: int) -> CodeAgent:
        """
        Load the Boss Agent.
            - tools: The tools to use. Set to self.tools.
            - model: The model to use. Set to self.serverModel.

        Args:
            max_steps: The maximum number of steps the agent can take.
            verbosity_level: The verbosity level of the agent.
        """
        logger.info("Initializing agent manager...")
        agent = CodeAgent(
            model=self.serverModel,
            tools=self.tools,
            managed_agents=[
                self.WebAgent(max_steps, verbosity_level)
            ],
            additional_authorized_imports=[],
            planning_interval=planning_interval,
            verbosity_level=verbosity_level,
            final_answer_checks=[],
            max_steps=max_steps,
        )
        logger.info("Agent manager initialized successfully")
        return agent


    def WebAgent(self, max_steps: int, verbosity_level: int) -> CodeAgent:
        """
        Loading a Web Agent.
        """
        logger.info("Loading web agent - - -")
        agent = CodeAgent(
            model=self.serverModel,
            tools=[DuckDuckGoSearchTool()],
            name="Web_Agent",
            description="A Web Agent that can search the web for information.",
            verbosity_level=verbosity_level,
            max_steps=max_steps
        )
        logger.info("Web agent loaded successfully!")
        return agent


    def runAgent(self, prompt: str, history: list[str]) -> str:
        """
        Run the agent.

        Args:
            prompt: The prompt to use.
            history: The history of the conversation.
        """
        # Format the prompt
        formatted_prompt, original_prompt = self.prompts.promptFormatter(task="chatting", prompt=prompt)

        # Save user's prompt to database before being processed
        self.database.conversation_saver(
            data={
                'role': 'user',
                'text': original_prompt
            },
            data_table='conversations'
        )
        logger.info(f"User's original prompt saved to database")

        logger.info(f"Running agent with prompt: {formatted_prompt}")
        result = self.managerAgent.run(formatted_prompt, history)
        logger.info("Agent execution completed")

        # Save system's response to database
        self.database.conversation_saver(
            data={
                'role': 'system',
                'text': result
            },
            data_table='conversations'
        )
        logger.info(f"System's response saved to database")
        return result


    def runImageAgent(self, prompt: str, image_path: str, history: list[str] = None) -> str:
        """
        Run the agent with an image.

        Args:
            prompt: The prompt to use.
            image_path: Path to the image file.
            history: The history of the conversation.
        """
        # Format the prompt
        formatted_prompt, original_prompt = self.prompts.promptFormatter(task="chattingImage", prompt=prompt, image_path=image_path)

        # Save user's prompt to database before being processed
        self.database.conversation_saver(
            data={
                'role': 'user',
                'text': original_prompt
            },
            data_table='conversations'
        )
        logger.info(f"User's original prompt saved to database")


        logger.info(f"Running image agent with prompt: {prompt}")
        logger.info(f"Using image from path: {image_path}")

        # Create a prompt that instructs the agent to use the image analysis tool
        agent_prompt = self.prompts.agentPromptTemplate(prompt=prompt, image_path=image_path)

        # Save agent's prompt to database before being processed
        self.database.conversation_saver(
            data={
                'role': 'agent',
                'text': agent_prompt
            },
            data_table='conversations'
        )
        logger.info(f"Agent's prompt saved to database")


        # Run the agent with the formatted prompt
        result = self.managerAgent.run(agent_prompt, history or [])
        logger.info("Image agent execution completed")

        # Save system's response to database
        self.database.conversation_saver(
            data={
                'role': 'system',
                'text': result
            },
            data_table='conversations'
        )
        logger.info(f"System's response saved to database")
        return result


    def loadModel(self) -> OpenAIServerModel:
        """
        Load the model acceptable by the SmolAgents CodeAgent.
        """
        logger.info("Loading server model...")
        model = OpenAIServerModel(model_id=self.model_handler.model_name)
        logger.info("Server model loaded successfully")
        return model
