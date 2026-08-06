import json

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import role_required
from .forms import BranchForm
from .models import Branch

User = get_user_model()


@role_required("ADMIN")
def create_branch_json(request):
    """Quick AJAX branch creation used by the admin Branch & Staff drawer."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

    try:
        payload = json.loads(request.body or "{}")
    except (ValueError, TypeError):
        return JsonResponse({"success": False, "error": "Invalid request payload."}, status=400)

    name = (payload.get("branch_name") or "").strip()
    location = (payload.get("location") or "").strip()

    if not name:
        return JsonResponse({"success": False, "error": "Branch name is required."}, status=400)

    if Branch.objects.filter(name__iexact=name).exists():
        return JsonResponse({"success": False, "error": "Branch already exists."}, status=400)

    base_code = "".join(ch for ch in name.upper() if ch.isalnum())[:8] or "BR"
    code = base_code
    suffix = 1
    while Branch.objects.filter(code=code).exists():
        suffix += 1
        code = f"{base_code}{suffix}"

    branch = Branch.objects.create(name=name, code=code, address=location)
    return JsonResponse({
        "success": True,
        "branch_id": branch.id,
        "name": branch.name,
        "code": branch.code,
        "address": branch.address,
    })


@role_required("ADMIN")
def update_branch_json(request, branch_id):
    """Update the editable branch details from the Branch & Staff cards."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

    try:
        payload = json.loads(request.body or "{}")
    except (ValueError, TypeError):
        return JsonResponse({"success": False, "error": "Invalid request payload."}, status=400)

    branch = get_object_or_404(Branch, pk=branch_id)
    name = (payload.get("branch_name") or "").strip()
    address = (payload.get("location") or "").strip()
    is_active = payload.get("is_active", branch.is_active)

    if not name:
        return JsonResponse({"success": False, "error": "Branch name is required."}, status=400)
    if not isinstance(is_active, bool):
        return JsonResponse({"success": False, "error": "Invalid branch status."}, status=400)
    if Branch.objects.filter(name__iexact=name).exclude(pk=branch.pk).exists():
        return JsonResponse({"success": False, "error": "A branch with this name already exists."}, status=400)

    branch.name = name
    branch.address = address
    branch.is_active = is_active
    branch.save(update_fields=["name", "address", "is_active", "updated_at"])
    return JsonResponse({
        "success": True,
        "branch_id": branch.id,
        "name": branch.name,
        "address": branch.address,
        "is_active": branch.is_active,
    })


@role_required("ADMIN")
def delete_branch_json(request, branch_id):
    """AJAX branch deletion used by the admin Branch & Staff edit modal."""
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

    branch = get_object_or_404(Branch, pk=branch_id)

    staff_count = User.objects.filter(branch=branch).count()
    if staff_count:
        return JsonResponse({
            "success": False,
            "error": f"Cannot delete this branch — {staff_count} staff member(s) are still assigned to it. Reassign or remove them first.",
        }, status=400)

    branch_id_value = branch.id
    branch.delete()

    return JsonResponse({"success": True, "branch_id": branch_id_value})


@role_required("ADMIN")
def create_branch(request):
    branches = Branch.objects.all()

    if request.method == "POST":
        form = BranchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Branch created successfully.")
            return redirect("branches:create_branch")
        messages.error(request, "Please correct the errors below.")
    else:
        form = BranchForm()

    return render(request, "branches/create_branch.html", {"form": form, "branches": branches})


@role_required("ADMIN", "MANAGER")
def branch_staff(request, branch_id=None):
    branches = Branch.objects.all()
    selected_branch = None
    staff = User.objects.none()

    if branch_id:
        selected_branch = get_object_or_404(Branch, pk=branch_id)
        staff = User.objects.filter(branch=selected_branch).exclude(role=User.Role.STUDENT)

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        target_branch_id = request.POST.get("branch_id")
        user = get_object_or_404(User, pk=user_id)
        branch = get_object_or_404(Branch, pk=target_branch_id) if target_branch_id else None
        user.branch = branch
        user.save(update_fields=["branch"])
        messages.success(request, f"{user.email} assigned to {branch.name if branch else 'no branch'}.")
        return redirect("branches:branch_staff", branch_id=target_branch_id)

    unassigned_staff = User.objects.filter(branch__isnull=True).exclude(role=User.Role.STUDENT)

    return render(
        request,
        "branches/branch_staff.html",
        {
            "branches": branches,
            "selected_branch": selected_branch,
            "staff": staff,
            "unassigned_staff": unassigned_staff,
        },
    )
