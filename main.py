from src.core.model import ModelCore
from src.core.agent import AgentCore
from src.core.tools import WebAgentTools
from src.core.utils import Utils
from src.core.database import DatabaseCore
from src.core.logging_config import setup_logging

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
        logger.info("Utils loaded!")


    def database_handler(self):
        logger.info("Loading Database - - -")
        self.database = DatabaseCore(verbose=self.verbose, database_type=self.database_type, database_path=self.database_path)
        logger.info("Database loaded!")


    def model_handler(self):
        logger.info("Loading Model - - - ")
        self.model = ModelCore(
            model_provider=self.model_provider,
            model_name=self.model_name,
            utils=self.utils,
            image_model_name=self.image_model_name,
            API_TOKEN=self.API_TOKEN,
            database=self.database,
            verbose=self.verbose
            )
        logger.info("Model loaded!")
        

    def tools_handler(self):
        self.tools = []


    def agent_handler(self):
        logger.info("Loading Agent - - - ")
        self.agent = AgentCore(self.model, 
            utils=self.utils, 
            tools=[], 
            planning_interval=self.planning_interval, 
            max_steps=self.max_steps, 
            verbosity_level=self.verbosity, 
            verbose=self.verbose,
            database=self.database
            )
        logger.info("Agent loaded!")


if __name__ == "__main__":
    artbuddy = ArtBuddy()
