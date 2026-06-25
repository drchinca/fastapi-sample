import random
import string


def random_email() -> str:
    local = "".join(random.choices(string.ascii_lowercase + string.digits, k=random.randint(8, 14)))
    domain = "".join(random.choices(string.ascii_lowercase, k=random.randint(5, 10)))
    tld = random.choice(("com", "org", "net", "io", "dev"))
    return f"{local}@{domain}.{tld}"


def random_name() -> str:
    first = random.choice(("Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley"))
    last = random.choice(("Smith", "Lee", "Patel", "Garcia", "Kim", "Brown"))
    return f"{first} {last}"
