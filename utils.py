import secrets
import string


def code_generator(length: int = 5):
    charset = string.digits + string.ascii_letters
    result = ""

    for _ in range(length):
        index = secrets.randbelow(len(charset))
        result += charset[index]

    return result
