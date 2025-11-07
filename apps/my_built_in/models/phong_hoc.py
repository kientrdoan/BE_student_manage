from django.db import models

class PhongHoc(models.Model):
    room_code= models.CharField(max_length=50, null=True)
    building = models.CharField(max_length=100)
    max_capacity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        db_table = "phong_hoc"

    def __str__(self):
        return self.room_code