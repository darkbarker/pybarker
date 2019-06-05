from django.core.mail.backends.smtp import EmailBackend as _EmailBackend

from constance import config


# расширение EmailBackend, которое берёт настройки из constance
class EmailBackend(_EmailBackend):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = config.EMAIL_HOST
        self.port = config.EMAIL_PORT
        self.username = config.EMAIL_HOST_USER
        self.password = config.EMAIL_HOST_PASSWORD
        self.use_tls = config.EMAIL_USE_TLS
