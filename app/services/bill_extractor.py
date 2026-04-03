from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import os

class BillItem(BaseModel):
    name: str = Field(description="Name or description of the item/service")
    cost: str = Field(description="Cost of the item")

class ItemizedBillInfo(BaseModel):
    items: List[BillItem] = Field(default_factory=list, description="List of itemized charges")
    total: Optional[str] = Field(None, description="Total amount of the bill")

def get_llm():
    """Lazy initialization of LLM"""
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        temperature=0
    )

parser = PydanticOutputParser(pydantic_object=ItemizedBillInfo)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert at extracting information from itemized bills.
Extract the following:
- items: List of all line items with their name and cost
- total: Total amount of the bill

For each item, extract:
- name: Description of the service/item
- cost: Amount charged (keep original format with currency)

If total is not found, return null.

{format_instructions}"""),
    ("user", "Extract information from these itemized bill pages:\n\n{pages}")
])

async def extract_itemized_bill(pages: List[Dict[str, any]]) -> Dict:
    if not pages:
        return {
            "items": [],
            "total": None
        }
    
    llm = get_llm()
    
    pages_text = "\n\n".join([
        f"Page {page['page']}:\n{page['text']}"
        for page in pages
    ])
    
    formatted_prompt = prompt.format_messages(
        format_instructions=parser.get_format_instructions(),
        pages=pages_text
    )
    
    response = await llm.agenerate([formatted_prompt])
    result_text = response.generations[0][0].text
    
    bill_info = parser.parse(result_text)
    return bill_info.dict()
