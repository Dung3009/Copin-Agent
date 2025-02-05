from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from prompt import prompt_template_support
import os
from dotenv import load_dotenv

from vectordb.vectordb import queryVectordb
load_dotenv(".env", override=True)

OPEN_AI_KEY = os.environ.get("OPEN_AI_KEY")

class Copin_support:
    
    open_ai_key = OPEN_AI_KEY
    llm = ChatOpenAI(
            openai_api_key=open_ai_key, temperature=0.5, model="gpt-4o-mini"
        )
    

    
 


    prompt = PromptTemplate(template=prompt_template_support, input_variables=["context", "question"])
    
    rag_chain = (
        prompt
        | llm
        | StrOutputParser()
    )

def support_user(request):
    result = queryVectordb(request)
    answer = process_response(result, request)
    return answer
    

def process_response(result, request):
    if not result:
        answer = "I don't understand the question. Please contact [this link](https://t.me/leecopin) for support "
    else:
        answer = Copin_support.rag_chain.invoke({
            "context": result,
            "question": request
        })
    return answer
    

