from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import role_required
from core.services import filter_by_branch
from students.models import Student
from .forms import DocumentReviewForm, DocumentUploadForm
from .models import Document


@role_required("STUDENT")
def upload_docs(request):
    student, _ = Student.objects.get_or_create(user=request.user)
    documents = student.documents.all()

    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.student = student
            document.save()
            messages.success(request, "Document uploaded successfully.")
            return redirect("documents:upload_docs")
        messages.error(request, "Please correct the errors below.")
    else:
        form = DocumentUploadForm()

    return render(request, "documents/upload_docs.html", {"documents": documents, "form": form})


@role_required("ADMIN", "MANAGER", "FRONTDESK")
def document_review(request):
    documents = Document.objects.select_related("student__user", "student__user__branch")
    documents = filter_by_branch(request.user, documents, branch_field="student__user__branch")

    status_filter = request.GET.get("status", "")
    if status_filter:
        documents = documents.filter(status=status_filter)

    if request.method == "POST":
        document = get_object_or_404(Document, pk=request.POST.get("document_id"))
        form = DocumentReviewForm(request.POST, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, "Document review saved.")
        return redirect("documents:document_review")

    return render(
        request,
        "documents/document_review.html",
        {"documents": documents, "statuses": Document.Status.choices, "status_filter": status_filter},
    )
