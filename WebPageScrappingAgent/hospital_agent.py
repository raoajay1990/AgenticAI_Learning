# hospital_agent.py
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_community.document_transformers import BeautifulSoupTransformer
from langchain_openai import ChatOpenAI
from langchain import hub
import pandas as pd
import re
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print(api_key)
# 1. Configure LLM with temperature 0 for precise extraction
llm = ChatOpenAI(temperature=0, model="gpt-4o")

# 2. Define data extraction schema
hospital_schema = {
    "properties": {
        "hospital_name": {"type": "string", "description": "Full hospital name with tags"},
        "tags": {"type": "string", "description": "Hospital tags like SmartSelect/VFM/Gramin"},
        "doctor_count": {"type": "number", "description": "Total number of doctors"},
        "bed_count": {"type": "number", "description": "Total number of beds"},
        "accreditations": {"type": "string", "description": "Accreditations if any"},
        "address": {"type": "string", "description": "Full hospital address"}
    },
    "required": ["hospital_name", "doctor_count", "bed_count", "address"]
}

# 3. Create web scraping tool
def hospital_scraper(url: str) -> dict:
    """Scrape and extract hospital data from webpage"""
    try:
        # Load and parse HTML
        loader = AsyncHtmlLoader([url])
        docs = loader.load()
        transformer = BeautifulSoupTransformer()
        transformed_docs = transformer.transform_documents(
            docs, tags_to_extract=["div", "span", "p"]
        )
        
        # Extract structured data
        content = transformed_docs[0].page_content
        return {
            "hospital_name": re.search(r"^(.*?)\s+(SmartSelect|VFM|Gramin)", content).group(0).strip(),
            "tags": re.search(r"(SmartSelect|VFM|Gramin)", content).group(1),
            "doctor_count": int(re.search(r"Total Doctor Count\s*(\d+)", content).group(1)),
            "bed_count": int(re.search(r"Total Bed Count\s*(\d+)", content).group(1)),
            "accreditations": re.search(r"Accreditations\s*(.*?)(?=\n\w+)", content).group(1).strip() or "N/A",
            "address": re.sub(r"\s+", " ", re.search(r"Hospital Address\s*(.*?)(?=\n\w+|$)", content, re.DOTALL).group(1)).strip()
        }
    except Exception as e:
        return {"error": str(e)}

# 4. Create Excel export tool
def save_to_excel(data: dict, filename="hospitals.xlsx"):
    """Save extracted data to Excel file"""
    df = pd.DataFrame([data])
    df.to_excel(filename, index=False)
    return f"Data saved to {filename}"

# 5. Set up ReAct agent
tools = [
    Tool(
        name="WebScraper",
        func=hospital_scraper,
        description="Scrapes hospital websites for critical information"
    ),
    Tool(
        name="ExcelExporter",
        func=save_to_excel,
        description="Saves structured data to Excel files"
    )
]

prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 6. Execution flow
if __name__ == "__main__":
    result = agent_executor.invoke({
        "input": "Scrape https://www.careinsurance.com/health-plan-network-hospitals.html?search_type=ipd&latlng=&search1=Hyderabad&search2=&button=Submit and save hospital details to Excel with columns: Hospital Name, Tags, Doctor Count, Bed Count, Accreditations, Address"
    })
    
    print(f"Final Result: {result['output']}")
