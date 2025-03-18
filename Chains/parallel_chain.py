import asyncio
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_google_vertexai.vision_models import VertexAIImageGeneratorChat
from langchain_core.prompts import PromptTemplate
from vertexai import init
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnableParallel
import requests
import io
from PIL import Image
import base64
from dotenv import load_dotenv

load_dotenv()

# Initialize Vertex AI with your project ID and region
init(project="nomadic-mesh-454105-a2", location="us-central1")

# Create the image generation and text generation models
prompt1 = PromptTemplate(
    template="generate an centerd image of {topic}",
    input_variables=["topic"],
)
generator = VertexAIImageGeneratorChat()

llm = ChatOpenAI()

prompt2 = PromptTemplate(
    template='Generate 5-point descriptions of the: {topic}',
    input_variables=['topic']
)

parser = StrOutputParser()

# Parallel chain for image and text generation
parallel_chain = RunnableParallel({
    'image': prompt1 | generator,
    'text': prompt2 | llm | parser
})

async def main():
    response = await parallel_chain.ainvoke({'topic': 'paris skyline'})

    print("Response received:")
    print(response.keys())

    # Display text response
    print("\nText description:")
    print(response['text'])

    # Check if image generation was successful
    if response.get('image'):
        # Extract the image URL
        generated_image = response['image'].content[0]
        
        img_base64 = generated_image["image_url"]["url"].split(",")[-1]
        # Convert base64 string to Image
        img = Image.open(io.BytesIO(base64.decodebytes(bytes(img_base64, "utf-8"))))
        img.show()
    else:
        print("No image generated or empty response!")

# Run the asynchronous function
asyncio.run(main())
