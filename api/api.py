import json
import logging
import os
import random
import re
import uuid
import xml.sax.saxutils as saxutils
from pathlib import Path
from typing import List, Annotated, Optional

import requests
from fastapi import FastAPI, Form, Cookie
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from .sql_driver import Correction, User, get_pages_done_by_user, create_user, create_page, engine, \
    get_the_thing
from .type_hint import GoodPage

el_numbre = re.compile(r"(\d+)[_-]")

ranges = {
    "0": (1,),
    "1": (2, 3, 4, 5),
    "2": (6, 7, 8),
    "VT": (9, 10),
}


def number_from_file(file: Path) -> int | str:
    stem = file.stem
    if "suppl" in stem:
        return "s" + el_numbre.search(stem).group(1)
    return int(el_numbre.search(stem).group(1))


main_dir = Path(__file__).parent

app = FastAPI()

host = os.getenv("MAZETTE_PATH", "")
prefix = os.getenv("MAZETTE_PREFIX", "")

maz_non_corr = Path(os.getenv("MAZETTE_NON_CORR", "MAZ_non_corr"))
maz_corr = Path(os.getenv("MAZETTE_CORR", "MAZ_corr"))
imgs = Path(os.getenv("MAZETTE_IMGS", "webp"))

hmb = Path(os.getenv("MAZETTE_HMB", "how_many_for_b.json"))

app.mount("/static", StaticFiles(directory=main_dir / "static"), name="static")
templates = Jinja2Templates(directory=main_dir / "templates")

files = maz_non_corr.glob("*/*.json")
files = {f for f in files if "to_do" not in f.as_posix() and "Doublons" not in f.as_posix()}
files = {number_from_file(f): f for f in files}

max_nb = max((k for k in files if isinstance(k, int)))
min_nb = min((k for k in files if isinstance(k, int)))

logger_level = os.getenv("MAZETTE_LOG_LEVEL", "WARNING")
logger = logging.getLogger("mazette")
logger.setLevel(logger_level)


def get_doc(nb: int | str) -> Optional[Path]:
    return files.get(nb)


def get_random_doc() -> Path:
    """Gets a random document, we cant recursively call in the get method because then get calls it
    before finishing the lookup which causes a recursion error """
    return files.get(random.randint(min_nb, max_nb), None) or get_random_doc()


def get_random_doc_and_page_not_in_set(pages: set[tuple[str, int]], tries: int = 0) -> Optional[tuple[Path, int]]:
    if tries > 10:
        return None

    file = get_random_doc()
    page = get_random_page(file)
    if (file.name, page) not in pages:
        return file, page
    return get_random_doc_and_page_not_in_set(pages, tries + 1)


def get_random_doc_and_page_in_set(pages: set[tuple[str, int]]) -> Optional[tuple[Path, int]]:
    if not pages:
        return None
    file_name, page = random.choice(list(pages))
    file, page = files.get(file_name, None), page or get_random_doc_and_page_in_set(pages)
    return file, page


def get_random_doc_and_page_for_user(uuid_: uuid.UUID) -> tuple[Path, int]:
    pages_1, pages_2, pages_3, pages_more = get_the_thing(uuid_)

    match random.randint(1, 10):
        case ranges.get("0"):
            result = get_random_doc_and_page_not_in_set(pages_1 | pages_2 | pages_3 | pages_more)
        case ranges.get("1"):
            result = get_random_doc_and_page_in_set(pages_1)
        case ranges.get("2"):
            result = get_random_doc_and_page_not_in_set(pages_2)
        case ranges.get("VT"):
            raise ValueError("VT not implemented")

    return result or get_random_doc_and_page_for_user(uuid_)


def open_file(file: Path) -> dict:
    with open(file, "r") as f:
        return json.load(f)


def get_page_nb(data: dict, page: int) -> int:
    return data["pages_number"][page]


def get_random_page(data: dict) -> int:
    return random.randint(0, len(data["texte"]) - 1)


def get_page_text(data: dict, page: int) -> List[str]:
    return [e for e in (saxutils.unescape(e).strip() for e in data["texte"][page]) if e]


def get_pages_nb(data: dict) -> List[int]:
    return data["pages_number"]


def get_first_page(data: dict) -> int:
    return min(data["pages_number"], key=int)  # Should be the first index of pages_number  but its safer this way


def get_last_page(data: dict) -> int:
    return max(data["pages_number"], key=int)  # Same as above


