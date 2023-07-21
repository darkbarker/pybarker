from django.urls import path

from . import views

app_name = "modelshistory"

urlpatterns = [
    # url(r"^model_autocomplete/(?P<model_name>[^/]+)/$", views.ModelAutocomplete.as_view(), name="model-autocomplete", ),
    path("field_history/<model_pk_field>/", views.ModelFieldHistory.as_view(), name="model-field-history", ),
]
