
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnableParallel
from dotenv import load_dotenv
import os
load_dotenv()
#-----------------------------------------------

class StudyMaterialGenerator:
    def __init__(self):
        self.llm=ChatGroq(model="llama-3.3-70b-versatile")
        self.parser=StrOutputParser()
        self.prompt1=PromptTemplate(
            template="Explain this {topic} in simple language with example in detail.",
            input_variables=["topic"]
        )
        self.prompt2=PromptTemplate(
            template="Generate a proper notes on the following /n {content}",
            input_variables=["content"]
        )
        self.prompt3=PromptTemplate(
            template="Generate a quiz with 4 option  on the following /n {content}",
            input_variables=["content"]
        )
        self.prompt4=PromptTemplate(
            template="Solve the following quiz /n {quiz} and generate rembering point on the basis of quiz from this /n {notes}",
            input_variables=["quiz","notes"]
        )
        self.material=[]

    def generate_study_material(self,topic):
        content_chain= self.prompt1 | self.llm | self.parser
        content_chain_output=content_chain.invoke({"topic":topic})
        # print("Content \n",content_chain_output)
        self.material.append(content_chain_output)
        notes_quiz_chain = RunnableParallel(
            {
                'notes': self.prompt2 | self.llm | self.parser,
                'quiz': self.prompt3 | self.llm | self.parser,
            }
        )
        result=notes_quiz_chain.invoke({"content":content_chain_output})
        self.material.append(result["notes"])
        self.material.append(result["quiz"])
        # print("Notes \n",result["notes"])
        # print("Quiz \n",result["quiz"])
        keytakeaway_chain = self.prompt4 | self.llm | self.parser
        keytakeaway_chain_output=keytakeaway_chain.invoke({"notes":result["notes"],"quiz":result["quiz"]})
        self.material.append(keytakeaway_chain_output)
        # print("Key Takeaway \n",keytakeaway_chain_output)
        return self.material
