
def get_client_ip(request):
    # X-Forwarded-For: <client>, <proxy1>, <proxy2>
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


# замена временная для request.is_ajax(), реализация из django 3.2
def request_is_ajax(request):
    return request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest"
