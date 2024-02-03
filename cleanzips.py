from pathlib import Path

pdfs = Path('pdfs')

for folder in pdfs.iterdir():
    for node in folder.iterdir():
        if not node.is_dir():
            continue

        for pdf in node.iterdir():
            pdf.rename(pdfs / folder.name / pdf.name)


