from src.core.utils import Utils
from src.core.database import DatabaseCore
from src.core.logging_config import setup_logging

from openai import OpenAI
import logging

# Get logger for this module
logger = logging.getLogger(__name__)

class ModelCore:
    def __init__(self, model_provider: str, 
                       model_name: str,
                       utils: Utils,
                       image_model_name: str,
                       API_TOKEN: str,
                       database: DatabaseCore,
                       verbose: bool):
        """
        Initialize the model core.
        
        Args:
            model_provider: The provider of the model (e.g., "openai")
            model_name: The name of the model
            API_TOKEN: API token for authentication
            verbose: Whether to enable verbose logging
        """
        self.model_provider = model_provider
        self.model_name = model_name
        self.utils = utils
        self.image_model_name = image_model_name
        self.API_TOKEN = API_TOKEN
        self.verbose = verbose
        self.database = database

        # Configure logging based on verbose mode
        setup_logging(verbose=self.verbose)
        
        if self.model_provider.lower() == "openai":
            logger.info("Loading OpenAI model!")
            self.client = self.loadOpenAIClient()
            logger.info("OpenAI model loaded successfully!")
        else:
            logger.error(f"Unsupported model provider: {self.model_provider}")
            raise


    def imageGenerator(self, prompt: str, size: str = "1024x1024", quality: str = "low", save_path: str="data/generated_images") -> tuple[str, str]:
        """
        Generate an image from a prompt using OpenAI's DALL-E 3 model.
        
        Args:
            prompt: The text description of the desired image
            size: The size of the generated image. Options: "256x256", "512x512", "1024x1024", "1024x1792", "1792x1024"
            quality: The quality of the generated image. Options: "low", "medium", "high"
            
        Returns:
            tuple[str, str]: URL of the generated image and the local path where it was saved
            
        Raises:
            Exception: If image generation fails
        """
        # Format the prompt
        formatted_prompt, original_prompt = self.promptFormatter(task="image_generation", prompt=prompt)

        # Save user's prompt to database
        self.database.conversation_saver(
            data={
                'role': 'user',
                'text': original_prompt
            },
            data_table='conversations'
        )
        logger.info("User's image generation prompt saved to database")

        try:
            logger.info(f"Generating image with prompt: {formatted_prompt}")
            
            # Generate the image
            response = self.client.images.generate(
                model=self.image_model_name,
                prompt=formatted_prompt,
                n=1,
                size=size,
                # quality=quality
            )
            image_url = response.data[0].url

            # Save the image to the local directory
            path_to_image = self.utils.imgSaver(image_url=image_url, formatted_prompt=formatted_prompt, save_path=save_path)
            logger.info(f"Image saved successfully to {save_path}")

            # Encode the generated image to base64
            base64_image = self.utils.encode_image(image_path=path_to_image)

            # Save the generated image to database
            self.database.conversation_saver(
                data={
                    'role': 'system',
                    'image': base64_image
                },
                data_table='conversations'
            )
            logger.info("Generated image saved to database")

            return path_to_image
        except Exception as e:
            logger.error(f"Failed to generate image: {str(e)}")
            raise


    def chattingImage(self, prompt: str, image_path: str) -> str:
        """
        Generate a response from the model.
        
        Args:
            prompt: The input prompt for the model
            image_path: The path to the image to analyze
            
        Returns:
            str: Generated response from the model
        """
        logger.info(f"Processing image chat with prompt: {prompt}")
        logger.info(f"Using image from path: {image_path}")

        base64_image = self.utils.encode_image(image_path=image_path) 

        # Format the prompt
        formatted_prompt, original_prompt = self.promptFormatter(task="chattingImage", prompt=prompt, image_path=image_path)

        # Save user's original prompt and image to database
        self.database.conversation_saver(
            data={
                'role': 'user',
                'text': original_prompt,
                'image': base64_image
            },
            data_table='conversations'
        )
        logger.info("User's original prompt and image saved to database")

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": formatted_prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            )
            result = response.choices[0].message.content
            logger.info(f"Model has generated a response: {result}")

            # Save system's response to database
            self.database.conversation_saver(
                data={
                    'role': 'system',
                    'text': result
                },
                data_table='conversations'
            )
            logger.info("System's response saved to database")

            return result
        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            raise


    def chatting(self, prompt: str) -> str:
        """
        Generate a response from the model.
        
        Args:
            prompt: The input prompt for the model
            
        Returns:
            str: Generated response from the model
        """
        logger.info(f"Processing chat with prompt: {prompt}")

        # Format the prompt
        formatted_prompt, original_prompt = self.promptFormatter(task="chatting", prompt=prompt)

        # Save user's prompt to database before being processed
        self.database.conversation_saver(
            data={
                'role': 'user',
                'text': original_prompt
            },
            data_table='conversations'
        )
        logger.info(f"User's original prompt saved to database")

        try:
            logger.info(f"Model is processing user's prompt: {prompt}")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user", 
                        "content": formatted_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=512
            )
            result = response.choices[0].message.content
            logger.info(f"Model has generated a response: {result}")

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
        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            raise


    def promptFormatter(self, task: str, prompt: [str], image_path: str = None) -> str:
        """
        Format the prompt for the model.

        Args:
            task: The task to format the prompt for
            prompt: The prompt to format
            image_path: The path to the image to analyze

        Returns:
            str: The formatted prompt
        """
        original_prompt = prompt

        if task == "sumUpIdeas":
            all_conversations = ""
            for conversation in prompt[0]:
                all_conversations += f"{conversation[1]}\n"
            
            prompt = f"""
            Following is a long conversation that we had together about how to be a good designer. You, now, as a smart summarizer and designer,
            are responsible for creating a short summary of all the very important ideas that are mentioned in the following conversations.
            Avoid being verbose, rather focus on keeping all the ideas and explaining them very shortly. The important part for you is 
            to mention all the ideas and summarize them perfectly.Here are the conversations: {all_conversations}
            """
        elif task == "generatingImageWithIdeas":
            prompt = f"""
            You are a designer. You are given a prompt and an idea. You need to generate an image based on the prompt and the idea.
            Here is the prompt: {prompt[0]}
            Here is the idea: {prompt[1]}
            """
        return prompt, original_prompt


    def loadOpenAIClient(self) -> OpenAI:
        """
        Load and configure OpenAI Client.
        
        Returns:
            OpenAI: Configured OpenAI client instance
        """
        try:
            logger.info("Initializing OpenAI client...")
            client = OpenAI(api_key=self.API_TOKEN)
            logger.info("OpenAI client initialized successfully")
            return client
        except Exception as e:
            logger.error(f"Failed to load OpenAI Client: {str(e)}")
            raise
