from typing import List, Dict, Any
from src.models.data_models import ExtractedData, ValidationResult

class ClaimValidator:
    """
    Service for validating extracted claim data for consistency and completeness.
    """
    
    def __init__(self):
        self.required_documents = ["hospital_bill", "discharge_summary"]
        self.optional_documents = ["insurance_card"]
    
    async def validate(self, extracted_data: List[ExtractedData]) -> ValidationResult:
        """
        Validate the extracted data for consistency and completeness.
        """
        missing_documents = self._check_missing_documents(extracted_data)
        discrepancies = self._check_discrepancies(extracted_data)
        warnings = self._check_warnings(extracted_data)
        
        return ValidationResult(
            missing_documents=missing_documents,
            discrepancies=discrepancies,
            warnings=warnings
        )
    
    def _check_missing_documents(self, extracted_data: List[ExtractedData]) -> List[str]:
        """
        Check for missing required documents.
        """
        missing = []
        document_types = [data.document_type for data in extracted_data]
        
        for required_doc in self.required_documents:
            if required_doc not in document_types:
                missing.append(f"Missing required document: {required_doc}")
        
        return missing
    
    def _check_discrepancies(self, extracted_data: List[ExtractedData]) -> List[str]:
        """
        Check for discrepancies between documents.
        """
        discrepancies = []
        
        # Group data by document type
        data_by_type = {}
        for data in extracted_data:
            data_by_type[data.document_type] = data.data
        
        # Check patient name consistency
        patient_names = []
        for doc_type in ["hospital_bill", "discharge_summary", "insurance_card"]:
            if doc_type in data_by_type:
                name = data_by_type[doc_type].get("patient_name") or data_by_type[doc_type].get("card_holder_name")
                if name:
                    patient_names.append((doc_type, name))
        
        if len(patient_names) > 1:
            # Check if names are consistent
            names = [name for _, name in patient_names]
            if not self._names_match(names):
                discrepancies.append(f"Patient name mismatch across documents: {', '.join([f'{doc}: {name}' for doc, name in patient_names])}")
        
        # Check date consistency
        if "hospital_bill" in data_by_type and "discharge_summary" in data_by_type:
            bill_data = data_by_type["hospital_bill"]
            discharge_data = data_by_type["discharge_summary"]
            
            # Check admission dates
            bill_admission = bill_data.get("admission_date")
            discharge_admission = discharge_data.get("admission_date")
            
            if bill_admission and discharge_admission and bill_admission != discharge_admission:
                discrepancies.append(f"Admission date mismatch: Bill shows {bill_admission}, Discharge summary shows {discharge_admission}")
            
            # Check discharge dates
            bill_discharge = bill_data.get("discharge_date")
            discharge_discharge = discharge_data.get("discharge_date")
            
            if bill_discharge and discharge_discharge and bill_discharge != discharge_discharge:
                discrepancies.append(f"Discharge date mismatch: Bill shows {bill_discharge}, Discharge summary shows {discharge_discharge}")
        
        # Check hospital name consistency
        hospital_names = []
        for doc_type in ["hospital_bill", "discharge_summary"]:
            if doc_type in data_by_type:
                hospital = data_by_type[doc_type].get("hospital_name")
                if hospital:
                    hospital_names.append((doc_type, hospital))
        
        if len(hospital_names) > 1:
            names = [name for _, name in hospital_names]
            if not self._hospital_names_match(names):
                discrepancies.append(f"Hospital name mismatch: {', '.join([f'{doc}: {name}' for doc, name in hospital_names])}")
        
        # Check insurance company consistency
        if "hospital_bill" in data_by_type and "insurance_card" in data_by_type:
            bill_insurance = data_by_type["hospital_bill"].get("insurance_company")
            card_insurance = data_by_type["insurance_card"].get("insurance_company")
            
            if bill_insurance and card_insurance and not self._insurance_companies_match(bill_insurance, card_insurance):
                discrepancies.append(f"Insurance company mismatch: Bill shows {bill_insurance}, Card shows {card_insurance}")
        
        return discrepancies
    
    def _check_warnings(self, extracted_data: List[ExtractedData]) -> List[str]:
        """
        Check for potential issues that are not critical but worth noting.
        """
        warnings = []
        
        # Check extraction confidence
        for data in extracted_data:
            if data.extraction_confidence < 0.5:
                warnings.append(f"Low confidence extraction for {data.document_type}: {data.extraction_confidence:.2f}")
        
        # Check for missing key fields
        data_by_type = {}
        for data in extracted_data:
            data_by_type[data.document_type] = data.data
        
        if "hospital_bill" in data_by_type:
            bill_data = data_by_type["hospital_bill"]
            if not bill_data.get("total_amount"):
                warnings.append("Hospital bill missing total amount")
            if not bill_data.get("patient_name"):
                warnings.append("Hospital bill missing patient name")
        
        if "discharge_summary" in data_by_type:
            discharge_data = data_by_type["discharge_summary"]
            if not discharge_data.get("diagnosis"):
                warnings.append("Discharge summary missing diagnosis")
            if not discharge_data.get("patient_name"):
                warnings.append("Discharge summary missing patient name")
        
        if "insurance_card" in data_by_type:
            insurance_data = data_by_type["insurance_card"]
            if not insurance_data.get("policy_number"):
                warnings.append("Insurance card missing policy number")
            if not insurance_data.get("sum_insured"):
                warnings.append("Insurance card missing sum insured amount")
        
        return warnings
    
    def _names_match(self, names: List[str]) -> bool:
        """
        Check if patient names are similar enough to be considered the same person.
        """
        if not names:
            return True
        
        # Normalize names for comparison
        normalized_names = []
        for name in names:
            # Convert to lowercase, remove extra spaces
            normalized = ' '.join(name.lower().split())
            normalized_names.append(normalized)
        
        # Check if all names are the same
        first_name = normalized_names[0]
        return all(name == first_name for name in normalized_names)
    
    def _hospital_names_match(self, names: List[str]) -> bool:
        """
        Check if hospital names are similar enough to be considered the same hospital.
        """
        if not names:
            return True
        
        # Normalize hospital names
        normalized_names = []
        for name in names:
            # Convert to lowercase, remove common words
            normalized = name.lower()
            # Remove common hospital suffixes/prefixes
            normalized = normalized.replace('hospital', '').replace('medical', '').replace('centre', '').replace('center', '')
            normalized = ' '.join(normalized.split())
            normalized_names.append(normalized)
        
        # Check if core names match
        first_name = normalized_names[0]
        return all(name == first_name for name in normalized_names)
    
    def _insurance_companies_match(self, company1: str, company2: str) -> bool:
        """
        Check if insurance company names refer to the same company.
        """
        # Normalize company names
        norm1 = company1.lower().replace('insurance', '').replace('general', '').replace('ltd', '').replace('limited', '')
        norm2 = company2.lower().replace('insurance', '').replace('general', '').replace('ltd', '').replace('limited', '')
        
        norm1 = ' '.join(norm1.split())
        norm2 = ' '.join(norm2.split())
        
        return norm1 == norm2

