import uuid
from typing import Optional, List

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

class Page(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    document_id: str
    page_number: int

