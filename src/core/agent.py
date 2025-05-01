from src.core.model import ModelCore
from src.core.utils import Utils

from smolagents import CodeAgent, OpenAIServerModel, DuckDuckGoSearchTool, Tool

from PIL import Image
import os
import logging

# Get logger for this module
logger = logging.getLogger(__name__)

class AgentCore:
    def __init__(self, model_instance: ModelCore, utils: Utils, tools: list[Tool], planning_interval: int, max_steps: int, verbosity_level: int, verbose: bool):
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
        """
        # Configure logging based on verbosity level
        if verbose:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            # Disable all logging when not verbose
            logging.disable(logging.CRITICAL)

        logger.info("Initializing AgentCore - - -")
        self.model_handler = model_instance
        self.serverModel = self.loadModel()
        self.tools = tools
        self.managerAgent = self.agentManager(planning_interval, verbosity_level, max_steps)
        logger.info("AgentCore initialized successfully!")


    def runAgent(self, prompt: str, history: list[str]) -> str:
        """
        Run the agent.

        Args:
            prompt: The prompt to use.
            history: The history of the conversation.
        """
        logger.info(f"Running agent with prompt: {prompt}")
        result = self.managerAgent.run(prompt, history)
        logger.info("Agent execution completed")
        return result


    def loadModel(self) -> OpenAIServerModel:
        """
        Load the model acceptable by the SmolAgents CodeAgent.
        """
        logger.info("Loading server model...")
        model = OpenAIServerModel(model_id=self.model_handler.model_name)
        logger.info("Server model loaded successfully")
        return model


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
            tools=[],
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
            tools=[],
            name="Web_Agent",
            description="A Web Agent that can search the web for information.",
            verbosity_level=verbosity_level,
            max_steps=max_steps
        )
        logger.info("Web agent loaded successfully!")
        return agent
