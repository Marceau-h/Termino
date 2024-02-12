from pathlib import Path

corr = "MAZ_corr"
non_corr = "MAZ_non_corr"

files_corr = [e.name for e in Path(corr).glob("*/*")]

files_non_corr = [e.name for e in Path(non_corr).glob("*/*") if "to_do" not in e.parents]

diff = set(files_non_corr).difference(set(files_corr))

print(diff)
print(len(diff))
print(len(files_corr))
print(len(files_non_corr))

