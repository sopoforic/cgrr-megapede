megapede
========

This module reads score files and resources for Megapede, a game by Cheesy
Software.

Usage
=====

Use `read_scores` to read a score file:

```python
>>> megapede.read_scores("path/to/megapede")
[
  {
    'name': 'TRCY',
    'score': 6128,
    'level': 2
  },
  {
    'name': 'SCORE3765Z',
    'score': 3765,
    'level': 1
  },
  # more scores
]
```

Use `read_resources` to get a dictionary of resources in `MEGAPEDE.RES`
(experimental!):

```python
>>> res = megapede.read_resources("path/to/megapede")
>>> res.keys()
dict_keys([
  'GAMEOVER.DIG',
  'LEVEL4.DIG',
  'MEGAPEDE.STL',
  'BLAG.DIG',
  # more resource files
])
```

Requirements
============

* Python 2.7+ or 3.3+
    * No python 2.6 or 3.2.
* cgrr from https://github.com/sopoforic/cgrr
* pillow
* jinja2 (if you want to do an html export)

You can install these dependencies with `pip install -r requirements.txt`.

License
=======

This module is available under the GPL v3 or later. See the file COPYING for
details.

[![Code Health](https://landscape.io/github/sopoforic/cgrr-megapede/master/landscape.svg?style=flat)](https://landscape.io/github/sopoforic/cgrr-megapede/master)
