from langchain_groq import ChatGroq
from dotenv import load_dotenv
from typing import Optional,Literal,Union
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel,Field

load_dotenv()

llm=ChatGroq(model="llama-3.3-70b-versatile")

#Structured Output Schema

class Quiz(BaseModel):
    question: Union[str,list[str]] = Field(description="Question of the Quiz with numbering")
    options: list[str] = Field(description="Options of the Quiz with A,B,C,D")
    answer: str = Field(description="Answer of the Quiz")

class Quizess(BaseModel):
    quiz: list[Quiz] = Field(description="List of Quizes")


structured_llm = llm.with_structured_output(Quizess)
prompt=PromptTemplate(
    template="Generate a  quizes with 4 option (like bullets point with option(A,B,C,D)) on the following /n {content}",
    input_variables=["content"]
)
chain=prompt | structured_llm

content=['Artificial Intelligence (AI) is a rapidly evolving technology that enables machines to simulate human intelligence, learning from data to perform tasks such as problem-solving, decision-making, and natural language understanding. From chatbots and recommendation systems to advanced medical diagnostics and autonomous vehicles, AI is transforming industries by improving efficiency and accuracy. Machine learning, a subset of AI, allows systems to recognize patterns and adapt over time, while deep learning enables breakthroughs in areas like image recognition and language translation. As AI continues to evolve, it holds the potential to revolutionize various fields, making life more convenient while also raising ethical concerns about privacy, bias, and job automation.']



result=chain.invoke({"content":content})
for q in result.quiz:
    print(q.question)
    print(q.options)
    print(q.answer)
    print("\n")