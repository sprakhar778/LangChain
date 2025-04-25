from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm=ChatGroq(model="llama-3.1-8b-instant")

promt=PromptTemplate(
    template="Generate 5 facts on the following topic: {topic}",
    input_variables=["topic"],
)

parser=StrOutputParser()

chain=promt | llm | parser

result=chain.invoke({"topic":"Milky Way Galaxy"})
print(result)