from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

# -----------------------------------------------
llm = ChatGroq(model="llama-3.1-8b-instant")

class Quiz(BaseModel):
    quetions:list[str]=Field(description="Question with numbering on the given topic")
    options:list[list[str]]=Field(description="Multiple-choice options  for respective question number")
    answer:list[str]=Field(description="Correct answers")


parser=PydanticOutputParser(pydantic_object=Quiz)

prompt=PromptTemplate(
    template="Generate 5 quiz questions  on {content} follow the instruction given below \n {format_instruction}",
    input_variables=["content"],
    partial_variables={'format_instruction': parser.get_format_instructions()}
     )

chain= prompt | llm | parser

result=chain.invoke({"content":"Milky Way Galaxy"})
print(result)

quetions=result.quetions
options=result.options
answer=result.answer

for i in range(5):
    print(f"Question {i+1}: {quetions[i]}")
    print()
    for j in range(4):
        print(f"Option {chr(65+j)}: {options[i][j]}")
        print()
    print(f"Correct Answer: {answer[i]}")
    print("\n")