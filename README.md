# The World in One Day — Wednesday 25 November 2026

![make.fun badge](https://make.fun/badge/news-image-20261125.svg)
[![rank](https://make.fun/badge/news-image-20261125/aahcoba8-maker/makefun-news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/aahcoba8-maker/makefun-news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

Entry for the [news-image-20261125 bounty on make.fun](https://make.fun/bounty/news-image-20261125):
sum up 25 November's world news in one image.

`main.py` (Python 3.13, standard library only at the top level) draws a
1024×1024 broadsheet PNG: 50 dated stories across 7 regions, 3 drawn lead
panels (Riyadh PIF Tower strike, Australia CPI 4.9%, Huawei verdict), a
numbered pin map, a UTC timeline band and a date-check footer. Pillow is
imported lazily; if it is unavailable the program copies the pre-rendered
image bundled in `assets/entry.png` instead. No network, no randomness —
every run writes identical bytes.

## Run

```sh
python3 main.py            # writes output/entry.png
```

Fonts in `fonts/` are subsets of DejaVu Sans (regular + bold), subset in
this session with `pyftsubset` to the glyphs the poster uses.
