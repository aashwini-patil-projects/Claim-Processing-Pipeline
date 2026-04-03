from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict
import os

class DocumentClassification(BaseModel):
    claim_forms: List[int] = Field(default_factory=list, description="Page numbers containing claim forms")
    cheque_or_bank_details: List[int] = Field(default_factory=list, description="Page numbers containing cheque or bank details")
    identity_document: List[int] = Field(default_factory=list, description="Page numbers containing identity documents")
    itemized_bill: List[int] = Field(default_factory=list, description="Page numbers containing itemized bills")
    discharge_summary: List[int] = Field(default_factory=list, description="Page numbers containing discharge summaries")
    prescription: List[int] = Field(default_factory=list, description="Page numbers containing prescriptions")
    investigation_report: List[int] = Field(default_factory=list, description="Page numbers containing investigation reports")
    cash_receipt: List[int] = Field(default_factory=list, description="Page numbers containing cash receipts")
    other: List[int] = Field(default_factory=list, description="Page numbers containing other document types")

def get_llm():
    """Lazy initialization of LLM"""
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        temperature=0
    )

parser = PydanticOutputParser(pydantic_object=DocumentClassification)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a medical insurance document classification expert. Analyze each page carefully and classify it into EXACTLY ONE category.

CATEGORY DEFINITIONS:

1. claim_forms: Insurance claim application forms with fields for policy details, claimant information
2. cheque_or_bank_details: Bank statements, cancelled cheques, account details, IFSC codes
3. identity_document: Government IDs (Aadhaar, PAN card, passport, driver's license, voter ID)
4. itemized_bill: Hospital bills with line-by-line charges (room charges, medicines, procedures with individual costs)
5. discharge_summary: Hospital discharge papers with diagnosis, treatment summary, admission/discharge dates
6. prescription: Doctor's prescription with medicines, dosage, doctor's signature
7. investigation_report: Lab reports, X-rays, MRI, CT scan, blood test results, pathology reports
8. cash_receipt: Payment receipts showing amount paid, date, hospital stamp
9. other: Documents that don't fit any above category

CLASSIFICATION RULES:
- Look for keywords: "discharge summary", "prescription", "bill", "receipt", "lab report", "Aadhaar", "PAN"
- Check for doctor signatures, hospital letterheads, test results, itemized charges
- Each page goes to EXACTLY ONE category
- Be specific - don't default to "other" unless truly unclassifiable

{format_instructions}"""),
    ("user", "Classify each page below:\n\n{pages}")
])

async def classify_documents(pages: List[Dict[str, any]]) -> Dict[str, List[int]]:
    llm = get_llm()
    
    # Build pages text
    pages_text = "\n\n".join([
        f"=== PAGE {page['page']} ===\n{page['text'][:1000]}"
        for page in pages
    ])
    
    # Debug logging
    print("\n" + "="*60)
    print("CLASSIFIER DEBUG INFO")
    print("="*60)
    print(f"Total pages to classify: {len(pages)}")
    for page in pages[:2]:  # Show first 2 pages
        text_preview = page['text'][:200] if page['text'] else "[EMPTY]"
        print(f"\nPage {page['page']} preview (first 200 chars):")
        print(f"  Length: {len(page['text'])} characters")
        print(f"  Content: {text_preview}")
    print("="*60 + "\n")
    
    formatted_prompt = prompt.format_messages(
        format_instructions=parser.get_format_instructions(),
        pages=pages_text
    )
    
    response = await llm.agenerate([formatted_prompt])
    result_text = response.generations[0][0].text
    
    # Debug: Show LLM response
    print("\n" + "="*60)
    print("LLM CLASSIFICATION RESPONSE")
    print("="*60)
    print(result_text)
    print("="*60 + "\n")
    
    classification = parser.parse(result_text)
    return classification.dict()
