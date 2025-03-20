from django.shortcuts import render,redirect
from django.views import View
from .models import Recruitment,RecruitmentTask,Schedule,Candidate,Booking
from .forms import Candidate,CandidateForm
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_date
from datetime import datetime
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Onboarding, EmployeeDocuments
from .forms import EmployeeDocumentsForm  # Create this form

def candidate_submission(request, uuid):
    recruitment = get_object_or_404(Recruitment, uuid=uuid)  # Fetch recruitment by UUID
    success_message = None  # Variable to store success message
    error_message = None  # Variable to store error message

    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']

            # Check if the candidate already applied
            if Candidate.objects.filter(email=email, recruitment=recruitment).exists():
                error_message = "You have already applied for this job."
            else:
                candidate = form.save(commit=False)
                candidate.recruitment = recruitment  # Link to recruitment
                candidate.save()
                success_message = "Your application has been submitted successfully!"
                form = CandidateForm()  # Reset form after successful submission

    else:
        form = CandidateForm()

    return render(request, 'recruitment\candidate_submission.html', {
        'form': form,
        'recruitment': recruitment,
        'success': success_message,
        'error': error_message
    })  




@csrf_exempt
def add_schedule(request, recruitment_id):
    """
    API to add available date and time slots for a recruitment, including the meet link.
    """
    recruitment = get_object_or_404(Recruitment, id=recruitment_id)
    
    # Fetch all available slots
    available_slots = Schedule.objects.filter(recruitment=recruitment).order_by("date", "time_slot")

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            date_str = data.get("date")
            time_str = data.get("time_slot")
            meet_link = data.get("meet_link", "").strip()  # Fetching meet link from request
            print(data)
            if not meet_link:
                return JsonResponse({"error": "Meet link is required"}, status=400)

            date_obj = parse_date(date_str)
            time_obj = datetime.strptime(time_str, "%H:%M").time()

            # Check if the slot already exists
            if Schedule.objects.filter(recruitment=recruitment, date=date_obj, time_slot=time_obj).exists():
                return JsonResponse({"error": "Time slot already exists for this recruitment"}, status=400)

            # Create the schedule with the meet link
            schedule = Schedule.objects.create(
                recruitment=recruitment,
                date=date_obj,
                time_slot=time_obj,
                meet_link=meet_link  # Ensure your Schedule model has this field
            )

            return JsonResponse({"message": "Schedule added successfully", "id": schedule.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    # Render the template and pass available slots
    return render(request, "recruitment/add_slots.html", {"recruitment": recruitment, "available_slots": available_slots})
def book_slot_by_candidate(request, candidate_id):
    # Fetch the candidate using the candidate_id
    candidate = get_object_or_404(Candidate, id=candidate_id)
    recruitment = candidate.recruitment  # Get the related recruitment session
    
    # Ensure the candidate is linked to the recruitment session
    if not recruitment:
        return HttpResponse("Recruitment session not found", status=404)

    # If the candidate has already booked a slot, redirect to a thank-you page or similar
    if Booking.objects.filter(candidate=candidate).exists():
        return HttpResponse("You have already booked a slot.", status=400)

    # Handling the POST request for booking
    if request.method == "POST":
        schedule_id = request.POST.get("schedule_id")
        schedule = get_object_or_404(Schedule, id=schedule_id, recruitment=recruitment)
        candidate.interview_status=True
        candidate.save()

        # Check if the schedule is already booked
        if schedule.is_booked:
            messages.error(request, "This time slot is already booked.")
            return redirect("book_slot_by_candidate", candidate_id=candidate.id)

        # Create the booking for the candidate
        booking = Booking(schedule=schedule, candidate=candidate)
        booking.save()
        schedule.is_booked = True
        schedule.save()
        messages.success(request, "Your Slot booking has been successfully made!")

        

    # Fetch available schedules for the recruitment session
    schedules = Schedule.objects.filter(recruitment=recruitment, is_booked=False)

    return render(request, "recruitment/book_slot_by_candidate.html", {
        "recruitment": recruitment,
        "candidate": candidate,
        "schedules": schedules
    })


def candidate_selection_view(request, recruitment_id):
    recruitment = get_object_or_404(Recruitment, id=recruitment_id)
    candidates = Candidate.objects.filter(recruitment=recruitment, interview_status=True).prefetch_related('bookings')

    if request.method == "POST":
        selected_candidates = request.POST.getlist("selected_candidates")
        
        for candidate in candidates:
            candidate.selected = str(candidate.id) in selected_candidates
            
            # Check if an offer letter was uploaded
            offer_letter_field = f'offer_letter_document_{candidate.id}'
            if offer_letter_field in request.FILES:
                candidate.offer_letter_document = request.FILES[offer_letter_field]

            candidate.save()

    return render(request, "recruitment/candidate_selection.html", {"candidates": candidates, "recruitment": recruitment})



def upload_employee_documents(request, onboarding_id):
    onboarding = get_object_or_404(Onboarding, id=onboarding_id)

    # Check if documents already exist, else create a new entry
    documents, created = EmployeeDocuments.objects.get_or_create(onboarding=onboarding)

    if request.method == "POST":
        form = EmployeeDocumentsForm(request.POST, request.FILES, instance=documents)
        if form.is_valid():
            form.save()
            messages.success(request, "Documents uploaded successfully!")
            return redirect("upload_employee_documents", onboarding_id=onboarding.id)
        else:
            messages.error(request, "There was an error uploading the documents.")

    else:
        form = EmployeeDocumentsForm(instance=documents)

    return render(request, "onboarding/upload_documents.html", {"form": form, "onboarding": onboarding})


def employee_documents_detail(request, onboarding_id):
    onboarding = get_object_or_404(Onboarding, id=onboarding_id)
    documents = get_object_or_404(EmployeeDocuments, onboarding=onboarding)

    if request.method == "POST":  # When the "Verify" button is clicked
        documents.verified = True
        documents.save()
        messages.success(request, "Employee documents verified successfully!")
        return redirect("employee_documents_detail", onboarding_id=onboarding.id)

    return render(request, "onboarding/employee_documents_detail.html", {"documents": documents, "onboarding": onboarding})