from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnableParallel
from dotenv import load_dotenv
import os
load_dotenv()
#-----------------------------------------------
llm=ChatGroq(model="llama-3.3-70b-versatile")

parser=StrOutputParser()

prompt1=PromptTemplate(
    template="Explain this {topic} in simple language with example in detail.",
    input_variables=["topic"]
)
prompt2=PromptTemplate(
    template="Generate a proper notes on the following /n {content}",
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

#-------------------------------------------------------



#-------------------------------------------------------
content_chain= prompt1 | llm | parser
content_chain_output=content_chain.invoke({"topic":"Quantum Computing"})
print("Content \n",content_chain_output)
#-------------------------------------------------------

notes_quiz_chain = RunnableParallel(
    {
        'notes': prompt2 | llm | parser,
        'quiz': prompt3 | llm | parser,
    }
)
result=notes_quiz_chain.invoke({"content":content_chain_output})
print("Notes \n",result["notes"])
print("Quiz \n",result["quiz"])

#-------------------------------------------------------

keytakeaway_chain = prompt4 | llm | parser
keytakeaway_chain_output=keytakeaway_chain.invoke({"notes":result["notes"],"quiz":result["quiz"]})
print("Key Takeaway \n",keytakeaway_chain_output)

#--------------------------------------------------------------
