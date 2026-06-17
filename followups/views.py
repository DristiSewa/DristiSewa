from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import role_required
from core.services import filter_by_branch
from .forms import AppointmentForm, FollowUpForm
from .models import Appointment, FollowUp


@role_required("ADMIN", "MANAGER", "FRONTDESK")
def followup_list(request):
    followups = FollowUp.objects.select_related("student__user", "assigned_to")
    followups = filter_by_branch(request.user, followups, branch_field="student__user__branch")

    if request.method == "POST":
        form = FollowUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Follow-up saved.")
            return redirect("followups:followup_list")
        messages.error(request, "Please correct the errors below.")
    else:
        initial = {}
        student_id = request.GET.get("student")
        if student_id:
            initial["student"] = student_id
        form = FollowUpForm(initial=initial)

    return render(
        request,
        "followups/followup_list.html",
        {
            "followups": followups,
            "form": form,
            "pending_count": followups.filter(is_done=False).count(),
            "done_count": followups.filter(is_done=True).count(),
        },
    )


@role_required("ADMIN", "MANAGER", "FRONTDESK")
def followup_toggle(request, pk):
    followup = get_object_or_404(FollowUp, pk=pk)
    if request.method == "POST" and "status" in request.POST:
        followup.is_done = request.POST.get("status") == "completed"
    else:
        followup.is_done = not followup.is_done
    followup.save(update_fields=["is_done"])
    messages.success(request, "Follow-up status updated.")
    return redirect("followups:followup_list")


@role_required("ADMIN", "MANAGER", "FRONTDESK")
def appointment_list(request):
    appointments = Appointment.objects.select_related("student__user", "staff")
    appointments = filter_by_branch(request.user, appointments, branch_field="student__user__branch")

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment created.")
            return redirect("followups:appointment_list")
        messages.error(request, "Please correct the errors below.")
    else:
        form = AppointmentForm()

    return render(request, "followups/appointment_list.html", {"appointments": appointments, "form": form})


@role_required("ADMIN", "MANAGER", "FRONTDESK")
def appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            appointment = form.save(commit=False)
            if appointment.status == Appointment.Status.SCHEDULED and "appointment_date" in form.changed_data:
                appointment.status = Appointment.Status.RESCHEDULED
            appointment.save()
            messages.success(request, "Appointment updated.")
            return redirect("followups:appointment_list")
        messages.error(request, "Please correct the errors below.")
    else:
        form = AppointmentForm(instance=appointment)

    return render(request, "followups/appointment_form.html", {"form": form, "appointment": appointment})


@role_required("ADMIN", "MANAGER", "FRONTDESK")
def appointment_cancel(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.status = Appointment.Status.CANCELLED
    appointment.save(update_fields=["status"])
    messages.success(request, "Appointment cancelled.")
    return redirect("followups:appointment_list")
