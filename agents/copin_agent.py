from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, Tool, create_openai_functions_agent
from chains.copin_query_chain import query_trader
from chains.copin_support_chain import support_user
from langchain import hub
import os
from dotenv import load_dotenv
load_dotenv(".env", override=True)

OPEN_AI_KEY = os.environ.get("OPEN_AI_KEY")



    
    

tools=[
    Tool(
        name="Query",
        func=query_trader,
        description=""" Useful when you need to find traders based on user criteria.
        """
        
    ),
    Tool(
        name="Support",
        func=support_user,
        description="""Useful when you need to answer the questions about Copin.
        """
        
    )
]

chat_model = ChatOpenAI(
    openai_api_key=OPEN_AI_KEY, temperature=0.8, model="gpt-4o-mini"
)
copin_agent_prompt = hub.pull("dungdlab/copin_agent")

copin_rag_agent = create_openai_functions_agent(
    llm=chat_model,
    prompt=copin_agent_prompt,
    tools=tools,
)

copin_rag_agent_executor = AgentExecutor(
    agent=copin_rag_agent,
    tools=tools,
    return_intermediate_steps=False,
    verbose=True,
)


