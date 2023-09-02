from datetime import datetime, timezone
import logging
from math import ceil
from typing import Annotated, AsyncIterator, Generic, List, TypeVar
from fastapi import Query, status, Depends, FastAPI, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from django.contrib.auth.hashers import PBKDF2PasswordHasher
from slapi.models import TextPair, User
from slapi.db import engine, async_session


app = FastAPI()
basic_security = HTTPBasic()

# try:
#     from slapi.admin_starlette_admin import admin
#     admin.mount_to(app)
# except ImportError:
#     logging.getLogger().fatal('admin not installed', exc_info=True)

try:
    from slapi.admin_sqladmin import mount
    mount(app, engine)
except ImportError:
    logging.getLogger().fatal('admin not installed', exc_info=True)


async def get_read_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session


async def get_write_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session
        await session.commit()


async def get_current_user(credentials: Annotated[HTTPBasicCredentials, Depends(basic_security)]) -> User:
    async with async_session(expire_on_commit=False) as session:
        dbres = await session.execute(select(User).where(
            User.username == credentials.username
        ))
        user = dbres.scalar_one_or_none()
        if user != None:
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    # headers={"WWW-Authenticate": "Basic"},
                )

            hasher = PBKDF2PasswordHasher()
            if not hasher.verify(credentials.password, user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    # headers={"WWW-Authenticate": "Basic"},
                )

            user.last_login = datetime.now(timezone.utc)
            await session.commit()
            session.expunge(user)

            return user

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            # headers={"WWW-Authenticate": "Basic"},
        )


M = TypeVar('M')


class PaginatedResponse(BaseModel, Generic[M]):
    count: int = Field(description='Number of items')
    page: int = Field(description='Requested page number')
    page_size: int = Field(description='Requested page size')
    page_count: int = Field(description='Total pages for requested page size')
    items: List[M] = Field(description='List of items')


class TextPairDto(BaseModel):
    id: int
    user_id: int
    text1: list[str]
    text2: list[str]
    is_learned_flg: bool


def split_text_pair(t: str) -> list[str]:
    res = [x.strip() for x in t.splitlines()]
    return [x for x in res if res]


@app.get("/pairs", response_model=PaginatedResponse[TextPairDto])
async def get_pairs(user: User = Depends(get_current_user),
                    page: int = Query(1, ge=1),
                    page_size: int = Query(10, gte=10, le=100)):
    res: List[TextPairDto] = []
    async with async_session() as session:
        query = select(TextPair).where(
            TextPair.user_id == user.id
        )

        count_res = await session.execute(select(func.count()).select_from(query.subquery()))
        count = count_res.scalar_one()

        offset = (page - 1) * page_size
        limit = page_size * page
        if offset < count:
            dbres = await session.execute(query.offset(offset).limit(limit))
            for d in dbres.scalars():
                res.append(TextPairDto(
                    id=d.id,
                    user_id=d.user_id,
                    text1=split_text_pair(d.text1),
                    text2=split_text_pair(d.text2),
                    is_learned_flg=d.is_learned_flg,
                ))
    return PaginatedResponse[TextPairDto](
        count=count,
        page=page,
        page_size=page_size,
        page_count=ceil(max(1, count - 0) / page_size),
        items=res,
    )


@app.get("/pairs/{id}")
async def get_pair(
    id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_read_session)],
) -> TextPairDto:
    # async with async_session() as session:
    dbres = await session.execute(
        select(TextPair).where(
            TextPair.user_id == user.id,
            TextPair.id == id
        )
    )
    d = dbres.scalar_one_or_none()
    if d != None:
        return TextPairDto(
            id=d.id,
            user_id=d.user_id,
            text1=split_text_pair(d.text1),
            text2=split_text_pair(d.text2),
            is_learned_flg=d.is_learned_flg,
        )
    raise HTTPException(status_code=404, detail="TextPair not found")
