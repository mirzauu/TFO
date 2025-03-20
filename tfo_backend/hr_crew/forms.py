from django import forms
from .models import Candidate
from django import forms
from .models import EmployeeDocuments

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'email', 'resume']


class EmployeeDocumentsForm(forms.ModelForm):
    class Meta:
        model = EmployeeDocuments
        fields = [
            "relieving_letter",
            "salary_slip",
            "aadhaar_image",
            "pan_image",
            "bank_account_number",
            "ifsc_code",
        ]
