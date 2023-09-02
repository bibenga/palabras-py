from sqlalchemy import select, update
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.actions import action
from starlette_admin.contrib.sqla.admin import Admin
from starlette_admin.contrib.sqla.view import ModelView
from starlette_admin.auth import AdminUser, AuthProvider
from starlette_admin.exceptions import LoginFailed
from slapi.models import StudyState, TextPair, User
from slapi.db import engine, async_session


class UsernameAndPasswordProvider(AuthProvider):
    """
    This is only for demo purpose, it's not a better
    way to save and validate user credentials
    """

    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        async with async_session(expire_on_commit=False) as session:
            dbres = await session.execute(select(User).where(
                User.username == username
            ))
            user = dbres.scalar_one_or_none()
            if user == None:
                raise LoginFailed("Invalid username or password")

            request.session.update({"user_id": user.id})
            return response

    async def is_authenticated(self, request) -> bool:
        user_id = request.session.get("user_id", None)
        if user_id:
            async with async_session(expire_on_commit=False) as session:
                dbres = await session.execute(select(User).where(
                    User.id == user_id
                ))
                user = dbres.scalar_one_or_none()
                if user != None and user.is_active and (user.is_superuser or user.is_staff):
                    request.state.user = user
                    return True

        return False

    def get_admin_user(self, request: Request) -> AdminUser:
        user = request.state.user
        return AdminUser(username=user.username, photo_url=None)

    async def logout(self, request: Request, response: Response) -> Response:
        request.session.clear()
        return response


# Create admin
admin = Admin(engine, title="Palabras admin",
              auth_provider=UsernameAndPasswordProvider(),
              middlewares=[Middleware(
                  SessionMiddleware,
                  secret_key="SuperSecret :)",
                  session_cookie="starlette_session")
              ],
              debug=True)


class UserModelView(ModelView):
    fields = [User.id, User.username, User.password,
              User.is_active, User.is_superuser, User.is_staff]
    exclude_fields_from_detail = [User.password]
    exclude_fields_from_list = [User.password]
    exclude_fields_from_edit = [User.password]


admin.add_view(UserModelView(User))


class TextPairModelView(ModelView):
    fields = ["id", "user", "text1", "text2", "is_learned_flg"]

    @action(
        name="mark_learned",
        text="Mark as learned",
        confirmation="Are you sure you want to mark selected pairs as learned?",
        submit_btn_text="Yes",
        submit_btn_class="btn-success",
    )
    async def mark_learned(self, request: Request, pks: list) -> str:
        async with async_session() as session:
            await session.execute(
                update(TextPair),
                [
                    {'id': int(pk), 'is_learned_flg': True}
                    for pk in pks
                ]
            )
            await session.commit()
        return "{} pairs were successfully marked as learned".format(len(pks))

    @action(
        name="mark_unknown",
        text="Mark as unknown",
        confirmation="Are you sure you want to mark selected pairs as unknown?",
        submit_btn_text="Yes",
        submit_btn_class="btn-success",
    )
    async def mark_unknown(self, request: Request, pks: list) -> str:
        async with async_session() as session:
            await session.execute(
                update(TextPair).where(
                    TextPair.id.in_(pks)
                ).values(
                    is_learned_flg=False
                )
            )
            await session.commit()
        return "{} pairs were successfully marked as unknown".format(len(pks))


admin.add_view(TextPairModelView(TextPair))


class StudyStateModelView(ModelView):
    # exclude_fields_from_list = [User.password]
    exclude_fields_from_create = [StudyState.created_ts, StudyState.modified_ts]
    exclude_fields_from_edit = [StudyState.created_ts, StudyState.modified_ts]


admin.add_view(StudyStateModelView(StudyState))
