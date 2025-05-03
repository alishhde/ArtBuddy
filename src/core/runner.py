from src.core.model import ModelCore
from src.core.agent import AgentCore
from src.core.database import DatabaseCore
from src.core.utils import Utils
from src.core.logging_config import setup_logging
from src.core.prompts import Prompts

import logging
from datetime import datetime

# Get logger for this module
logger = logging.getLogger(__name__)

class Runner:
    def __init__(self, model: ModelCore, agent: AgentCore, database: DatabaseCore, utils: Utils, prompts: Prompts, verbose: bool):
        self.model = model
        self.agent = agent
        self.database = database
        self.utils = utils
        self.prompts = prompts

        self.verbose = verbose
        setup_logging(verbose=verbose)


    def run(self, mode: str, agent_mode: bool=False, user_prompt: str=None, use_ideas: bool=False, img_path: str=None):
        if mode == "chatting" and agent_mode:
            return self.chattingAgent(user_prompt)
        elif mode == "chatting" and not agent_mode:
            return self.chattingModel(user_prompt)
        elif mode == "chattingImage" and agent_mode:
            return self.chattingImageAgent(user_prompt, img_path)
        elif mode == "chattingImage" and not agent_mode:
            return self.chattingImageModel(user_prompt, img_path)
        elif mode == "generatingImage" and use_ideas:
            return self.generatingImageWithIdeas(user_prompt)
        elif mode == "generatingImage" and not use_ideas:
            return self.generatingImage(user_prompt)


    def generatingImageWithIdeas(self, user_prompt: str):
        """
        Run the model directly for generating image.
        """
        # Retrieve the last idea
        retriever = self.database.idea_retriever(num_rows=1)
        last_idea = retriever[0]['ideas'][0]

        processed_prompt, _ = self.prompts.promptFormatter(task="generatingImageWithIdeas", prompt=[user_prompt, last_idea])

        # Run the model
        return self.model.imageGenerator(processed_prompt)


    def generatingImage(self, user_prompt: str):
        """
        Run the model directly for generating image.
        """
        logger.info("Running model")
        return self.model.imageGenerator(user_prompt)


    def chattingImageAgent(self, user_prompt: str, img_path: str):
        """
        Run the agent for chatting image.
        """
        logger.info("Running agent")
        return self.agent.runImageAgent(user_prompt, img_path)


    def chattingImageModel(self, user_prompt: str, img_path: str):
        """
        Run the model directly for chatting image.
        """
        logger.info("Running model")
        return self.model.chattingImage(user_prompt, img_path)


    def chattingAgent(self, user_prompt: str):
        """
        Run the agent for chatting.
        """
        logger.info("Running agent")
        return self.agent.runAgent(user_prompt, [])


    def chattingModel(self, user_prompt: str):
        """
        Run the model directly for chatting.
        """
        logger.info("Running model")
        return self.model.chatting(user_prompt)


    def sumUpIdeas(self, top_k: int=100):
        """
        Sum up the ideas from the database. every top_k conversations, save their sum up to the ideas database.
        """
        logger.info("Summing up ideas")
        top_k_conversations = self.database.conversation_retriever(basedOnDate=True, top_k=top_k, exclude_image=True)
        
        # Calling model to sum up the text and return a prompt shape ideas of everything discussed in the conversations
        prompt_with_conversations, _ = self.prompts.promptFormatter(task="sumUpIdeas", prompt=top_k_conversations)

        # Running model to summarize the prompt conversations
        model_summarized_ideas = self.model.chatting(prompt_with_conversations)
        
        # Save the prompt to the database
        self.database.idea_saver(
            data={
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'idea': model_summarized_ideas
            },
            data_table='ideas')
        return model_summarized_ideas
        