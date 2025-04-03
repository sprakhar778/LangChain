from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
from langchain_core.runnables import RunnableSequence, RunnableMap, RunnableLambda, RunnablePassthrough,RunnableParallel
load_dotenv()

prompt1=PromptTemplate(
    template="write joke about {topic}",
    input_variables=["topic"],
)

llm=ChatGroq(model="llama-3.1-8b-instant", temperature=0.9)

parser=StrOutputParser()

prompt2=PromptTemplate( 
    template="Explain joke {joke}",
    input_variables=["joke"],
)

joke_gen_chain= RunnableSequence(prompt1,llm,parser)

parallel_chain=RunnableParallel(
    {
        "joke": RunnablePassthrough(),
        "exlpain": RunnableSequence(prompt2,llm,parser)
    }
)

final_chain=RunnableSequence(joke_gen_chain,parallel_chain)
result=final_chain.invoke({"topic":"python"})
print(result["joke"])
print("**********************************")
print(result["exlpain"])
