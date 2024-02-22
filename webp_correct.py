from pathlib import Path

webp = Path('webp')

for webp_folder in webp.glob('*/*'):
    print(webp_folder)
    if not webp_folder.name.endswith("_path"):
        continue

    good_name = webp_folder.name[:-5]
    good_folder = webp_folder.parent / good_name
    good_folder.mkdir(parents=True, exist_ok=True)
    for webp_file in webp_folder.glob('*/*.webp'):
        new_file = good_folder / webp_file.name
        webp_file.rename(new_file)

    for webp_subfolder in webp_folder.glob('*'):
        if webp_subfolder.is_dir():
            webp_subfolder.rmdir()

    webp_folder.rmdir()

