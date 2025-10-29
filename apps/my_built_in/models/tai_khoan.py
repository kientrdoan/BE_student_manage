from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Superuser khác user bình thường, nếu bạn không dùng Django Admin
        thì chỉ cần tạo giống user thôi.
        """
        return self.create_user(email, password, **extra_fields)


class TaiKhoan(AbstractBaseUser):
    email = models.CharField(max_length=50, unique=True,)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    password = models.CharField(db_column="password_hash", max_length=156)
    phone = models.CharField(max_length=12, null=True, blank=True)
    address = models.CharField(max_length=156, null=True, blank=True)
    identity_number = models.CharField(max_length=12, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, null=True, blank=True)
    url = models.ImageField(upload_to='avatars/', null=True, blank=True)
    vector_embedding = models.CharField(max_length=156, null=True, blank=True)
    role = models.CharField(max_length=20, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = MyUserManager()

    class Meta:
        db_table = "tai_khoan"

    def __str__(self):
        return self.email
