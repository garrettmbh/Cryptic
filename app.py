import os
import re
import unicodedata

from flask import Flask, jsonify, render_template, request

import pokemonCryptic as pc

PORT = int(os.environ.get("PORT", 5060))
HOST = os.environ.get("HOST", "127.0.0.1")
MAX_PER_CATEGORY = 300
MAX_TEMPLATE_LENGTH = 40

app = Flask(__name__)


def normalize(text):
    """Make typed input and the word lists comparable.

    - straight, curly and double quotes all count as the same apostrophe
    - accents are dropped (Flabébé -> FLABEBE)
    - tabs / repeated spaces collapse to single spaces
    - everything is uppercased
    """
    text = text.replace("\u2019", "'").replace("\u2018", "'").replace('"', "'")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return " ".join(text.split()).upper()


def pretty(item):
    """Show the lists' stand-in double quote as a real apostrophe."""
    return item.replace('"', "\u2019")


CATEGORIES = [
    ("Pokémon", pc.listPokemon),
    ("Items", pc.listItems),
    ("Moves", pc.listMoves),
    ("Abilities", pc.listAbilities),
    ("Locations", pc.listLocations),
]

# For each category: the normalized words the solver runs on, plus a map back
# to the original spelling so results display nicely.
INDEX = []
for label, loader in CATEGORIES:
    keys = []
    display = {}
    for raw in loader():
        key = normalize(raw)
        if key not in display:
            keys.append(key)
            display[key] = []
        display[key].append(pretty(raw.strip()))
    INDEX.append((label, keys, display))


def run_solver(template, fodder):
    template = normalize(template).replace("_", "*")
    fodder = re.sub(r"[^A-Z0-9]", "", normalize(fodder))

    results = []
    for label, keys, display in INDEX:
        found = pc.solve(template, fodder, keys)
        words = [d for key in found for d in display[key]]
        results.append(
            {
                "category": label,
                "count": len(words),
                "words": sorted(words)[:MAX_PER_CATEGORY],
                "truncated": len(words) > MAX_PER_CATEGORY,
            }
        )
    return template, fodder, results


@app.get("/healthz")
def healthz():
    return "ok", 200


@app.get("/")
def home():
    return render_template("index.html", max_length=MAX_TEMPLATE_LENGTH)


@app.route("/api/solve", methods=["GET", "POST"])
def solve_api():
    data = request.get_json(silent=True) if request.method == "POST" else None
    source = data if isinstance(data, dict) else request.args
    template = str(source.get("template", "")).strip()
    fodder = str(source.get("fodder", "")).strip()

    if not template:
        return jsonify(error="Enter a pattern, for example **** ***d"), 400
    if len(template) > MAX_TEMPLATE_LENGTH:
        return jsonify(error=f"Patterns can be up to {MAX_TEMPLATE_LENGTH} characters long."), 400

    clean_template, clean_fodder, results = run_solver(template, fodder)
    return jsonify(
        template=clean_template,
        fodder=clean_fodder,
        total=sum(r["count"] for r in results),
        results=results,
    )


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=False)
