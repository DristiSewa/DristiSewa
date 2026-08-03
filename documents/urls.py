from django.urls import path

from . import views

app_name = "documents"

urlpatterns = [
    path("upload/", views.upload_docs, name="upload_docs"),
    path("review/", views.document_review, name="document_review"),
    path("<int:pk>/preview/", views.document_preview, name="document_preview"),
    path("<int:pk>/download/", views.document_download, name="document_download"),
]
