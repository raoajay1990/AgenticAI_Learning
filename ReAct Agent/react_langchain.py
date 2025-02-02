from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain import hub
from langchain.agents import create_react_agent
from langchain.agents import AgentExecutor
from tools.system_time_tool import check_system_time

print(f"Working on ReAct agent: Agent capable of reasing and taking actions")

llm = ChatOpenAI(model = "gpt-4")

query  = "What is the current time in new York (you are in India)"
prompt_template = hub.pull("hwchase17/react")

# print(f"Promt Template : {prompt_template}")

tools = [check_system_time]

react_agent = create_react_agent(
    llm = llm,
    tools = tools,
    prompt = prompt_template
)

agent_executor = AgentExecutor(
    agent = react_agent,
    verbose= True,
    tools= tools
)

result = agent_executor.invoke({"input": query})
print(result)

