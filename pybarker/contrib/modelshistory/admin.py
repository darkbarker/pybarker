from django.contrib import admin

from .models import HistoryModelEntry
from .utils import smart_value
from pybarker.django.contrib.admin.filters import SimpleTextFilter


class HistoryModelEntryAdmin(admin.ModelAdmin):
    list_display = ("f_action_time", "content_type", "object_repr", "action_flag_title", "f_field", "root_object_id")
    list_display_links = ("f_action_time", "content_type", "object_repr")
    list_filter = (("content_type", admin.RelatedOnlyFieldListFilter), "action_flag", ("field", SimpleTextFilter), ("root_object_id", SimpleTextFilter))

    def f_action_time(self, obj):
        return smart_value(obj.action_time)
    f_action_time.short_description = "action time"

    def f_field(self, obj):
        if obj.field is None:
            return None
        return f"{obj.field_title()} ({obj.field})"
    f_field.short_description = "field"


admin.site.register(HistoryModelEntry, HistoryModelEntryAdmin)
