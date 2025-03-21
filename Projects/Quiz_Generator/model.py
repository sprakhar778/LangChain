from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.schema.runnable import RunnableParallel
from typing import Union
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# -----------------------------------------------
# ✅ Pydantic Models for Quiz Structure
class Quiz(BaseModel):
    """Defines a single quiz question."""
    question: str = Field(description="Question with numbering")
    options: list[str] = Field(description="Multiple-choice options (A, B, C, D)")
    answer: str = Field(description="Correct answer")

class Quizzes(BaseModel):
    """Defines a list of quiz questions."""
    quiz: list[Quiz] = Field(description="List of quiz questions")

# -----------------------------------------------
# ✅ Study Material Generator Class
class StudyMaterialGenerator:
    def __init__(self):
        """Initialize the LLM and prompt templates."""
        self.llm = ChatGroq(model="llama-3.3-70b-versatile")
        self.structured_llm = self.llm.with_structured_output(Quizzes)
        self.parser = StrOutputParser()

        # Prompt Templates
        self.prompt1 = PromptTemplate(
            template="Explain this {topic} in simple language with example in detail.",
            input_variables=["topic"]
        )

        self.prompt2 = PromptTemplate(
            template="Generate proper notes on the following content:\n{content}",
            input_variables=["content"]
        )

        self.prompt3 = PromptTemplate(
            template="Generate 5 quiz questions with 4 options (A, B, C, D) based on the following content:\n{content}",
            input_variables=["content"]
        )

        self.prompt4 = PromptTemplate(
            template="Solve the following quiz:\n{quiz}\n"
                     "Provide the answers and detailed explanations with numbering (e.g., 1, 2, 3) separated by line breaks.",
            input_variables=["quiz"]
        )

    def generate_study_material(self, topic: str):
        """
        Generates study material for the given topic:
        1. Explanation
        2. Notes
        3. Quiz
        4. Quiz Solutions
        """
        material = []

        # ✅ Generate Explanation
        content_chain = self.prompt1 | self.llm | self.parser
        content = content_chain.invoke({"topic": topic})
        material.append(content)

        # ✅ Generate Notes and Quiz in Parallel
        notes_quiz_chain = RunnableParallel(
            {
                'notes': self.prompt2 | self.llm | self.parser,
                'quiz': self.prompt3 | self.structured_llm,
            }
        )

        result = notes_quiz_chain.invoke({"content": content})
        material.append(result['notes'])

        # ✅ Append the quiz questions
        quiz_content = []
        for q in result['quiz'].quiz:
            quiz_content.append({
                "question": q.question,
                "options": q.options,
                "answer": q.answer
            })
        material.append(quiz_content)

        # ✅ Generate Quiz Solutions
        quiz_text = "\n".join(
            [f"{idx + 1}. {q['question']}\nOptions: {', '.join(q['options'])}\nAnswer: {q['answer']}\n"
             for idx, q in enumerate(quiz_content)]
        )

        solution_quiz_chain = self.prompt4 | self.llm
        solution = solution_quiz_chain.invoke({"quiz": quiz_text})
        material.append(solution)

        return material
