from django.contrib import admin
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _


# фильтр для админки для ввода значения в текстовое поле, а не выбора из списка длинного XXX
class SimpleTextFilter(admin.AllValuesFieldListFilter):
    template = "admin/simpletext_list_filter.html"

    def choices(self, changelist):
        data = {}
        data["all"] = {
            "selected": self.lookup_val is None and self.lookup_val_isnull is None,
            "query_string": changelist.get_query_string({}, [self.lookup_kwarg, self.lookup_kwarg_isnull]),
            "display": _("All"),
        }

        found_current_val = False
        include_none = False
        for val in self.lookup_choices:
            if val is None:
                include_none = True
                continue
            val = force_str(val)
            if self.lookup_val == val:
                found_current_val = True

        # "form_url": changelist.get_query_string({}, [self.lookup_kwarg, self.lookup_kwarg_isnull]),
        # не канает, т.к. в action в form мы вставить не можем, разобьём на ряд скрытых инпутов
        # код на основе changelist.get_query_string, urlencode делать не надо, т.к. попадает в формы в виде валуе (а не урла), браузер разберётся
        p = changelist.params.copy()
        for r in [self.lookup_kwarg, self.lookup_kwarg_isnull]:
            for k in list(p):
                if k.startswith(r):
                    del p[k]

        data["current"] = {
            "hidden_inputs": p,
            "param_name": self.lookup_kwarg,
            "value": self.lookup_val,
            "notfound": self.lookup_val is not None and not found_current_val,
        }

        if include_none:
            data["empty"] = {
                "selected": bool(self.lookup_val_isnull),
                "query_string": changelist.get_query_string({
                    self.lookup_kwarg_isnull: "True",
                }, [self.lookup_kwarg]),
                "display": self.empty_value_display,
            }

        return [data]  # потому что до шаблона делается list выводу и мэп портится
