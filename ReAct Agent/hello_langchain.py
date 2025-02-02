#from dotenv import load_dotenv
#from langchain_core.messages import HumanMessage,SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

# load_dotenv()

llm = ChatOpenAI(model="gpt-4")

query = input("Enter the name of Celebrity")

prompt_template = PromptTemplate.from_template(
    template = "who is {input}?"
)

output_format = StrOutputParser()
chain = prompt_template | llm | output_format

result = chain.invoke({"input":query})

# messages = [
#     SystemMessage(content="You are a scientist is Quantum Pyshics and have no idea  about any sports, you can answer questions related to only physics, if anything else is asked you can respond as out of scope"),
#     HumanMessage(content = query)
# ]

# result = llm.invoke(messages)

print(result)