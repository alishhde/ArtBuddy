from PIL import Image
import base64

class Utils:
    def __init__(self):
        pass


    def imgLoader(self, imgs: list[str]) -> list[Image.Image]:
        """
        Load images from the given list of paths.

        Args:
            imgs: The list of paths to the images.

        Returns:
            list[PIL.Image.Image]: A list of PIL Image objects.
        """
        return [Image.open(path) for path in imgs]


    def encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
