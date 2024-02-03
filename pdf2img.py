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
        continue

    if pdf.name in ["Moreau386pp598-609_GALL.pdf", "Moreau577_GALL.pdf"]:
        continue

    folder = imgs / pdf.relative_to(pdfs).with_suffix('')
    if folder.exists():
        continue

    images = convert_from_path(pdf, thread_count=10)

    try:

        folder.mkdir(parents=True)

        for i, image in enumerate(images):
            image.save(folder / f'{i}.png', 'PNG')
    except KeyboardInterrupt:
        pass

# from pathlib import Path
# from concurrent.futures import ProcessPoolExecutor
#
# from pdf2image import convert_from_path
# from tqdm.auto import tqdm
#
# pdfs = Path('pdfs')
# imgs = Path('imgs')
#
# pbar = pdfs.glob('**/*.pdf')
# pbar = sorted(pbar, key=lambda x: x.name)
# # pbar = tqdm(pbar, unit='pdf')
#
# def convert(pdf):
#     # pbar.set_description(pdf.name)
#     if pdf.parent.name in ['to_do', 'Doublons', "Sans_ID", "Socard", "Labadie"]:
#         return
#
#     folder = imgs / pdf.relative_to(pdfs).with_suffix('')
#     if folder.exists():
#         return
#
#     images = convert_from_path(pdf)
#
#     try:
#
#         folder.mkdir(parents=True)
#
#         for i, image in enumerate(images):
#             image.save(folder / f'{i}.png', 'PNG')
#     except KeyboardInterrupt:
#         pass
#
# with ProcessPoolExecutor(5) as executor:
#     executor.map(convert, pbar)
