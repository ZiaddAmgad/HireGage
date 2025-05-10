from typing import Annotated

from typing import TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from .system_prompt import SYSTEM_PROMPT
from .tools import Tools
from langgraph.prebuilt import ToolNode, tools_condition


memory = MemorySaver()

llm = ChatOllama(model="llama3.2:latest")

llm_with_tools = llm.bind_tools(Tools.get_tools())


class State(TypedDict):
    messages: Annotated[list, add_messages] 


graph_builder = StateGraph(State)


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

tool_node = ToolNode(tools=Tools.get_tools())


graph_builder.add_node("chatbot", chatbot)


graph_builder.add_node("tools", tool_node)


config = {"configurable": {"thread_id": "1"}}




graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition
)

graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile(checkpointer=memory)

def stream_graph_updates(user_input: str=''):
    messages = [{
        'role':'system',
        'content': SYSTEM_PROMPT
    }
    ,{'role':'assistant',
        'content': 'Job Title: Software Engineer\nJob Description: We are looking for a software engineer with experience in Python and JavaScript. The candidate should have a strong understanding of algorithms and data structures. The candidate should also have experience with web development frameworks such as Django or Flask.'
   }]
    
    if user_input:
        messages.append({'role':'user', 'content': user_input})

    for event in graph.stream({"messages": messages},config=config):
        for value in event.values():

            if not 'tools' in event  and value["messages"]:
                print("Interviewer:", value["messages"][-1].content)
                return value["messages"][-1].content
            else:
                if 'tools' in event :
                    print('tool called')
        
