from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

#Prompt
prompt=PromptTemplate(
    template="give me 5 point summary of the following {topic}",
    input_variables=["topic"],

)

#LLM
llm=ChatOpenAI()

#Output Parser
parser= StrOutputParser()

chain=prompt | llm | parser

result=chain.invoke({'topic':'Cricket'})

print(result)
