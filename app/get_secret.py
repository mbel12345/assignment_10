def get_secret(secret_name: str) -> str:

    '''
    Read secret from secrets/secret_name.password.text.
    In a production environment, this function would query a credential manager so that no password files are needed.
    '''

    with open(f'secrets/{secret_name}.secret.txt', 'r') as in_f:
        return in_f.read().strip()
