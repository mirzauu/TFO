from django.urls import path
from .views import candidate_submission,add_schedule,book_slot_by_candidate,candidate_selection_view,upload_employee_documents,employee_documents_detail

urlpatterns = [
   path('apply/<uuid:uuid>/', candidate_submission, name='candidate_submission'),
     path('recruitment/<int:recruitment_id>/add_schedule/', add_schedule, name='add_schedule'),
     path('book-slot/<int:candidate_id>/', book_slot_by_candidate, name='book_slot_by_candidate'),
     path('recruitment/<int:recruitment_id>/candidates/', candidate_selection_view, name='candidate_selection'),
     path("upload-documents/<int:onboarding_id>/", upload_employee_documents, name="upload_employee_documents"),
      path("employee-documents/<int:onboarding_id>/", employee_documents_detail, name="employee_documents_detail"),
     


]


