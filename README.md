# Pokémon cryptic solver

A small Flask website around `pokemonCryptic.py`. It lists answers from Pokémon,
items, moves, abilities and locations that fit a pattern and contain the letters
of a suspected anagram.

## Run it

    pip install -r requirements.txt
    python app.py

The site runs on port 5060 by default. Open http://localhost:5060

Chrome and Edge refuse to open port 5060 (they show ERR_UNSAFE_PORT), because it
is the standard SIP port. If that happens, pick another port:

    PORT=5006 python app.py

Set HOST=0.0.0.0 if you want other devices on your network to reach it.

## Deploy with Docker / Northflank

    docker build -t pokemon-cryptic .
    docker run -p 8000:8000 pokemon-cryptic

The container runs gunicorn on $PORT (8000 in the container). On Northflank, create a
service from this repo using the Dockerfile build, add an HTTP port 8000 under
networking, and set the health check path to /healthz. Public Northflank URLs
are served over HTTPS on port 443, so the Chrome port-5060 block does not apply
there.

## Using it

- Pattern: `*` is an unknown letter. Spaces and punctuation count as squares,
  so `**** ***d` means a four-letter word, a space, then a three-letter word
  ending in D.
- Anagram letters (optional): every one of these letters must appear in the answer.
- There is also a JSON endpoint: `/api/solve?template=**** ***d&fodder=noir`

## Files

- `pokemonCryptic.py`: your script. The matching logic is unchanged; `solve()` now
  returns its matches instead of printing them, and `main()` only runs when the
  file is executed directly, so it still works on the command line.
- `app.py`: the web server and input cleanup (apostrophes, accents, extra spaces).
- `templates/index.html`: the page.
