import yaml
import json
import sys
import hashlib
from pathlib import Path
from jsonschema import validate, ValidationError

config_path = Path(__file__).parent.parent / "src" / "config" / "features.yaml"
schema_path = Path(__file__).parent.parent / "src" / "config" / "features.schema.json"

def sha256sum(filename):
    h = hashlib.sha256()
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def main():
    with open(config_path) as f:
        config = yaml.safe_load(f)
    with open(schema_path) as f:
        schema = json.load(f)
    try:
        validate(instance=config, schema=schema)
        print("✅ features.yaml is valid!")
        print(f"SHA256: {sha256sum(config_path)}")
    except ValidationError as e:
        print(f"❌ features.yaml validation error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
