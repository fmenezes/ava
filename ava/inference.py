from langchain_community.chat_models.ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

prompt = ChatPromptTemplate.from_template(
    """You're A.V.A. (Artificial Virtual Assistant), help with this query:

{input}"""
)

output_parser = StrOutputParser()
model = ChatOllama(model="llama2:13b")
chain = (
    {"input": RunnablePassthrough()}
    | prompt
    | model
    | output_parser
)

def infere(prompt: str) -> str:
    return chain.invoke(prompt)
