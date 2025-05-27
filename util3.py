# utils.py
def get_nested_value(data, path):
    if isinstance(path, list):
        for p in path:
            val = get_nested_value(data, p)
            if val is not None:
                return val
        return None

    keys = path.split('.')
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, None)
        else:
            return None

    if isinstance(data, (int, float)):
        return data
    elif isinstance(data, str):
        clean = data.replace(",", "").strip()
        if clean.startswith("(") and clean.endswith(")"):
            try:
                return -float(clean[1:-1])
            except:
                return None
        try:
            return float(clean)
        except:
            return None
    else:
        return None
