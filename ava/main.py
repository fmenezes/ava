import streamlit as st
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_community.chat_models.ollama import ChatOllama
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    return SQLChatMessageHistory(session_id, "sqlite:///db.sqlite3")


st.title("A.V.A.")

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
    prompt | ChatOllama(model="llama2:13b") | StrOutputParser(),
    input_messages_key="input",
    history_messages_key="history",
    get_session_history=get_session_history,
)

with st.sidebar:
    st.session_state.session_id = st.text_input("session id", "foo")
    if st.button("reset"):
        history: SQLChatMessageHistory = get_session_history(
            st.session_state.session_id
        )
        history.clear()

with st.spinner("Thinking..."):
    history: SQLChatMessageHistory = get_session_history(st.session_state.session_id)
    if len(history.get_messages()) == 0:
        history.add_ai_message("Hi, how can I assist you today?")
    st.session_state.messages = [
        {
            "role": "user" if message.type == "human" else "assistant",
            "content": message.content,
        }
        for message in history.get_messages()
    ]
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.write_stream(chain.stream(
                {"input": prompt}, config={"configurable": {"session_id": st.session_state.session_id}}
            ))
            st.session_state.messages.append({"role": "assistant", "content": response})
