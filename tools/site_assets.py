"""Deterministic shared bundles; filenames change whenever their bytes change."""
def asset_bundle(name,extension,sources):
 parts=[(ROOT/'assets'/source).read_text() for source in sources]
 content=('\n'.join(';(()=>{\n'+part+'\n})();' for part in parts) if extension=='js' else '\n'.join(parts)).encode()
 filename=name+'-'+hashlib.sha256(content).hexdigest()[:12]+'.'+extension
 (ROOT/'assets'/filename).write_bytes(content)
 return '/assets/'+filename
SITE_CSS=asset_bundle('site','css',['style.css','catalog-enhancements.css','ux.css','home.css','conversion.css'])
SITE_JS=asset_bundle('site','js',['ux.js','app.js','catalog-enhancements.js','conversion.js'])

BLOG_CSS=asset_bundle('blog','css',['blog.css'])
