from typing import List, Dict

def aggregate_results(results: List[Dict]) -> Dict:
    aggregated = {
        "total_claims": len(results),
        "processed_claims": results,
        "status": "completed"
    }
    return aggregated

def combine_agent_outputs(id_data: Dict, discharge_data: Dict, bill_data: Dict, classification: Dict) -> Dict:
    """
    Combines outputs from all extraction agents into a final JSON response.
    
    Args:
        id_data: Patient information from identity documents
        discharge_data: Information from discharge summaries
        bill_data: Itemized bill information
        classification: Document classification results
    
    Returns:
        Final combined JSON response
    """
    combined = {
        "patient_information": {
            "name": id_data.get("patient_name"),
            "date_of_birth": id_data.get("date_of_birth"),
            "id_number": id_data.get("id_number"),
            "policy_number": id_data.get("policy_number")
        },
        "medical_information": {
            "diagnosis": discharge_data.get("diagnosis"),
            "admission_date": discharge_data.get("admission_date"),
            "discharge_date": discharge_data.get("discharge_date"),
            "doctor_name": discharge_data.get("doctor_name")
        },
        "billing_information": {
            "items": bill_data.get("items", []),
            "total_amount": bill_data.get("total")
        },
        "document_classification": classification
    }
    
    return combined
