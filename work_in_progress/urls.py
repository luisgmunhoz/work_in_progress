from django.urls import path
from django.contrib import admin
from ninja import NinjaAPI, Schema

api = NinjaAPI()


class HelloSchema(Schema):
    name: str = "world"


@api.post("/hello")
def hello(request, data: HelloSchema):
    return f"Hello {data.name}"


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
