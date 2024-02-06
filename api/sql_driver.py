from typing import Optional

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

