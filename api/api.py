import os
import requests
from io import StringIO
from typing import List
from pathlib import Path
import random
import json
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, UploadFile, Form, File
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from starlette.templating import Jinja2Templates

from .type_hint import GoodPage
from .sql_driver import Correction

engine = create_engine("sqlite:///database.db")
with engine.begin() as conn:
    if not engine.dialect.has_table(conn, "correction"):
        Correction.__table__.create(bind=engine)


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


def get_random_doc() -> Path:
    files = list(maz_corr.glob("*/*.json"))  # TODO: change to maz_non_corr when pages_nb will be added
    files = [f for f in files if "to_do" not in f.as_posix()]
    files = [f for f in files if "Doublons" not in f.as_posix()]

    file = random.choice(files)

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


def get_img_path(file: Path, page_nb: int) -> Path:
    return imgs / file.parent.name / file.stem / f"{page_nb}.png"


async def read_random():
    print("random")

    file = get_random_doc()
    data = open_file(file)

    if not data["texte"]:
        return await read_random()

    page = get_random_page(data)
    text = get_page(data, page)
    page_nb = get_page_nb(data, page)
    img = get_img_path(file, page_nb)

    if not img or not img.exists():
        return await read_random()

    print(
        f"file: {file}, page: {page}, page_nb: {page_nb}, text: {text}, img: {img}, img.exists: {img.exists()}, img.is_file: {img.is_file()}"
    )
    text = "\n".join(text)
    return file, page, page_nb, text, img


@app.get("/", response_class=HTMLResponse, tags=["main"])
async def read_root():
    file, page, page_nb, text, img = await read_random()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": {},
            "host": host,
            "prefix": prefix,
            "pic": img.as_posix(),
            "file": file,
            "file_name": file.name,
            "page": page,
            "page_nb": page_nb,
            "ocr": text,
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

