"""Scrub a transcript: remove the Qrypt token and anything that looks like key or entropy bytes.
Usage: scrub.py IN OUT  -> prints flags as JSON (key_like_found, token_found)."""
import sys,re,json,os
k=open(os.path.expanduser('~/.config/agentforge/qrypt_api_key')).read().strip()
s=open(sys.argv[1],errors='replace').read()
f={'token_found':k in s}
f['partial_token_found']=k[:6] in s
for n in range(len(k),5,-1): s=s.replace(k[:n],'[REDACTED_TOKEN]')
s=re.sub(r'QRYPT_API_KEY=(?!\.\.\.|\[|\\n|\s|$)[^\s"\\]+','QRYPT_API_KEY=[REDACTED]',s)
hexpat=re.compile(r'(?<![0-9a-fA-F])[0-9a-fA-F]{32,}(?![0-9a-fA-F])')
b64pat=re.compile(r'[A-Za-z0-9+/]{40,}={0,2}')
f['key_like_found']=bool(hexpat.search(s))
s=hexpat.sub('[REDACTED_HEX]',s); s=b64pat.sub('[REDACTED_B64]',s)
open(sys.argv[2],'w').write(s); print(json.dumps(f))
