

class Prompts:
    def __init__(self):
        pass


    def agentPromptTemplate(self, image_path: str, prompt: str):
        self.agentPromptTemplate = f"""
        You are an AI assistant that can analyze images. You have access to an image analysis tool.

        The user has provided an image at this path: {image_path}
        Their question about the image is: {prompt}

        To analyze the image, you should:
        1. Use the image_analysis tool with the image path and the user's question
        2. The tool will return an analysis of the image
        3. Use that analysis to provide a helpful response to the user's question

        Remember to:
        - Be specific about what you see in the image
        - Address the user's question directly
        - Provide insights and explanations based on the image analysis
        - Defend your answer
        """
        return self.agentPromptTemplate


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
        elif task == "chattingImage":
            prompt = f"""
            You are a designer. You are given a prompt and an image. You need to analyze the image and provide a response to the prompt.
            Here is the prompt: {prompt[0]}
            Here is the image: {image_path}
            """
            
        elif task == "chattingImageAgent":
            prompt = f"""
            You are a designer. You are given a prompt and an image. You need to analyze the image and provide a response to the prompt.
            Here is the prompt: {prompt[0]}
            Here is the image: {image_path}
            """
            
        return prompt, original_prompt