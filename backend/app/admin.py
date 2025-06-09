from fastapi_admin.app import app
from fastapi_admin.models import AbstractAdmin
from fastapi_admin.resources import Model
from fastapi_admin.widgets import displays, inputs

from app.models.user import User


@app.register
class Admin(AbstractAdmin):
    pass


@app.register
class UserAdmin(Model):
    resource = User
    fields = [
        "id",
        "telegram_id",
        "username",
        "first_name",
        "last_name",
        "is_active",
        "is_subscribed",
        "generated_videos_count",
        "created_at",
    ]
    
    displays = [
        displays.Id(),
        displays.Username(),
        displays.FirstName(),
        displays.LastName(),
        displays.IsActive(),
        displays.IsSubscribed(),
        displays.GeneratedVideosCount(),
        displays.CreatedAt(),
    ]

    inputs = [
        inputs.IsActive(),
        inputs.IsSubscribed(),
        inputs.GeneratedVideosCount(),
    ] 