
# Verify if the date provided is valid
def verify_date(date_str):
    try:
        if len(date_str) != 8:
            return False
        day = int(date_str[:2])
        month = int(date_str[2:4])
        year = int(date_str[4:])
        if day < 1 or day > 31 or month < 1 or month > 12 or year < 1000:
            return False
        return True
    except ValueError:
        return False

# Verify if the number of files provided is valid
def verify_num_files(num_files_str):
    try:
        num_files = int(num_files_str)
        return num_files > 0
    except ValueError:
        return False