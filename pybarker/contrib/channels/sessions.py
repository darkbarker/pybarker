from django.conf import settings


class FakeQueryCookieMiddleware:
    """
    переписанный чанеловский CookieMiddleware который не читает куки, а читает параметр токен из кверистринга
    и делает единственный фейковый куку чтобы дальше в цепочке AuthMiddlewareStack всё работало
    также кладёт разобранный токен в scope["__token"]
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        cookies = {}
        qs = scope["query_string"]  # b'token=foo'
        if qs:
            qs = qs.decode("ascii")  # token=foo
            if qs.startswith("token="):
                qs = qs[6:]  # foo
                cookies[settings.SESSION_COOKIE_NAME] = qs  # {'sessionid': 'foo'}
                scope["__token"] = qs
        return await self.inner(dict(scope, cookies=cookies), receive, send)
