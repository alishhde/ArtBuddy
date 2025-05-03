from smolagents import Tool
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ImageAnalysisTool(Tool):
    name = "image_analysis"
    description = """
    This is a tool that analyzes images using the model's image capabilities.
    It takes an image path and a prompt, and returns an analysis of the image based on the prompt.
    """
    inputs = {
        "image_path": {
            "type": "string",
            "description": "The path to the image file to analyze",
        },
        "prompt": {
            "type": "string",
            "description": "The prompt/question about the image",
        }
    }
    output_type = "string"

    def __init__(self, model_handler):
        self.model_handler = model_handler

    def forward(self, image_path: str, prompt: str) -> str:
        """
        Analyze an image using the model's image capabilities.

        Args:
            image_path: Path to the image file
            prompt: The prompt to use for analysis

        Returns:
            str: Analysis of the image
        """
        try:
            return self.model_handler.chattingImage(prompt, image_path)
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return f"Error analyzing image: {str(e)}"
 