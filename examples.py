import json
import os

def load_examples() -> list[dict]:
    """Load few-shot examples from examples.json. Returns [] if file missing."""
    path = os.path.join(os.path.dirname(__file__), "examples.json")
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        print(f"Warning: examples.json is malformed: {e}")
        return []