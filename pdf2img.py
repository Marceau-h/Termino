import contextlib
import json
from pathlib import Path

from pdf2image import convert_from_path
from tqdm.auto import tqdm

pdfs = Path('pdfs')
imgs = Path('imgs')
done = Path('done.json')

if done.exists():
    with open(done, 'r') as f:
        done = json.load(f)
else:
    done = []

pbar = pdfs.glob('**/*.pdf')
pbar = sorted(pbar, key=lambda x: x.name)
pbar = tqdm(pbar, unit='pdf')

try:
    for pdf in pbar:
        pbar.set_description(pdf.name)
        if pdf.parent.name in ['to_do', 'Doublons', "Sans_ID", "Socard", "Labadie"]:
            # continue
            pass

        if pdf.name in ["Moreau386pp598-609_GALL.pdf", "Moreau577_GALL.pdf"]:
            continue

        folder = imgs / pdf.relative_to(pdfs).with_suffix('')
        if folder.exists():
            for image in folder.glob('*.png'):
                image.unlink()
        else:
            folder.mkdir(parents=True)

        for i, image in enumerate(convert_from_path(pdf, thread_count=10)):
            image.save(folder / f'{i}.png', 'PNG')

        done.append(pdf.name)
finally:
    with contextlib.suppress(KeyboardInterrupt):
        with open(done, 'w') as f:
            json.dump(done, f)
