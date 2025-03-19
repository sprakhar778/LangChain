from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnableParallel
from dotenv import load_dotenv
import os
load_dotenv()

llm=ChatGroq(model="llama-3.3-70b-versatile")
parser=StrOutputParser()


prompt1=PromptTemplate(
    template="Explain this {topic} in simple language with example in detail.",
    input_variables=["topic"]
)

prompt2=PromptTemplate(
    template="Generate a key takeaway on the foloowing /n {content}",
    input_variables=["content"]
)

prompt3=PromptTemplate(
    template="Generate a quiz with 4 option  on the following /n {content}",
    input_variables=["content"]
    
)

prompt4=PromptTemplate(
    template="Solve the following quiz /n {quiz} and generate rembering point on the basis of quiz from this /n {notes}",
    input_variables=["quiz","notes"]
)


parallel_chain = RunnableParallel(
    {
        'notes': prompt2 | llm | parser,
        'quiz': prompt3 | llm | parser,
    }
)

chain= prompt1 | llm | parser | parallel_chain | prompt4 | llm | parser

result=chain.invoke({"topic":"Quantum Computing"})


print(result)

chain.get_graph().print_ascii()