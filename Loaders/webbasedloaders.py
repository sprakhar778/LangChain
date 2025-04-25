from langchain_community.document_loaders import WebBaseLoader
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

llm=ChatGroq(model="llama-3.1-8b-instant", temperature=0.9)

prompt = PromptTemplate(
    template='Answer the following question \n {question} from the following text - \n {text}',
    input_variables=['question','text']
)

parser = StrOutputParser()

url = 'https://en.wikipedia.org/wiki/Local_search_(optimization)'
loader = WebBaseLoader(url)

docs = loader.load()

print(docs[0].page_content)

# chain = prompt | llm | parser

# print(chain.invoke({'question':'What is the prodcut that we are talking about?', 'text':docs[0].page_content}))