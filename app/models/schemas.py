from pydantic import BaseModel
from typing import List, Dict, Optional

class PatientInformation(BaseModel):
    name: Optional[str]
    date_of_birth: Optional[str]
    id_number: Optional[str]
    policy_number: Optional[str]

class MedicalInformation(BaseModel):
    diagnosis: Optional[str]
    admission_date: Optional[str]
    discharge_date: Optional[str]
    doctor_name: Optional[str]

class BillItem(BaseModel):
    name: str
    cost: str

class BillingInformation(BaseModel):
    items: List[BillItem]
    total_amount: Optional[str]

class ProcessResponse(BaseModel):
    claim_id: str
    patient_information: PatientInformation
    medical_information: MedicalInformation
    billing_information: BillingInformation
    document_classification: Dict[str, List[int]]
    status: str
