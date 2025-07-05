def verif_str(name: str) -> bool:
    stripped = name.replace(" ", "")
    if not stripped:
        return False
    if not stripped.isalpha():
        return False
    return True


def verif_tel_number(num: str) -> bool:
    stripped = num.replace(" ", "")
    if not stripped:
        return False
    if not stripped.isdigit():
        return False
    if len(stripped) != 8:
        return False
    return True
