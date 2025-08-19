# pip install 'bubbletea-chat[llm]'
# pip install openai
import bubbletea_chat as bt
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

todo_list = []
history = []

tools = [
    {
        "type": "function",
        "name": "add_todo",
        "description": "Add a todo to the list",
        "parameters": {
            "type": "object",
            "properties": {
                "todo": {
                    "type": "string",
                    "description": "A todo string",
                },
            },
            "required": ["todo"],
        },
    },
    {
        "type": "function",
        "name": "remove_todo",
        "description": "Remove given todo from the list",
        "parameters": {
            "type": "object",
            "properties": {
                "todo": {
                    "type": "string",
                    "description": "A todo string",
                },
            },
            "required": ["todo"],
        },
    },
    {
        "type": "function",
        "name": "show_list",
        "description": "Show the list of todos",
    },
]

def add_todo(todo):
    todo_list.append(todo)
    return f"Task {todo} added"

def remove_todo(todo):
    try:
        todo_list.remove(todo)
    except:
        print(f"Remove {todo} failed")
        return f"Task {todo} remove failed"
    return f"Task {todo} removed"

def show_list():
    return todo_list

def call_function(name, args):
    if name == "add_todo":
        return add_todo(**args)
    if name == "remove_todo":
        return remove_todo(**args)
    if name == "show_list":
        return show_list()
    

@bt.chatbot
def echo_bot(message: str):
    history.append(message)

    input_list = [
        {"role": "user", "content": '\n'.join(history)}
    ]
    response = client.responses.create(
        model="gpt-5",
        instructions="Perform tool-calling only for the last sentence in the prompt.",
        tools=tools,
        input=input_list,
    )

    input_list += response.output
    final_result = ""

    for tool_call in response.output:
        if tool_call.type != "function_call":
            continue

        name = tool_call.name
        args = json.loads(tool_call.arguments)

        result = call_function(name, args)
        final_result = str(result)
    
    # Simple echo bot
    return bt.Text(final_result)

if __name__ == "__main__":
    # Creates /chat endpoint automatically
    bt.run_server(echo_bot, port=8000, host="0.0.0.0")
