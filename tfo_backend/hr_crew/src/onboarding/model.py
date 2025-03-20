from pydantic import BaseModel

from typing import List, Optional
from pydantic import BaseModel, Field

# --- BaseModel ---
class NewHireInfo(BaseModel):
    employee_id: Optional[str] = Field(None, description="employee_id of the new hire.")
    first_name: Optional[str] = Field(None, description="First name of the new hire.")
    last_name: Optional[str] = Field(None, description="Last name of the new hire.")
    start_date: Optional[str] = Field(None, description="Start date of the new hire.")
    role: Optional[str] = Field(None, description="Role assigned to the new hire.")
    department: Optional[str] = Field(None, description="Department of the new hire.")
    email: Optional[str] = Field(None, description="Email address of the new hire.")
    orientation_schedule: Optional[str] = Field(None, description="Personalized orientation schedule.")
    document_status: Optional[str] = Field(None, description="Status of document collection and verification.")
    it_setup_status: Optional[str] = Field(None, description="Status of IT setup for the new hire.")
