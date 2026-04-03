from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import os

class PatientInfo(BaseModel):
    patient_name: Optional[str] = Field(None, description="Full name of the patient")
    date_of_birth: Optional[str] = Field(None, description="Date of birth in any format found")
    id_number: Optional[str] = Field(None, description="Identity document number")
    policy_number: Optional[str] = Field(None, description="Insurance policy number")

def get_llm():
    """Lazy initialization of LLM"""
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        temperature=0
    )

parser = PydanticOutputParser(pydantic_object=PatientInfo)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert at extracting patient information from medical documents, identity documents, and claim forms.

Extract the following fields from ANY document provided:
- patient_name: Full name (look for: Name, Patient Name, Full Name, Insured Name, Cardholder Name, Policyholder)
- date_of_birth: Date of birth (look for: DOB, Date of Birth, Birth Date, Born, D.O.B)
- id_number: Any ID number (look for: ID No, Aadhaar, PAN, Passport No, License No, SSN, National ID, Driver License)
- policy_number: Insurance policy number (look for: Policy No, Policy Number, Member ID, Insurance ID, Plan Number, Policy ID)

IMPORTANT RULES:
- Search ALL pages provided - patient info may be on claim forms, not just ID documents
- Extract the FIRST name you find - it's likely the patient
- Look for dates in format like "March 15, 1985" or "03/15/1985" or "15-03-1985"
- Extract ANY alphanumeric ID or policy numbers
- If multiple values found, prefer the most complete one
- If a field is not found anywhere, return null

{format_instructions}"""),
    ("user", "Extract patient information from these documents:\n\n{pages}")
])

async def extract_identity_info(pages: List[Dict[str, any]]) -> Dict:
    if not pages:
        return {
            "patient_name": None,
            "date_of_birth": None,
            "id_number": None,
            "policy_number": None
        }
    
    llm = get_llm()
    
    # Include full text for better extraction
    pages_text = "\n\n".join([
        f"=== PAGE {page['page']} ===\n{page['text']}"
        for page in pages
    ])
    
    # Debug: Show what text is being sent
    print("\n" + "="*60)
    print("IDENTITY EXTRACTOR DEBUG")
    print("="*60)
    print(f"Processing {len(pages)} page(s) for patient information")
    for page in pages:
        print(f"\nPage {page['page']} text (first 300 chars):")
        print(page['text'][:300] if page['text'] else "[EMPTY]")
    print("="*60 + "\n")
    
    formatted_prompt = prompt.format_messages(
        format_instructions=parser.get_format_instructions(),
        pages=pages_text
    )
    
    response = await llm.agenerate([formatted_prompt])
    result_text = response.generations[0][0].text
    
    # Debug: Show extraction result
    print("\n" + "="*60)
    print("IDENTITY EXTRACTION RESULT")
    print("="*60)
    print(result_text)
    print("="*60 + "\n")
    
    patient_info = parser.parse(result_text)
    return patient_info.dict()
