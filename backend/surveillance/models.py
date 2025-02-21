from django.db import models
from users.models import CustomUser

class Camera(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cameras')
    name = models.CharField(max_length=255)
    ip_url = models.URLField(max_length=500, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class DetectionLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='detection_logs')
    detected_at = models.DateTimeField(auto_now_add=True)
    object_type = models.CharField(max_length=100)
    confidence = models.FloatField()
    x_min = models.FloatField(null=True, blank=True)
    y_min = models.FloatField(null=True, blank=True)
    x_max = models.FloatField(null=True, blank=True)
    y_max = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.object_type} on {self.camera.name} at {self.detected_at}"

class Alert(models.Model):
    id = models.BigAutoField(primary_key=True)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='alerts')
    detection_log = models.ForeignKey(DetectionLog, on_delete=models.CASCADE, related_name='alerts')
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    message = models.CharField(max_length=255)

    def __str__(self):
        return f"Alert for {self.camera.name} - {self.message}"

