import asyncio
from langchain_openai import ChatOpenAI
from langchain_google_vertexai.vision_models import VertexAIImageGeneratorChat
from langchain_core.prompts import PromptTemplate
from vertexai import init
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnableParallel
from langchain_groq import ChatGroq
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
        self.llm = ChatGroq( model="llama-3.3-70b-versatile")
   
        self.prompt2 = PromptTemplate(
            template = """
                    Write a detailed and engaging blog post about: {topic}

                    ### Key Requirements:
                    - **Title:** Create a catchy and relevant title that captures attention.
                    - **Introduction:** Write a compelling introduction that hooks the reader and introduces the topic clearly.
                    - **Main Content:**
                        - Include at least 3-5 detailed sections or subheadings covering key aspects of the topic.
                        - Provide accurate information, statistics, and examples where applicable.
                        - Use clear and concise language with short paragraphs for readability.
                       ### Additional Instructions:
                    - **Target Audience:** {audience} 
                    - **Tone:** {tone}
                    - **Word Count:** Aim for {word_count} words.
                    - **Tone and Style:** 
                        - Use an informative and engaging tone.
                        - Include relatable examples or anecdotes when suitable.
                        - Use bullet points or numbered lists for clarity where needed.
                    - **SEO Optimization:**
                        - Include relevant keywords naturally.
                        - Add internal and external links if applicable.
                    - **Conclusion:** Summarize the key points and include a call to action or a thought-provoking closing statement.

                 
                    """,
            input_variables=['topic','audience','tone','word_count']
        )
        
        self.parser = StrOutputParser()
        
        # Parallel chain setup
        self.parallel_chain = RunnableParallel({
            'image': self.prompt1 | self.generator,
            'text': self.prompt2 | self.llm | self.parser
        })

    async def generate(self, topic, target_audience="general", tone="informative", count=500):
        """Runs the async generation logic for image and text."""
        response = await self.parallel_chain.ainvoke({'topic': topic, 'audience': target_audience, 'tone': tone, 'word_count':count})

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
