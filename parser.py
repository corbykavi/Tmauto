# parser.py
import re
from typing import Dict, Optional

# Normalizer + heuristic parser

RE_YEAR = re.compile(r'\((?P<year>19\d{2}|20\d{2})\)')
RE_SEASON = re.compile(r'(?:S|Season)[\s\._-]*?(?P<season>\d{1,2})', re.IGNORECASE)
RE_EP_RANGE = re.compile(r'(?:EP|E|Episodes?)\s*[^\d]*(?P<range>\d{1,3}(?:[^\d\-_,]*[-,]\d{1,3})*)', re.IGNORECASE)
RE_EP_SINGLE = re.compile(r'\bEP(?:ISODE)?\s*\.?\s*(?P<ep>\d{1,3})\b', re.IGNORECASE)
RE_RES = re.compile(r'(2160p|1080p|720p|480p|4k|x264|x265)', re.IGNORECASE)
RE_LANGS = re.compile(r'\[([^\]]+)\]')
RE_SIZE = re.compile(r'(?P<size>\d+(?:\.\d+)?)\s*(?P<unit>GB|MB)', re.IGNORECASE)

def extract_title_year_basename(name: str) -> (str, Optional[int]):
    # remove common uploader prefixes
    n = re.sub(r'^\s*\[?[A-Za-z0-9\-_. ]+\]?\s*[-_]*\s*', '', name)
    # pick year if present
    m = RE_YEAR.search(n)
    year = int(m.group("year")) if m else None
    # remove trailing bracketed groups for title base
    # take part before common separators like '-' ' - ' '  -  ' between title and tags
    base = n
    # cut at first ' - ' after title-like substring if many tokens
    # heuristic: split on ' - ' or ' — ' or ' _ ' and take leftmost part that contains letters
    parts = re.split(r'\s[-–—_]\s', base, maxsplit=1)
    title_part = parts[0]
    # remove year portion from title part
    if year:
        title_part = re.sub(r'\(\s*' + str(year) + r'\s*\)', '', title_part)
    return title_part.strip(), year

def parse_filename(name: str) -> Dict:
    # input: raw filename (may include extension and .001 etc)
    s = name.strip()
    # try to find languages
    langs_m = RE_LANGS.search(s)
    languages = None
    if langs_m:
        languages = langs_m.group(1).replace('+', '+').strip()
    # resolution/quality
    res_m = RE_RES.search(s)
    quality = res_m.group(1) if res_m else None
    # season
    season_m = RE_SEASON.search(s)
    season = int(season_m.group("season")) if season_m else None
    # episode range or single
    ep = None
    ep_m = RE_EP_RANGE.search(s)
    if ep_m:
        ep = ep_m.group("range").strip()
    else:
        ep2 = RE_EP_SINGLE.search(s)
        if ep2:
            ep = ep2.group("ep")
    # size if in name
    size_m = RE_SIZE.search(s)
    size = f"{size_m.group('size')}{size_m.group('unit')}" if size_m else None

    title, year = extract_title_year_basename(s)
    group_tag = title.lower()
    if year:
        group_tag += f" ({year})"
    if season:
        group_tag += f" S{str(season).zfill(2)}"
    if languages:
        group_tag += f" [{languages}]"
    return {
        "title": title,
        "year": year,
        "season": season,
        "episode": ep,
        "languages": languages,
        "quality": quality,
        "size_text": size,
        "group_tag": group_tag
    }