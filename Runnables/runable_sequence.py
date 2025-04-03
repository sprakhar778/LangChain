from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers  import StrOutputParser
from dotenv import load_dotenv
import os
from langchain_core.runnables import RunnableSequence, RunnableMap, RunnableLambda

load_dotenv()

prompt=PromptTemplate(
    template="write joke about {topic}",
    input_variables=["topic"],
)

llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0.9, openai_api_key=os.getenv("OPENAI_API_KEY"))

parser=StrOutputParser()

chain= RunnableSequence(prompt,llm,parser)

print(chain.invoke({"topic":"python"}))