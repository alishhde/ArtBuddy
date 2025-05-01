from src.core.utils import Utils

from datetime import datetime
from openai import OpenAI
import requests
import os
import logging

# Get logger for this module
logger = logging.getLogger(__name__)

class ModelCore:
    def __init__(self, model_provider: str, 
                       model_name: str,
                       utils: Utils,
                       image_model_name: str,
                       API_TOKEN: str,
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

        # Configure logging based on verbose mode
        if self.verbose:
            logging.basicConfig(
                level=logging.DEBUG,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            # Disable all logging when not verbose
            logging.disable(logging.CRITICAL)
        
        if self.model_provider.lower() == "openai":
            logger.info("Loading OpenAI model!")
            self.client = self.loadOpenAIClient()
            logger.info("OpenAI model loaded successfully!")
        else:
            logger.error(f"Unsupported model provider: {self.model_provider}")
            raise


    def imageGenerator(self, prompt: str, size: str = "1024x1024", quality: str = "low") -> tuple[str, str]:
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
        try:
            logger.info(f"Generating image with prompt: {prompt}")
            
            # Generate the image
            response = self.client.images.generate(
                model=self.image_model_name,
                prompt=prompt,
                n=1,
                size=size,
                # quality=quality
            )
            image_url = response.data[0].url

            # Create a filename based on timestamp and prompt
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_prompt = "".join(x for x in prompt[:30] if x.isalnum() or x in (' ', '-', '_')).strip()
            filename = f"{timestamp}_{safe_prompt}.png"
            save_path = os.path.join("data", "generated_images", filename)

            # Download and save the image
            logger.info(f"Downloading image to {save_path}")
            
            response = requests.get(image_url)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Image saved successfully to {save_path}")

            return image_url, save_path
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

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
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
            logger.info(f"Generated response: {result}")
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

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=512
            )
            result = response.choices[0].message.content
            logger.info(f"Generated response: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            raise


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