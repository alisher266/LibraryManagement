def validate_int(value, name):
    try:
        return int(value)
    except:
        print(f"{name} must be a number!")
        return None
