from datetime import datetime
from typing import List
from fastapi import Request
from sqlalchemy import ForeignKey, String, Boolean, false, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship,  mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "slid_user"

    # "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT
    # "password" varchar(128) NOT NULL
    # "last_login" datetime NULL
    # "is_superuser" bool NOT NULL
    # "username" varchar(150) NOT NULL UNIQUE
    # "first_name" varchar(150) NOT NULL
    # "last_name" varchar(150) NOT NULL
    # "email" varchar(254) NOT NULL
    # "is_staff" bool NOT NULL
    # "is_active" bool NOT NULL
    # "date_joined" datetime NOT NULL

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
    # "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT
    # "text1" text NOT NULL
    # "text2" text NOT NULL
    # "is_learned_flg" bool NOT NULL
    # "learned_ts" datetime NULL
    # "created_ts" datetime NOT NULL
    # "modified_ts" datetime NOT NULL
    # "user_id" bigint NOT NULL REFERENCES "slid_user" ("id") DEFERRABLE INITIALLY DEFERRED
    # "comment" text NOT NULL

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("slid_user.id"))
    user: Mapped["User"] = relationship(back_populates="text_pairs")
    text1: Mapped[str] = mapped_column(String())
    text2: Mapped[str] = mapped_column(String())
    is_learned_flg: Mapped[bool] = mapped_column(
        Boolean(), default=False, server_default=false())

    # async def __admin_repr__(self, request: Request):
    #     return f'{self.text1} / {self.text2}'

class StudyState(Base):
    __tablename__ = "slfrase_studystate"
    # "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT
    # "is_passed_flg" bool NOT NULL
    # "passed_ts" datetime NULL
    # "created_ts" datetime NOT NULL
    # "modified_ts" datetime NOT NULL
    # "text_pair_id" bigint NOT NULL REFERENCES "slfrase_textpair" ("id") DEFERRABLE INITIALLY DEFERRED
    # "is_skipped_flg" bool NOT NULL
    # "answer" text NOT NULL
    # "possible_answers" text NOT NULL
    # "question" text NOT NULL

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
