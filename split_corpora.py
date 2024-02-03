import json
from pathlib import Path

import pandas as pd
import plotly.express as px


def how_many_pages(lst1, lst2):
    if not lst1 or not lst2:
        raise ValueError("Empty list")

    how_many = 0

    if len(lst1) < len(lst2):
        lst1, lst2 = lst2, lst1

    for p in lst1:
        if p not in lst2:
            how_many += 1

    return how_many


corr = Path("MAZ_corr")
non_corr = Path("MAZ_non_corr")

corr_n_non_corr = []

for file_c in corr.glob("*/*"):

    file_nc = non_corr / file_c.relative_to(corr)

    if not file_nc.exists():
        type_ = "C"
    else:
        with open(file_c) as f:
            c = json.load(f)
        with open(file_nc) as f:
            nc = json.load(f)

        txt_nc = nc["texte"]
        txt_c = c["texte"]

        if txt_nc == txt_c:
            type_ = "A"
        else:
            type_ = "B"

    corr_n_non_corr.append((file_c, type_))

files_by_type = {
    "A": [],
    "B": [],
    "C": []
}

for file, type_ in corr_n_non_corr:
    files_by_type[type_].append(file)

how_many_for_b = []
toremove = []

for file_c in files_by_type["B"]:
    file_nc = non_corr / file_c.relative_to(corr)

    with open(file_c) as f:
        c = json.load(f)
    with open(file_nc) as f:
        nc = json.load(f)

    txt_nc = nc["texte"]
    txt_c = c["texte"]

    try:
        hmp = how_many_pages(txt_nc, txt_c)
    except ValueError:
        toremove.append(file_c)
        files_by_type["C"].append(file_c)
        continue

    how_many_for_b.append(
        {
            "file": file_c.as_posix(),
            "how_many": hmp,
            "len_c": len(txt_c),
            "len_nc": len(txt_nc),
            "same_len": len(txt_c) == len(txt_nc),
            "ratio": hmp / max(len(txt_c), len(txt_nc))
        }
    )

for e in toremove:
    files_by_type["B"].remove(e)

with open("files_by_type.json", "w") as f:
    json.dump(
        {k: [e.as_posix() for e in v] for k, v in files_by_type.items()},
        f,
        indent=4,
        ensure_ascii=False
    )

with open("how_many_for_b.json", "w") as f:
    json.dump(
        how_many_for_b,
        f,
        indent=4,
        ensure_ascii=False
    )

df = pd.DataFrame(how_many_for_b)

df["ratio"] = df["ratio"].round(2)

ratio = df["ratio"].value_counts()
ratio = ratio.sort_index()

fig = px.histogram(
    ratio,
    x=ratio.index,
    y=ratio.values,
    labels={"x": "ratio", "y": "nombre de fichiers"},
    title="Répartition des fichiers selon le ratio de pages modifiées",
    nbins=10,
    histfunc="sum",
    text_auto=True

)

hm = df["how_many"].value_counts()
hm = hm.sort_index()

fig2 = px.histogram(
    hm,
    x=hm.index,
    y=hm.values,
    labels={"x": "nombre de pages modifiées", "y": "nombre de fichiers"},
    title="Répartition des fichiers selon le nombre de pages modifiées",
    histfunc="sum",
    text_auto=True,
    log_y=True,

)

df["hm10"] = df["how_many"].apply(lambda x: x if x < 10 else 10)

hm10 = df["hm10"].value_counts()
hm10 = hm10.sort_index()

fig3 = px.histogram(
    hm10,
    x=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10+"],
    y=hm10.values,
    labels={"x": "nombre de pages modifiées", "y": "nombre de fichiers"},
    title="Répartition des fichiers selon le nombre de pages modifiées",
    nbins=10,
    histfunc="sum",
    text_auto=True,

)

df["hm5"] = df["how_many"].apply(lambda x: x if x < 5 else 5)
hm5 = df["hm5"].value_counts()
hm5 = hm5.sort_index()

fig4 = px.histogram(
    hm5,
    x=["1", "2", "3", "4", "5+"],
    y=hm5.values,
    labels={"x": "nombre de pages modifiées", "y": "nombre de fichiers"},
    title="Répartition des fichiers selon le nombre de pages modifiées",
    nbins=5,
    histfunc="sum",
    text_auto=True

)

df["hm50"] = df["how_many"].apply(lambda x: x if x < 50 else 50)
hm50 = df["hm50"].value_counts()
hm50 = hm50.sort_index()

fig5 = px.histogram(
    hm50,
    x=[e if e < 50 else "50+" for e in hm50.index],
    y=hm50.values,
    labels={"x": "nombre de pages modifiées", "y": "nombre de fichiers"},
    title="Répartition des fichiers selon le nombre de pages modifiées",
    histfunc="sum",
    text_auto=True,
    nbins=25
)

with open("ratio.html", "w") as f:
    f.write(fig.to_html())

with open("hm.html", "w") as f:
    f.write(fig2.to_html())

with open("hm10.html", "w") as f:
    f.write(fig3.to_html())

with open("hm5.html", "w") as f:
    f.write(fig4.to_html())

with open("hm50.html", "w") as f:
    f.write(fig5.to_html())
