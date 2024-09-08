import getpass
import os
import sqlite3
from platform import platform

import ollama
import streamlit as st
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import create_react_agent

st.title("A.V.A. Autonomous Virtual Assistant")

models = [model["name"] for model in ollama.list()["models"]]

try:
    default_model = models.index("llama3.1:8b")
except:
    default_model = None

with st.sidebar:
    st.session_state.session_id = st.text_input("session id", getpass.getuser())
    st.session_state.model = st.selectbox("model", models, default_model)

model = ChatOllama(model=st.session_state.model)
cnn = sqlite3.connect("db.sqlite3", check_same_thread=False)
checkpointer = SqliteSaver(cnn)


@tool
def tool_cwd():
    """Get current working directory"""
    return os.getcwd()


@tool
def tool_env():
    """Get current environment variables"""
    return os.environ


@tool
def tool_ls(path):
    """
    List contents of directory

    Arguments:
    path: the path to list
    """
    return os.listdir(path)


@tool
def tool_is_dir(path):
    """
    Check if path is a directory

    Arguments:
    path: the path to check

    Result:
    bool: True if is directory else if is file
    """
    return os.path.isdir(path)


@tool
def tool_platform():
    """Get which system/OS is running"""
    return platform()


tools = load_tools(
    ["ddg-search", "read_file", "terminal"], allow_dangerous_tools=True
) + [
    tool_platform,
    tool_env,
    tool_ls,
    tool_is_dir,
    tool_cwd,
]
app = create_react_agent(
    model,
    tools,
    checkpointer=checkpointer,
    state_modifier="You're A.V.A. Autonomous Virtual Assistant who is tasked to help your user well as possible. Keep answers short. Only use tools if strictly needed.",
    debug=True,
)

history = app.get_state(
    config={"configurable": {"thread_id": st.session_state.session_id}}
)

with st.spinner("Thinking..."):
    messages = history.values.get("messages", [])
    if len(messages) == 0:
        messages = [AIMessage("Hello, how may I assist you today?")]
        app.update_state(
            config={"configurable": {"thread_id": st.session_state.session_id}},
            values={"messages": messages},
        )
    for message in messages:
        if message.type not in ["human", "ai"] or message.content == "":
            continue
        with st.chat_message(message.type):
            st.markdown(message.content)

if prompt := st.chat_input("What is up?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            final_state = app.invoke(
                {"messages": [HumanMessage(content=prompt)]},
                config={"configurable": {"thread_id": st.session_state.session_id}},
            )
            st.write(final_state["messages"][-1].content)
