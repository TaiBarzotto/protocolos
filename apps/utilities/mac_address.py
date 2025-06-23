import psutil

def get_mac_address():
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == psutil.AF_LINK:
                return addr.address
    return "00:00:00:00:00:00"  # Substitua com uma função que obtenha o MAC real.
