import uuid
from typing import Optional, List

from sqlalchemy import UniqueConstraint
from sqlalchemy import create_engine
from sqlmodel import Field, SQLModel


class Correction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    file: str
    page: int
    page_nb: int
    corresponding: int
    good_page: int
    ocr: str
    corrected: str
    same: bool
    hash_: str
    user: Optional[int] = None
    page_: Optional[int] = None


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    UUID: uuid.UUID
    __table_args__ = (UniqueConstraint("UUID"),)


class Page(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: str
    page_number: int
    __table_args__ = (UniqueConstraint("document_id", "page_number"),)


def get_pages_done_by_user(uuid_: uuid.UUID) -> List[tuple[str, int]]:
    with engine.begin() as conn:

        user = conn.execute(User.__table__.select().where(User.UUID == uuid_)).first()
        if not user:
            raise ValueError("User not found")

        pages = conn.execute(Correction.__table__.select().where(Correction.user == user.id)).all()
        pages = [page.page_ for page in pages]
        pages = conn.execute(Page.__table__.select().where(Page.id.in_(pages))).all()

        return [(page.document_id, page.page_number) for page in pages]


def create_user():
    with engine.begin() as conn:
        while True:
            uuid_ = uuid.uuid4()
            user = conn.execute(User.__table__.select().where(User.UUID == uuid_)).first()
            if not user:
                conn.execute(User.__table__.insert(), {"UUID": uuid_})
                return uuid_


def get_user_by_uuid(uuid_: uuid.UUID | str) -> User:
    if isinstance(uuid_, str):
        uuid_ = uuid.UUID(uuid_)

    with engine.begin() as conn:
        return conn.execute(User.__table__.select().where(User.UUID == uuid_)).first()


def create_page(document_id: str, page_number: int):
    with engine.begin() as conn:
        conn.execute(
            Page.__table__.insert(),
            {"document_id": document_id, "page_number": page_number}
        )

        return conn.execute(
            Page.__table__.select().where(Page.document_id == document_id).where(Page.page_number == page_number)
        ).first().id


def get_page_by_id(page_id: int) -> Page:
    with engine.begin() as conn:
        return conn.execute(Page.__table__.select().where(Page.id == page_id)).first()


engine = create_engine("sqlite:///database.db")
with engine.begin() as conn:
    print(f"has_table: {engine.dialect.has_table(conn, 'Correction')}")
    if not engine.dialect.has_table(conn, "correction"):
        Correction.__table__.create(bind=engine)

    print(f"has_table: {engine.dialect.has_table(conn, 'User')}")
    if not engine.dialect.has_table(conn, "user"):
        User.__table__.create(bind=engine)

    print(f"has_table: {engine.dialect.has_table(conn, 'Page')}")
    if not engine.dialect.has_table(conn, "page"):
        Page.__table__.create(bind=engine)
