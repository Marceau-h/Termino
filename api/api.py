import json
import os
import random
import uuid
import xml.sax.saxutils as saxutils
from pathlib import Path
from typing import List, Annotated, Optional

import requests
from fastapi import FastAPI, Form, Response, Request, Cookie
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from starlette.templating import Jinja2Templates

from .sql_driver import Correction, User, Page
from .type_hint import GoodPage

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



main_dir = Path(__file__).parent

app = FastAPI()

host = os.getenv("MAZETTE_PATH", "")
prefix = os.getenv("MAZETTE_PREFIX", "")

maz_non_corr = Path(os.getenv("MAZETTE_NON_CORR", "MAZ_non_corr"))
maz_corr = Path(os.getenv("MAZETTE_CORR", "MAZ_corr"))
imgs = Path(os.getenv("MAZETTE_IMGS", "imgs"))

hmb = Path(os.getenv("MAZETTE_HMB", "how_many_for_b.json"))

app.mount("/static", StaticFiles(directory=main_dir / "static"), name="static")
templates = Jinja2Templates(directory=main_dir / "templates")

files = list(maz_corr.glob("*/*.json"))  # TODO: change to maz_non_corr when pages_nb will be added
files = [f for f in files if "to_do" not in f.as_posix()]
files = [f for f in files if "Doublons" not in f.as_posix()]

random.shuffle(files)
i = 0


def get_random_doc() -> Path:
    """Getting a random document from a shuffled list of documents,
    this prevents to have the same document twice in a row"""
    global i
    file = files[i]
    if i == len(files) - 1:
        i = 0
        random.shuffle(files)
    else:
        i += 1

    return file


def open_file(file: Path) -> dict:
    with open(file, "r") as f:
        data = json.load(f)

    return data


def get_random_page(data: dict) -> int:
    page = random.randint(0, len(data["texte"]) - 1)
    return page


def get_page(data: dict, page: int) -> List[str]:
    return [saxutils.unescape(e) for e in data["texte"][page]]


def get_page_nb(data: dict, page: int) -> int:
    return data["pages_number"][page]


def get_pages_nb(data: dict) -> List[int]:
    return data["pages_number"]


def get_first_page(data: dict) -> int:
    return min(data["pages_number"])  # Should be the first index of pages_number  but its safer this way


def get_last_page(data: dict) -> int:
    return max(data["pages_number"])  # Same as above


def get_img_path(file: Path, page_nb: int) -> Path | str | None:
    # return imgs / file.parent.name / file.stem / f"{page_nb}.png"
    file = f"{file.parent.name}/{file.stem}/{page_nb}.png"
    if (imgs / file).exists():
        return imgs / file
    else:
        url = f"https://cdn.marceau-h.fr/mazette/{file}"

        try:
            r = requests.get(url)
            r.raise_for_status()
            return imgs / file
        except Exception as e:
            pass

    return None


def get_img_url(file: Path, page_nb: int) -> Optional[str]:
    file = f"{file.parent.name}/{file.stem}/{page_nb}.png"
    url = f"https://cdn.marceau-h.fr/mazette/{file}"
    try:
        r = requests.get(url)
        r.raise_for_status()
        return url
    except Exception as e:
        pass
    return None


async def read_random():
    print("random")

    file = get_random_doc()
    data = open_file(file)

    if not data["texte"]:
        return await read_random()

    page = get_random_page(data)
    text = get_page(data, page)
    page_nb = get_page_nb(data, page)
    first_page = get_first_page(data)
    last_page = get_last_page(data)
    # img = get_img_path(file, page_nb)
    img = get_img_url(file, page_nb)

    if not img:
        return await read_random()

    print(
        f"file: {file}, page: {page}, page_nb: {page_nb}, text: {text}, img: {img}, "
        # f"img.exists: {img.exists()}, img.is_file: {img.is_file()}"
    )
    text = "\n".join(text)
    return file, page, page_nb, first_page, last_page, text, img


@app.get("/", response_class=HTMLResponse, tags=["main"])
async def read_root():
    file, page, page_nb, first_page, last_page, text, img = await read_random()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": {},
            "host": host,
            "prefix": prefix,
            # "pic": img.as_posix(),
            "pic": img,
            "file": file,
            "file_name": file.name,
            "page": page,
            "page_nb": page_nb,
            "ocr": text,
            "first_page": first_page,
            "last_page": last_page,
        }
    )


@app.get("/imgs/{path:path}", response_class=FileResponse, tags=["main"])
async def read_img(path: str):
    img = imgs / path
    url = f"https://cdn.marceau-h.fr/mazette/{path}"

    if img.exists():
        return FileResponse(img)

    try:
        # r = requests.get(url, stream=True)
        # r.raise_for_status()
        # return StreamingResponse(r.raw, media_type="image/png")
        r = requests.get(url)
        r.raise_for_status()
        return RedirectResponse(url)

    except Exception as e:
        print(e)
        return JSONResponse(status_code=404, content={"message": "Image not found"})


@app.post("/submit", response_class=RedirectResponse, tags=["main"])
async def submit(
        file: Annotated[str, Form()],
        page: Annotated[int, Form()],
        page_nb: Annotated[int, Form()],
        corresponding: Annotated[int, Form()],
        good_page: Annotated[GoodPage, Form()],
        ocr: Annotated[str, Form()],
        corrected: Annotated[str, Form()],
        mazette: str = Cookie(None),
):
    print(f"submit: {file=}, {page=}, {page_nb=}, {corresponding=}, {good_page=}, {ocr=}, {corrected=}")

    json_res = {
        "file": file,
        "page": page,
        "page_nb": page_nb,
        "corresponding": corresponding,
        "good_page": good_page,
        "ocr": ocr,
        "corrected": corrected,
        "same": corrected == ocr,
        "hash_": hash((file, page, page_nb, corresponding, good_page, ocr, corrected))
    }

    with engine.begin() as conn:
        # Is the user already in the database
        user = conn.execute(User.__table__.select().where(User.UUID == mazette)).first()
        if not user:
            raise ValueError("User not found")

        json_res["user"] = user.id

        json_res["page_"] = create_page(file.__str__(), page_nb)


        conn.execute(
            Correction.__table__.insert(),
            json_res
        )

    return JSONResponse(status_code=200, content=json_res)

@app.get("/set_cookie", response_class=JSONResponse, tags=["main"])
def create_cookie():
    print("cookie")
    response = JSONResponse(content={"message": "Come to the dark side, we have cookies"})
    response.set_cookie(
        key="mazette",
        value=create_user().hex,
        secure=False,
    )
    print(response.body)
    print(response.raw_headers)
    return response

@app.get("/read_cookie", response_class=JSONResponse, tags=["main"])
async def read_cookie(mazette: str = Cookie(None)):
    return JSONResponse(content={"mazette": mazette})


def create_user():
    with engine.begin() as conn:
        while True:
            uuid_ = uuid.uuid4()
            user = conn.execute(User.__table__.select().where(User.UUID == uuid_)).first()
            if not user:
                conn.execute(User.__table__.insert(), {"UUID": uuid_})
                return uuid_

def create_page(document_id: str, page_number: int):
    with engine.begin() as conn:
        conn.execute(
            Page.__table__.insert(),
            {"document_id": document_id, "page_number": page_number}
        )

        return conn.execute(
            Page.__table__.select().where(Page.document_id == document_id).where(Page.page_number == page_number)
        ).first().id

