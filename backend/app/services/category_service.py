from datetime import date


def calculate_category(birth_date: date) -> str:
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    if age <= 7:
        return "Mini Infantil 7"
    elif age == 8:
        return "Mini Infantil 8"
    elif age == 9:
        return "Mini Infantil 9"
    elif age == 10:
        return "Preinfantil"
    elif age <= 13:
        return "Transición"
    elif age == 14:
        return "Prejuvenil"
    elif age <= 17:
        return "Juvenil"
    else:
        return "Mayores"
