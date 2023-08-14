import urllib.request


def find_ip() -> str:
    external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    return external_ip