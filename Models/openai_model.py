from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-4o")

prompt=PromptTemplate(
    template="Generate 5 facts on the following topic: {topic}",
    input_variables=["topic"],
)

parser=StrOutputParser()

chain=prompt | llm | parser

result=chain.invoke({"topic":"Milky Way Galaxy"})
print(result)