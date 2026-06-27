# agent/agent.py
import os
from langchain_groq import ChatGroq
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_classic.memory import ConversationBufferWindowMemory
from agent.tools import search_products, get_reviews, check_order_status, escalate_to_human
from dotenv import load_dotenv

load_dotenv()

TOOLS = [search_products, get_reviews, check_order_status, escalate_to_human]

SYSTEM_PROMPT = """You are ShopBot, a helpful customer support agent for an online electronics store that sells Amazon devices (Kindles, Fire tablets, chargers, accessories).

You have access to these tools:
{tools}

Tool names: {tool_names}

You MUST follow this EXACT format every single time:

Question: the input question
Thought: what I should do
Action: search_products
Action Input: the search query
Observation: the result
Thought: I have enough information to answer now
Final Answer: the response to the customer

STRICT RULES:
1. ALWAYS call exactly ONE tool, then write Final Answer
2. NEVER write "Action: None" — always use a real tool name
3. NEVER repeat a tool call
4. If the query is out of scope (novels, food, clothing), still call search_products with a related electronics term, then in Final Answer explain what the store sells and suggest a relevant product
5. Final Answer must be a friendly, readable sentence — NOT a raw list

Previous conversation:
{chat_history}

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

def build_agent():
    llm = ChatGroq(
        model="llama-3.3-70b-versatile", 
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
    )

    prompt = PromptTemplate.from_template(SYSTEM_PROMPT)
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        k=5,
        return_messages=False
    )

    agent = create_react_agent(llm, TOOLS, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=TOOLS,
        memory=memory,
        verbose=True,
        max_iterations=4,
        max_execution_time=30,
        handle_parsing_errors=True,
        return_intermediate_steps=True,  # We'll use this for fallback
    )
    return executor

_agent = None

def get_agent():
    global _agent
    if _agent is None:
        _agent = build_agent()
    return _agent