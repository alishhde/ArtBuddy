from PIL import Image
import base64
import os
import requests
from datetime import datetime
import logging

from src.core.logging_config import setup_logging

# Get logger for this module
logger = logging.getLogger(__name__)

class Utils:
    def __init__(self, verbose: bool):
        self.verbose = verbose
        setup_logging(verbose=verbose)


    def imgLoader(self, imgs: list[str]) -> list[Image.Image]:
        """
        Load images from the given list of paths.

        Args:
            imgs: The list of paths to the images.

        Returns:
            list[PIL.Image.Image]: A list of PIL Image objects.
        """
        return [Image.open(path) for path in imgs]

    def imgSaver(self, image_url: str, formatted_prompt: str, save_path: str):
        
        # Create a filename based on timestamp and prompt
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_prompt = "".join(x for x in formatted_prompt[:15] if x.isalnum() or x in (' ', '-', '_')).strip()
        filename = f"{timestamp}_{safe_prompt}.png"
        save_path = os.path.join(save_path, filename)

        # Download and save the image
        logger.info(f"Downloading image to {save_path}")
        
        response = requests.get(image_url)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)


    def encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
