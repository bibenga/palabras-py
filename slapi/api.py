from datetime import datetime, timezone
from typing import Annotated, List
from fastapi import status, Depends, FastAPI, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from django.contrib.auth.hashers import PBKDF2PasswordHasher

from slapi.models import TextPair, User

engine = create_async_engine(
    "sqlite+aiosqlite:///db.sqlite3",
    echo=True,
)

async_session = async_sessionmaker(engine, expire_on_commit=True)


app = FastAPI()
basic_security = HTTPBasic()


def auth_failed():
    raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            # headers={"WWW-Authenticate": "Basic"},
        )

async def get_current_user(credentials: Annotated[HTTPBasicCredentials, Depends(basic_security)]) -> User | None:
    async with async_session(expire_on_commit=False) as session:
        dbres = await session.execute(select(User).where(
            User.username == credentials.username
        ))
        user = dbres.scalar_one_or_none()
        if user != None:
            if not user.is_active:
                auth_failed()
            
            hasher = PBKDF2PasswordHasher()
            if not hasher.verify(credentials.password, user.password):
                auth_failed()

            user.last_login = datetime.now(timezone.utc)
            await session.commit()

            return user
        
        auth_failed()


class TextPairDto(BaseModel):
    id: int
    user_id: int
    text1: str
    text2: str
    is_learned_flg: bool


@app.get("/items")
async def read_items(user: Annotated[User, Depends(get_current_user)]) -> List[TextPairDto]:
    res: List[TextPairDto] = []

    print('read_items: user', user.id)

    async with async_session() as session:
        dbres = await session.execute(select(TextPair).where(
            TextPair.user_id == user.id
        ))
        for d in dbres.scalars():
            res.append(TextPairDto(
                id=d.id,
                user_id=d.user_id,
                text1=d.text1,
                text2=d.text2,
                is_learned_flg=d.is_learned_flg,
            ))

    return res


@app.get("/items/{id}")
async def read_item(user: Annotated[User, Depends(get_current_user)], id: int) -> TextPairDto:
    async with async_session() as session:
        dbres = await session.execute(select(TextPair).where(
            TextPair.user_id == user.id,
            TextPair.id == id
        ))
        d = dbres.scalar_one_or_none()
        if d != None:
            return TextPairDto(
                id=d.id,
                user_id=d.user_id,
                text1=d.text1,
                text2=d.text2,
                is_learned_flg=d.is_learned_flg,
            )
    raise HTTPException(status_code=404, detail="TextPair not found")
