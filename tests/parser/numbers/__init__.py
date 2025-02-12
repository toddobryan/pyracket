BASE_PREFIXES = {
    2 : ["#b", "#B"],
    8 : ["#o", "#O"],
    10 : ["", "#d", "#D"],
    16 : ["#x", "#X"],
}

def exact_prefixes(base: int) -> list[str]:
    assert base in BASE_PREFIXES
    prefixes = []
    for exact_prefix in ["", "#e", "#E"]:
        for base_prefix in BASE_PREFIXES[base]:
            prefixes.append(exact_prefix + base_prefix)
            if exact_prefix and base_prefix:
                prefixes.append(base_prefix + exact_prefix)
    return prefixes

EXACT = ["", "#e", "#E"]
DECIMAL = ["", "#d", "#D"]
BINARY = ["#b", "#B"]
OCTAL = ["#o", "#O"]
HEX = ["#x", "#X"]

def strip_base(s: str) -> str:
    if s.startswith("-"):
        return s[0] + s[3:]
    else:
        return s[2:]
