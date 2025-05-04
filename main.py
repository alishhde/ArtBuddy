from src.core.model import ModelCore
from src.core.agent import AgentCore
from src.core.utils import Utils
from src.core.database import DatabaseCore
from src.core.logging_config import setup_logging
from src.core.runner import Runner
from src.core.tools import ImageAnalysisTool
from src.core.prompts import Prompts

from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import logging

load_dotenv(override=True)

# Set verbose mode
verbose = bool(os.getenv("VERBOSE").lower() == "true") 

# Configure logging based on verbose mode
setup_logging(verbose=verbose)
logger = logging.getLogger(__name__)


class ArtBuddy:
    def __init__(self):
        logger.info("Initializing ArtBuddy - - -")

        # ==== Load environment variables ==== #
        self.variableLoader()
        logger.info("Environment variables loaded!")

        # ==== Load Utils ==== #
        self.utils_loader()
        logger.info("Utils loaded!")

        # ==== Load Prompts ==== #
        self.prompts_loader()
        logger.info("Prompts loaded!")

        # ==== Load Database ==== #
        self.database_handler()
        logger.info("Database loaded!")

        # ==== Load Model ==== #
        self.model_handler()
        logger.info("Model loaded!")

        # ==== Load Tools ==== #
        self.tools_handler()
        logger.info("Tools loaded!")

        # ==== Load Agent ==== #
        self.agent_handler()
        logger.info("Agent loaded!")

        # ==== Load Runner ==== #
        self.run()


    def variableLoader(self):
        logger.info("Loading environment variables...")
        
        self.model_provider = os.getenv("MODEL_PROVIDER")
        logger.info(f"Model Provider: {self.model_provider} -> type: {type(self.model_provider)}")
        
        self.model_name = os.getenv("MODEL_NAME")
        logger.info(f"Model Name: {self.model_name} -> type: {type(self.model_name)}")
        self.image_model_name = os.getenv("IMAGE_MODEL_NAME")
        logger.info(f"Image Model Name: {self.image_model_name} -> type: {type(self.image_model_name)}")
        self.API_TOKEN = os.getenv("OPENAI_TOKEN")
        self.verbose = bool(os.getenv("VERBOSE").lower() == "true")
        logger.info(f"Verbose: {self.verbose} -> type: {type(self.verbose)}")
        
        self.planning_interval = int(os.getenv("PLANNING_INTERVAL"))
        logger.info(f"Planning Interval: {self.planning_interval} -> type: {type(self.planning_interval)}")
        
        self.max_steps = int(os.getenv("MAX_STEPS"))
        logger.info(f"Max Steps: {self.max_steps} -> type: {type(self.max_steps)}")
        
        self.verbosity = int(os.getenv("VERBOSITY"))
        logger.info(f"Verbosity: {self.verbosity} -> type: {type(self.verbosity)}")
        
        logger.info("Environment variables loaded!")

        self.database_type = os.getenv("DATABASE_TYPE")
        logger.info(f"Database Type: {self.database_type} -> type: {type(self.database_type)}")
        self.database_path = os.getenv("DATABASE_PATH")
        logger.info(f"Database Path: {self.database_path} -> type: {type(self.database_path)}")
        

    def utils_loader(self):
        logger.info("Loading Utils - - -")
        self.utils = Utils(verbose=self.verbose)


    def prompts_loader(self):
        logger.info("Loading Prompts - - -")
        self.prompts = Prompts()


    def database_handler(self):
        logger.info("Loading Database - - -")
        self.database = DatabaseCore(verbose=self.verbose, database_type=self.database_type, database_path=self.database_path)


    def model_handler(self):
        logger.info("Loading Model - - - ")
        self.model = ModelCore(
            model_provider=self.model_provider,
            model_name=self.model_name,
            utils=self.utils,
            image_model_name=self.image_model_name,
            API_TOKEN=self.API_TOKEN,
            database=self.database,
            prompts=self.prompts,
            verbose=self.verbose
            )
        

    def tools_handler(self):
        logger.info("Loading Tools - - - ")

        # Image Analysis Tool
        image_analysis_tool = ImageAnalysisTool(model_handler=self.model)

        self.tools = [image_analysis_tool]


    def agent_handler(self):
        logger.info("Loading Agent - - - ")
        self.agent = AgentCore(self.model, 
            utils=self.utils, 
            tools=self.tools, 
            planning_interval=self.planning_interval, 
            max_steps=self.max_steps, 
            verbosity_level=self.verbosity, 
            verbose=self.verbose,
            database=self.database,
            prompts=self.prompts
            )


    def run(self):
        mode = "generatingImage"
        user_prompt = "A cute horse playing with a ball while sky boarding."
        img_path = None

        agent_mode = False
        use_ideas = False

        runner = Runner(model=self.model,
                        agent=self.agent,
                        database=self.database,
                        utils=self.utils,
                        prompts=self.prompts,
                        verbose=self.verbose)

        #### ----- Image Generation ----- ####
        # Basic image generation
        runner.run(
            mode="generatingImage",
            user_prompt="A beautiful sunset over mountains",
            use_ideas=False
        )

        # Image generation with ideas from previous conversations
        # runner.run(
        #     mode="generatingImage",
        #     user_prompt="Create an abstract painting",
        #     use_ideas=True
        # )

        #### ----- Image Analysis ----- ####
        # runner.run(
        #     mode="chattingImage",
        #     user_prompt="What is the main subject of this image?",
        #     img_path="data/imgs/squire.jpg"
        # )

        # Agent-based image analysis (more sophisticated analysis)
        # runner.run(
        #     mode="chattingImage",
        #     agent_mode=True,
        #     user_prompt="Analyze the composition and color theory in this image",
        #     img_path="data/imgs/squire.jpg"
        # )

        #### ----- Chatting ----- ####
        # Basic chat
        # runner.run(
        #     mode="chatting",
        #     user_prompt="Tell me about art history"
        # )

        # Agent-based chat (for complex queries and research)
        runner.run(
            mode="chatting",
            agent_mode=True,
            user_prompt="Research modern art movements and their influence on contemporary design"
        )


        # Sum up ideas every 10 conversations
        if len(self.database) % 10 == 0:
            runner.sumUpIdeas(top_k=10, exclude_image=True)


if __name__ == "__main__":
    artbuddy = ArtBuddy()
