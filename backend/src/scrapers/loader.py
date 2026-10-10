import json

def load_sources(type: str) -> list[dict]:
    with open("sources.json", "r") as f:
        sources = json.load(f)
    return [source for source in sources if source["type"] == type]
