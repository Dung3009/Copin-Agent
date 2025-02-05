from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
# from streamlit import json
import json
from analyze_func import connect_copin_els
from chains.copin_answer_chain import Copin_answer
from prompt import prompt_template_query_els
from langchain.schema.output_parser import StrOutputParser
import os
from dotenv import load_dotenv
load_dotenv(".env", override=True)

OPEN_AI_KEY = os.environ.get("OPEN_AI_KEY")

class Copin_query:
    open_ai_key = OPEN_AI_KEY
    llm = ChatOpenAI(
                openai_api_key=open_ai_key, temperature=0.5, model="gpt-4o-mini"
            )
    prompt = PromptTemplate(
            input_variables=["question"], template=prompt_template_query_els
        )
    rag_chain = (
        prompt
        | llm
        | StrOutputParser()
    )

def query_trader(request):
    copin_query = Copin_query()
    copin_answer = Copin_answer()
    query = copin_query.rag_chain.invoke({"question": request})
    query = json.loads(query)
    result_query  = connect_copin_els(query)
    try:
        result_message = ""
        for index, row in result_query.iterrows():
            row_message = ""
            for column, value in row.items():
                if column == "account":
                    row_message += f'<b><i>{column}: </i></b> <a href="https://app.copin.io/trader/{value}">{value}</a>\n'
                else:
                    row_message += f"<b><i>{column}: </i></b> {value}\n"
            result_message += row_message + "\n"  # Thêm khoảng trống giữa các hàng
        print(query)
    except Exception as e:
        print(query)
        result_message=[]
    answer = copin_answer.rag_chain.invoke({"context": result_message, "question": request})
    return answer