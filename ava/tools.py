import os
from platform import platform
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_core.tools import tool


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


LOADED_TOOLS = load_tools(
    ["ddg-search", "read_file", "terminal"], allow_dangerous_tools=True
)

TOOLS = LOADED_TOOLS + [
    tool_platform,
    tool_env,
    tool_ls,
    tool_is_dir,
    tool_cwd,
]
