from pathlib import Path
from pdf2image import convert_from_path
from tqdm.auto import tqdm

pdfs = Path('pdfs')
imgs = Path('imgs')

pbar = pdfs.glob('**/*.pdf')
pbar = sorted(pbar, key=lambda x: x.name)
pbar = tqdm(pbar, unit='pdf')

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

