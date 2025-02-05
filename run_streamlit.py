import streamlit as st
from agents.copin_agent import copin_rag_agent_executor
from vectordb.vectordb import Pinecone, ServerlessSpec
from dotenv import load_dotenv
import os
load_dotenv(".env", override=True)

NEW_PIPECONE_API = os.environ.get("NEW_PIPECONE_API")





st.set_page_config(page_title="Copin AI Assistant")
with st.sidebar:
    st.title("Copin AI Assistant")


# Function for generating LLM response
def generate_response(input):
    answer = copin_rag_agent_executor.invoke({"input": input} )
    return answer['output']


def extract_answer(output):
    # Tách output dựa trên chuỗi "{answer}"
    parts = output.split("{answer}")

    # Kiểm tra để chắc chắn rằng có ít nhất hai phần sau khi tách
    if len(parts) > 1:
        # Trả về phần sau chuỗi "{answer}", loại bỏ khoảng trắng thừa
        return parts[1].strip()
    else:
        # Nếu không tìm thấy "{answer}", trả về chuỗi rỗng hoặc thông báo phù hợp
        return "No answer found in the output"


# Add this function to store conversation in vectordb
def store_conversation(user_message, assistant_response):
    pc = Pinecone(
        api_key=NEW_PIPECONE_API
    )
    
    conversation_text = f"User: {user_message}\nAssistant: {assistant_response}"
    
    # Generate embedding for the conversation
    embedding = pc.inference.embed(
        model="multilingual-e5-large",
        inputs=[conversation_text],
        parameters={"input_type": "passage"},
    )
    
    index = pc.Index("multilingual-e5-large")
    
    # Create a unique ID for the conversation (you might want to use a more sophisticated ID generation)
    conversation_id = f"conv_{len(st.session_state.messages)}"
    
    # Store the conversation in Pinecone
    vector = {
        "id": conversation_id,
        "values": embedding[0].values,
        "metadata": {"text": conversation_text}
    }
    
    index.upsert(vectors=[vector], namespace="conversation_history")


# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "Welcome, just ask me about Copin"}
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User-provided prompt
if input := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": input})
    with st.chat_message("user"):
        st.write(input)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Getting your answer.."):
            response = generate_response(input)
            st.write(response)
            # Store the conversation after getting the response
            store_conversation(input, response)
    
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
