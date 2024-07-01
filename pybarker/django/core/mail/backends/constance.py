from django.core.mail.backends.smtp import EmailBackend as _EmailBackend

from constance import config


# расширение backends.smtp.EmailBackend, которое берёт настройки из constance (сначала из settings)
# параметры в constance учитываемые одноимённые с штатными:
# EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS
class EmailBackend(_EmailBackend):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = config.EMAIL_HOST
        self.port = config.EMAIL_PORT
        self.username = config.EMAIL_HOST_USER
        self.password = config.EMAIL_HOST_PASSWORD
        self.use_tls = config.EMAIL_USE_TLS
