import contextlib
import json
from pathlib import Path
# from concurrent.futures import ProcessPoolExecutor

from pdf2image import convert_from_path
from tqdm.auto import tqdm

pdfs = Path('../pdfs')
imgs = Path('../imgs2')
webp = Path('../webp')
done = Path('done.json')

max_width = 1920
max_height = 1080

if done.exists():
    with open(done, 'r') as f:
        done_list = json.load(f)
else:
    done_list = []

pbar = pdfs.glob('**/*.pdf')
pbar = sorted(pbar, key=lambda x: x.name)
pbar = tqdm(pbar, unit='pdf')

try:
    for pdf in pbar:
        pbar.set_description(pdf.name)
        if pdf.parent.name in ['to_do', 'Doublons', "Sans_ID", "Socard", "Labadie"]:
            continue
            pass

        if pdf.name in [
            "Moreau386pp598-609_GALL.pdf",
            "Moreau577_GALL.pdf",
            "Moreau1638_GALL.pdf",
            "Moreau1640_GALL.pdf",
            "Moreau3suppl47_GALL.pdf",
            "Moreau3suppl58_GALL.pdf",
            "├Йtat_general_des_Affaires_January_1650.pdf"
        ]:
            continue

        imgs_folder = imgs / pdf.relative_to(pdfs).with_suffix('')
        webp_folder = webp / pdf.relative_to(pdfs).with_suffix('')
        if imgs_folder.exists():
            images = list(imgs_folder.glob('*.png'))
            # if len(imgs) > 0:
            #     # continue
            for image in images:
                image.unlink()
        else:
            imgs_folder.mkdir(parents=True)

        if webp_folder.exists():
            images = list(webp_folder.glob('*.webp'))
            for image in images:
                image.unlink()
        else:
            webp_folder.mkdir(parents=True)

        for i, image in enumerate(convert_from_path(pdf, thread_count=10)):
            size = image.size
            if size[0] > max_width:
                size = (max_width, int(size[1] * max_width / size[0]))
            if size[1] > max_height:
                size = (int(size[0] * max_height / size[1]), max_height)
            image = image.resize(size)
            image.save(imgs_folder / f'{i}.png', 'png', optimize=True, quality=70, compress_level=9, lossless=False)
            image.save(webp_folder / f'{i}.webp', 'webp', optimize=True, quality=70, compress_level=9, lossless=False)

        done_list.append(pdf.name)

finally:
    with contextlib.suppress(KeyboardInterrupt):
        with open(done, 'w') as f:
            json.dump(done_list, f)
