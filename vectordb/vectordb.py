from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import DirectoryLoader
from dotenv import load_dotenv
import os
load_dotenv(".env", override=True)

NEW_PIPECONE_API = os.environ.get("NEW_PIPECONE_API")

def queryVectordb(input):

    pc = Pinecone(
        api_key=NEW_PIPECONE_API
    )

    index_name = "multilingual-e5-large"

    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=1024,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    index = pc.Index(index_name)

    query = input

    embedding = pc.inference.embed(
        model="multilingual-e5-large",
        inputs=[query],
        parameters={"input_type": "query"},
    )

    result = index.query(
        namespace="copin_data",
        vector=embedding[0].values,
        top_k=3,
        include_values=False,
        include_metadata=True,
    )
    try:
        score = result.matches[0]["score"]
        if score >= 0.8:
            answer = result.matches[0]["metadata"]["text"]
        else:
            answer = []
    except Exception as e:
        answer = []
    return answer


def syncData():
    pc = Pinecone(
        api_key=NEW_PIPECONE_API
    )
    loader = DirectoryLoader("./", glob="**/vectordb/data_copin/*.txt")
    documents = loader.load()
    data = []
    for i in range(len(documents)):
        doc = documents[i].page_content
        source =  documents[i].metadata['source']
        id = source.replace('vectordb/data_copin/', '').replace('.txt','')
        data.append(
            {"id": id, "text": doc},
        )
    index_name = "multilingual-e5-large"
    if not pc.has_index(index_name):
        pc.create_index(
            name=index_name,
            dimension=1024,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )

    index = pc.Index(index_name)
    embeddings = pc.inference.embed(
        model="multilingual-e5-large",
        inputs=[d["text"] for d in data],
        parameters={"input_type": "passage", "truncate": "END"},
    )

    vectors = []
    for d, e in zip(data, embeddings):
        vectors.append(
            {"id": d["id"], "values": e["values"], "metadata": {"text": d["text"]}}
        )

    index.upsert(vectors=vectors, namespace="copin_data")

