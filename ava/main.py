import getpass
import streamlit as st
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_community.chat_models.ollama import ChatOllama
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
import ollama

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    return SQLChatMessageHistory(session_id, "sqlite:///db.sqlite3")


st.title("A.V.A.")

models = [model['name'] for model in ollama.list()['models']]
default_model = None

try:
    default_model = models.index("llama2:13b")
except:
    pass

with st.sidebar:
    st.session_state.session_id = st.text_input(
        "session id", getpass.getuser())
    st.session_state.model = st.selectbox(
        "model", models, default_model)
    if st.button("reset"):
        history: SQLChatMessageHistory = get_session_history(
            st.session_state.session_id
        )
        history.clear()

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You're A.V.A. (Artificial Virtual Assistant). Response messages with a short answer, like one small sentence.",
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

chain = RunnableWithMessageHistory(
    prompt | ChatOllama(model=st.session_state.model) | StrOutputParser(),
    input_messages_key="input",
    history_messages_key="history",
    get_session_history=get_session_history,
)

with st.spinner("Thinking..."):
    history: SQLChatMessageHistory = get_session_history(st.session_state.session_id)
    if len(history.get_messages()) == 0:
        history.add_ai_message("Hi, how can I assist you today?")
    for message in history.get_messages():
        with st.chat_message(message.type):
            st.markdown(message.content)

if prompt := st.chat_input("What is up?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            st.write_stream(chain.stream(
                {"input": prompt}, config={"configurable": {"session_id": st.session_state.session_id}}
            ))
