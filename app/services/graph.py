from typing import Dict
from app.services.pdf_loader import load_pdf
from app.services.classifier import classify_documents
from app.services.extractor import extract_identity_info
from app.services.discharge_extractor import extract_discharge_summary
from app.services.bill_extractor import extract_itemized_bill
from app.services.aggregator import combine_agent_outputs

async def process_claim(file_path: str, claim_id: str) -> Dict:
    """
    Main workflow function that processes a claim PDF through the entire pipeline.
    
    Steps:
    1. Load PDF and split into pages
    2. Run segregator (classifier) to categorize pages
    3. Route relevant pages to specific agents
    4. Run extraction agents in parallel
    5. Aggregate results into final response
    
    Args:
        file_path: Path to the PDF file
        claim_id: Unique claim identifier
    
    Returns:
        Final aggregated JSON response
    """
    # Step 1: Load PDF
    pages = load_pdf(file_path)
    
    # Step 2: Run segregator (classify pages)
    classification = await classify_documents(pages)
    
    # Step 3: Route pages to agents
    # For patient info: check identity documents, claim forms, and first few pages
    identity_pages = [p for p in pages if p["page"] in classification.get("identity_document", [])]
    claim_form_pages = [p for p in pages if p["page"] in classification.get("claim_forms", [])]
    
    # Combine identity and claim form pages for patient extraction
    patient_info_pages = identity_pages + claim_form_pages
    
    # If no identity/claim pages found, use first 3 pages as fallback
    if not patient_info_pages:
        patient_info_pages = pages[:3]
        print("⚠️ No identity/claim pages found, using first 3 pages for patient extraction")
    
    discharge_pages = [p for p in pages if p["page"] in classification.get("discharge_summary", [])]
    bill_pages = [p for p in pages if p["page"] in classification.get("itemized_bill", [])]
    
    # Step 4: Run agents (extract information from relevant pages only)
    id_data = await extract_identity_info(patient_info_pages)
    
    # If patient info is incomplete, try searching all pages
    if not id_data.get("patient_name") or not id_data.get("date_of_birth"):
        print("⚠️ Patient info incomplete, searching all pages...")
        id_data = await extract_identity_info(pages[:5])  # Search first 5 pages
    
    discharge_data = await extract_discharge_summary(discharge_pages)
    bill_data = await extract_itemized_bill(bill_pages)
    
    # Step 5: Aggregate result
    final_result = combine_agent_outputs(
        id_data=id_data,
        discharge_data=discharge_data,
        bill_data=bill_data,
        classification=classification
    )
    
    final_result["claim_id"] = claim_id
    final_result["status"] = "completed"
    
    return final_result
