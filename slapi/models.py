from datetime import datetime
from typing import List
from fastapi import Request
from sqlalchemy import ForeignKey, String, Boolean, false, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship,  mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "slid_user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(150),  unique=True)
    password: Mapped[str] = mapped_column(String(128))
    is_active: Mapped[bool]
    is_staff: Mapped[bool]
    is_superuser: Mapped[bool]
    last_login: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    text_pairs: Mapped[List["TextPair"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    # async def __admin_repr__(self, request: Request):
    #     return self.username


class TextPair(Base):
    __tablename__ = "slfrase_textpair"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("slid_user.id"))
    user: Mapped["User"] = relationship(back_populates="text_pairs")
    text1: Mapped[str]
    text2: Mapped[str]
    comment: Mapped[str]
    is_learned_flg: Mapped[bool] = mapped_column(
        Boolean(), default=False, server_default=false())
    learned_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    modified_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    study_states: Mapped[List["StudyState"]] = relationship(
        back_populates="text_pair", cascade="all, delete-orphan"
    )

    # async def __admin_repr__(self, request: Request):
    #     return f'{self.text1} / {self.text2}'


class StudyState(Base):
    __tablename__ = "slfrase_studystate"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text_pair_id: Mapped[int] = mapped_column(ForeignKey("slfrase_textpair.id"))
    text_pair: Mapped["TextPair"] = relationship(back_populates="study_states")
    question: Mapped[str]
    possible_answers: Mapped[str]
    answer: Mapped[str]
    is_passed_flg: Mapped[bool] = mapped_column(Boolean(), default=False)
    is_skipped_flg: Mapped[bool] = mapped_column(Boolean(), default=False)
    passed_ts: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    modified_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
