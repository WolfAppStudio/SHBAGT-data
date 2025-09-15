from pathlib import Path
#!/usr/bin/env python3
import json, sys, os, glob, re

ROOT = Path(os.path.dirname(os.path.abspath(__file__))).parent.as_posix()

REQUIRED_CHAPTER_KEYS = {
  'id': int,
  'chapter_number': int,
  'slug': str,
  'titles': dict,
  'summary': dict,
  'transliteration': str,
  'name_meaning': dict,
  'verses_count': int
}

REQUIRED_VERSE_KEYS = {
  'id': int,
  'verse_number': int,
  'chapter_number': int,
  'slug': str,
  'text': str,
  'transliteration': str
}

LANGS = {'english','hindi'}

def error(msg):
  print(f"ERROR: {msg}")
  return 1

def check_chapters():
  path = os.path.join(ROOT, 'data', 'chapters.json')
  if not os.path.exists(path):
    return error('chapters.json missing')
  with open(path,'r') as f:
    data = json.load(f)
  if not isinstance(data, dict) or 'chapters' not in data or 'meta' not in data:
    return error('chapters.json must have meta and chapters at top level')
  chapters = data['chapters']
  if not isinstance(chapters, list) or len(chapters) == 0:
    return error('chapters must be non-empty array')
  ok = True
  seen_numbers = set()
  for ch in chapters:
    for k,t in REQUIRED_CHAPTER_KEYS.items():
      if k not in ch or not isinstance(ch[k], t):
        print(f"ERROR: chapter {ch.get('chapter_number')} missing/invalid {k}")
        ok = False
    # titles
    titles = ch.get('titles', {})
    if not isinstance(titles, dict) or not isinstance(titles.get('hi', ''), str) or not isinstance(titles.get('en',''), str):
      print(f"ERROR: chapter {ch.get('chapter_number')} titles.hi/en invalid")
      ok = False
    # summary
    summary = ch.get('summary', {})
    if not isinstance(summary, dict) or not isinstance(summary.get('en',''), str) or not isinstance(summary.get('hi',''), str):
      print(f"ERROR: chapter {ch.get('chapter_number')} summary.en/hi invalid")
      ok = False
    # name_meaning
    nm = ch.get('name_meaning', {})
    if not isinstance(nm, dict) or not isinstance(nm.get('en',''), str) or not isinstance(nm.get('hi',''), str):
      print(f"ERROR: chapter {ch.get('chapter_number')} name_meaning.en/hi invalid")
      ok = False
    # verses dir exists
    vdir = os.path.join(ROOT, 'data', 'verses', f"chapter_{ch['chapter_number']}")
    if not os.path.isdir(vdir):
      print(f"ERROR: verses dir missing for chapter {ch['chapter_number']}: {vdir}")
      ok = False
    # count matches files present
    files = sorted(glob.glob(os.path.join(vdir, 'verse_*.json')))
    if len(files) != ch['verses_count']:
      print(f"ERROR: chapter {ch['chapter_number']} verses_count={ch['verses_count']} but files={len(files)}")
      ok = False
    # ensure uniqueness
    if ch['chapter_number'] in seen_numbers:
      print(f"ERROR: duplicate chapter_number {ch['chapter_number']}")
      ok = False
    seen_numbers.add(ch['chapter_number'])
  return 0 if ok else 1


def check_verses():
  ok = True
  for p in sorted(glob.glob(os.path.join(ROOT, 'data', 'verses', 'chapter_*', 'verse_*.json'))):
    with open(p,'r') as f:
      try:
        v = json.load(f)
      except Exception as e:
        print(f"ERROR: {p} invalid json: {e}")
        ok = False
        continue
    # basic keys
    for k,t in REQUIRED_VERSE_KEYS.items():
      if k not in v or not isinstance(v[k], t):
        print(f"ERROR: {p} missing/invalid {k}")
        ok = False
    # language arrays
    for arr_key in ('translations','commentaries'):
      arr = v.get(arr_key)
      if arr is None:
        continue
      if not isinstance(arr, list):
        print(f"ERROR: {p} {arr_key} must be array if present")
        ok = False
        continue
      for i, it in enumerate(arr):
        if not isinstance(it, dict):
          print(f"ERROR: {p} {arr_key}[{i}] not object")
          ok = False
          continue
        if it.get('language') not in LANGS:
          print(f"ERROR: {p} {arr_key}[{i}].language invalid: {it.get('language')}")
          ok = False
        if not isinstance(it.get('description',''), str) or not it.get('description',''):
          print(f"ERROR: {p} {arr_key}[{i}].description missing/empty")
          ok = False
        if not isinstance(it.get('author_name',''), str) or not it.get('author_name',''):
          print(f"ERROR: {p} {arr_key}[{i}].author_name missing/empty")
          ok = False
  return 0 if ok else 1


def main():
  ec = 0
  ec |= check_chapters()
  ec |= check_verses()
  if ec == 0:
    print('Validation passed: chapters and verses are well-formed.')
  sys.exit(ec)

if __name__ == '__main__':
  main()
