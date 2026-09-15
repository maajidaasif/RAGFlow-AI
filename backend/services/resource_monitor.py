import psutil


def check_available_ram():
    memory = psutil.virtual_memory()

    available_ram_gb = memory.available / (1024 ** 3)

    return available_ram_gb


def get_ram_status(available_ram_gb, threshold_gb):
    if available_ram_gb >= threshold_gb:
        return "GREEN"
    else:
        return "RED"


def show_ram_warning():
    print("WARNING: Low available RAM.")
    print("Please close unnecessary applications before running heavy AI processing.")


if __name__ == "__main__":
    ram = check_available_ram()
    status = get_ram_status(ram, 4)

    print(f"Available RAM: {ram:.2f} GB")
    print(f"RAM Status: {status}")

    if status == "RED":
        show_ram_warning()