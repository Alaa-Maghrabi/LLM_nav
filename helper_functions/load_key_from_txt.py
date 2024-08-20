try:
    import os
    import numpy as np

except ImportError as e:
    raise e


def load_key(path: str = None):
    # Get the current script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    if path:
        key_path = path
    else:
        key_path = os.path.abspath(os.path.join(script_dir, '..', 'key', 'key.txt'))

    with open(key_path, 'r') as file:
        key = file.read().strip()
    return key
