from django.contrib.auth import SESSION_KEY
from django.contrib.sessions.models import Session
from django.utils import timezone


# возвращает все активные сессии указанного юзера в виде списка (session_key, декодированная session_data)
def get_all_usersessions(user_id):
    usersessions = []
    for session in Session.objects.filter(expire_date__gte=timezone.now()):
        decoded_session_data = session.get_decoded()
        if decoded_session_data.get(SESSION_KEY, None) == str(user_id):
            usersessions.append((session.session_key, decoded_session_data))
    return usersessions
