import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from slapi.models import User, TextPair


l = logging.getLogger("admin")

class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username", None) 
        password = form.get("password", None)
        l.info("try auth: %s", username)
        request.session.update({"token": "1"})
        return True

    async def logout(self, request: Request) -> bool:
        l.info("logout")
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Optional[Response]:
        token = request.session.get("token", None)
        l.info("check token: %s", token)
        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
        return None


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username]
    column_details_exclude_list = [User.text_pairs]
    form_excluded_columns = [User.text_pairs]


class TextPairAdmin(ModelView, model=TextPair):
    column_list = [TextPair.id, TextPair.user, TextPair.text1, TextPair.text2]
    column_searchable_list = [TextPair.text1, TextPair.text2]
    column_formatters = {TextPair.user: lambda m, a: m.user.username}
    column_details_exclude_list = [TextPair.study_states]
    column_formatters_detail = column_formatters
    form_excluded_columns = [TextPair.study_states]
    form_ajax_refs = {
        "user": {
            "fields": ("username", ),
            "order_by": "username",
        }
    }


def setup(app: Starlette, engine: AsyncEngine) -> Admin:
    auth_backend = AdminAuth(secret_key="SuperSecret :)")
    admin = Admin(app, engine, authentication_backend=auth_backend)
    admin.add_view(UserAdmin)
    admin.add_view(TextPairAdmin)
    return admin
