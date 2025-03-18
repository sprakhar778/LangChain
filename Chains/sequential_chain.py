#Required Imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

#Load Environment Variables
load_dotenv()

#Prompt1
prompt1=PromptTemplate(
    template="Create a maths problem on the given {topic} for 5th grade students",
    input_variables=["topic"],
)

#Prompt2
prompt2=PromptTemplate(
    template="First mention the problem statement as it is then solve the following maths problem: {problem}",
    input_variables=["problem"],
)

#Model
model=ChatOpenAI()

#Output Parser
parser= StrOutputParser()

chain=prompt1 | model | parser | prompt2 | model | parser

result=chain.invoke({'topic':'Crieket'})

print(result)

