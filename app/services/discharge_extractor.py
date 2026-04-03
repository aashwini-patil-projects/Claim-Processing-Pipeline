from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import os

class DischargeSummaryInfo(BaseModel):
    diagnosis: Optional[str] = Field(None, description="Primary diagnosis or list of diagnoses")
    admission_date: Optional[str] = Field(None, description="Date of hospital admission")
    discharge_date: Optional[str] = Field(None, description="Date of hospital discharge")
    doctor_name: Optional[str] = Field(None, description="Name of the attending doctor")

def get_llm():
    """Lazy initialization of LLM"""
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        temperature=0
    )

parser = PydanticOutputParser(pydantic_object=DischargeSummaryInfo)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert at extracting information from hospital discharge summaries.
Extract the following fields:
- diagnosis: Primary diagnosis or list of diagnoses
- admission_date: Date patient was admitted (keep original format)
- discharge_date: Date patient was discharged (keep original format)
- doctor_name: Name of the attending/discharging doctor

If a field is not found, return null for that field.

{format_instructions}"""),
    ("user", "Extract information from these discharge summary pages:\n\n{pages}")
])

async def extract_discharge_summary(pages: List[Dict[str, any]]) -> Dict:
    if not pages:
        return {
            "diagnosis": None,
            "admission_date": None,
            "discharge_date": None,
            "doctor_name": None
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
    
    discharge_info = parser.parse(result_text)
    return discharge_info.dict()
