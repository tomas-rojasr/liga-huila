from datetime import date


def calculate_category(birth_date: date) -> str:
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    if age < 8:
        return "SUB-8"
    elif age < 10:
        return "SUB-10"
    elif age < 12:
        return "SUB-12"
    elif age < 14:
        return "SUB-14"
    elif age < 16:
        return "SUB-16"
    elif age < 18:
        return "SUB-18"
    elif age < 20:
        return "SUB-20"
    else:
        return "PRIMERA"
