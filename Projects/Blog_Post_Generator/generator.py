import asyncio
from langchain_openai import ChatOpenAI
from langchain_google_vertexai.vision_models import VertexAIImageGeneratorChat
from langchain_core.prompts import PromptTemplate
from vertexai import init
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnableParallel
import io
from PIL import Image
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Vertex AI
init(project="nomadic-mesh-454105-a2", location="us-central1")

#  Core logic class
class BlogPostGenerator:
    """Class to generate a blog post with an image for a given topic."""
    def __init__(self):
        # Image generation prompt
        self.prompt1 = PromptTemplate(
            template="generate an centered image of {topic}",
            input_variables=["topic"],
        )
        
        self.generator = VertexAIImageGeneratorChat()
        
        # Text generation prompt
        self.llm = ChatOpenAI()
        self.prompt2 = PromptTemplate(
            template='Write a concise 100-word blog post about: {topic}',
            input_variables=['topic']
        )
        
        self.parser = StrOutputParser()
        
        # Parallel chain setup
        self.parallel_chain = RunnableParallel({
            'image': self.prompt1 | self.generator,
            'text': self.prompt2 | self.llm | self.parser
        })

    async def generate(self, topic):
        """Runs the async generation logic for image and text."""
        response = await self.parallel_chain.ainvoke({'topic': topic})

        result = {
            "text": response['text'],
            "image": None
        }

        # Check if image generation was successful
        if response.get('image'):
            try:
                # Extract the image URL or base64 response
                generated_image = response['image'].content[0]

                # Extract base64 string
                img_base64 = generated_image["image_url"]["url"].split(",")[-1]

                # Convert base64 to PIL image
                img = Image.open(io.BytesIO(base64.decodebytes(bytes(img_base64, "utf-8"))))
                result['image'] = img

            except Exception as e:
                print(f"Image processing failed: {e}")

        return result
