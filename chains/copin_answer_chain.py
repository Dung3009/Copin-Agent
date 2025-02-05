from langchain_openai import ChatOpenAI

from langchain.prompts import PromptTemplate
from prompt import prompt_template_answer
from langchain.schema.output_parser import StrOutputParser
import os
from dotenv import load_dotenv
load_dotenv(".env", override=True)

OPEN_AI_KEY = os.environ.get("OPEN_AI_KEY")


class Copin_answer:
    open_ai_key = OPEN_AI_KEY
    llm = ChatOpenAI(
                openai_api_key=open_ai_key, temperature=0.5, model="gpt-4o-mini"
            )
    prompt = PromptTemplate(
            input_variables=["context","question"], template=prompt_template_answer
        )
    rag_chain = (
        prompt
        | llm
        | StrOutputParser()
    )
    