from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from slapi.models import TextPair

engine = create_async_engine(
    "sqlite+aiosqlite:///db.sqlite3",
    echo=True,
)

async_session = async_sessionmaker(engine, expire_on_commit=True)


app = FastAPI()


class TextPairDto(BaseModel):
    id: int
    user_id: int
    text1: str
    text2: str
    is_learned_flg: bool


@app.get("/items")
async def read_items() -> List[TextPairDto]:
    res: List[TextPairDto] = []

    async with async_session() as session:
        dbres = await session.execute(select(TextPair))
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
async def read_item(id: int) -> TextPairDto:
    async with async_session() as session:
        dbres = await session.execute(select(TextPair).where(TextPair.id == id))
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