def get_img_path(file: Path, page_nb: int) -> Path | str | None:
    # return imgs / file.parent.name / file.stem / f"{page_nb}.webp"
    file = f"{file.parent.name}/{file.stem}/{page_nb}.webp"
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
    file = f"{file.parent.name}/{file.stem}/{page_nb}.webp"
    url = f"https://cdn.marceau-h.fr/mazette/{file}"
    try:
        r = requests.get(url)
        r.raise_for_status()
        return url
    except Exception as e:
        pass
    return None


async def read_random_for_user(uuid_: uuid.UUID):
    logger.info("random")

    file, page = get_random_doc_for_user(uuid_)
    data = open_file(file)

    if not data["texte"]:
        return await read_random_for_user(uuid_)

    # page = get_random_page(data)
    text = get_page_text(data, page)
    page_nb = get_page_nb(data, page)
    first_page = get_first_page(data)
    last_page = get_last_page(data)
    # img = get_img_path(file, page_nb)
    img = get_img_url(file, page_nb)

    if not img:
        return await read_random_for_user(uuid_)

    logger.info(
        f"file: {file}, page: {page}, page_nb: {page_nb}, text: {text}, img: {img}, "
    )
    text = "\n".join(text)
    return file, page, page_nb, first_page, last_page, text, img


async def read_page(file: int | str, page_nb: int):
    file = get_doc(file)
    if not file:
        logger.warning(f"file not found: {file}")
        return JSONResponse(status_code=404, content={"message": "File not found"})

    logger.info(f"file: {file}, page_nb: {page_nb}")

    data = open_file(file)
    page = get_page_text(data, page_nb)

    page_nb = get_page_nb(data, page_nb)
    first_page = get_first_page(data)
    last_page = get_last_page(data)

    img = get_img_url(file, page_nb)
    if not img:
        logger.warning(f"img not found: {img}")
        return JSONResponse(status_code=404, content={"message": "Image not found"})

    logger.info(
        f"file: {file}, page: {page}, page_nb: {page_nb}, text: {page}, img: {img}, first_page: {first_page}, last_page: {last_page}, pages_nb: {get_pages_nb(data)}"
    )
    page = "\n".join(page)
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
            "page": page_nb,
            "page_nb": page_nb,
            "ocr": page,
            "first_page": first_page,
            "last_page": last_page,
        }
    )


@app.get("/favicon.ico", response_class=FileResponse, tags=["main"])
async def favicon():
    return FileResponse(main_dir / "static" / "favicon.ico")


@app.get("/", response_class=HTMLResponse, tags=["main"])
async def read_root(mazette: str = Cookie(None)):
    mazette = uuid.UUID(mazette)

    while True:
        file, page, page_nb, first_page, last_page, text, img = await read_random_for_user(mazette)
        if (file.__str__(), page_nb) not in get_pages_done_by_user(mazette):
            break

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


@app.get("/{file}/{page_nb}", response_class=HTMLResponse, tags=["main"])
async def read_page_n(file: int, page_nb: int):
    return read_page(file, page_nb)


@app.get("/s/{file}/{page_nb}", response_class=HTMLResponse, tags=["main"])
def read_page_s(file: int, page_nb: int):
    return read_page(f"s{file}", page_nb)


@app.get("/imgs/{path:path}", response_class=FileResponse, tags=["main"])
async def read_img(path: str):
    img = imgs / path
    url = f"https://cdn.marceau-h.fr/mazette/{path}"

    if img.exists():
        return FileResponse(img)

    try:
        # r = requests.get(url, stream=True)
        # r.raise_for_status()
        # return StreamingResponse(r.raw, media_type="image/webp")
        r = requests.get(url)
        r.raise_for_status()
        return RedirectResponse(url)

    except Exception as e:
        logger.error(e)
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
    logger.info(f"submit: {file=}, {page=}, {page_nb=}, {corresponding=}, {good_page=}, {ocr=}, {corrected=}")

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

        logger.info(json_res)

        conn.execute(
            Correction.__table__.insert(),
            json_res
        )

    return JSONResponse(status_code=200, content=json_res)


@app.get("/set_cookie", response_class=JSONResponse, tags=["main"])
def create_cookie():
    logger.info("cookie")
    response = JSONResponse(content={"message": "Come to the dark side, we have cookies"})
    response.set_cookie(
        key="mazette",
        value=create_user().hex,
        secure=False,
    )
    logger.info(response.body)
    logger.info(response.raw_headers)
    return response


@app.get("/read_cookie", response_class=JSONResponse, tags=["main"])
async def read_cookie(mazette: str = Cookie(None)):
    return JSONResponse(content={"mazette": mazette})
