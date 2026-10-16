from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]
target=ROOT/'packhubglobe-hostinger-public_html.zip'
public_folders=['assets','catalog','products','industries','materials','services','guides','about','factory','request-quote','cases','privacy','terms','editorial-policy']
files=[ROOT/name for name in ['index.html','404.html','.htaccess','robots.txt','sitemap.xml','llms.txt']]
for folder in public_folders:files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file())
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
 for file in sorted(files):archive.write(file,file.relative_to(ROOT))
print(f'{target} — {len(files)} deployable files')
