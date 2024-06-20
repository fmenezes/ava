import streamlit as st
from langchain_community.chat_models.ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

st.title("A.V.A.")

prompt = ChatPromptTemplate.from_template(
    """You're A.V.A. (Artificial Virtual Assistant), help with this query:

{input}"""
)

output_parser = StrOutputParser()
model = ChatOllama(model="llama2:13b")
chain = {"input": RunnablePassthrough()} | prompt | model | output_parser


def generate_response(input_text: str) -> str:
    return chain.invoke({"input":input_text})


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner('Thinking...'):
            response = generate_response(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
