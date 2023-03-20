from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


# снято на django 4.1.7
class EmailedUserManager(UserManager):

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


# снято на django 4.1.7
class AbstractEmailedUser(AbstractUser):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions and email instead username.
    (instead django's AbstractUser)
    """

    email = models.EmailField(_("email address"), blank=False, null=False, unique=True)
    username = None

    objects = EmailedUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta(AbstractUser.Meta):
        abstract = True
