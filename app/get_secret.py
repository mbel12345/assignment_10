def get_secret(secret_name: str) -> str:

    '''
    In a production environment, this function would query a credential manager so that no password files are needed.
    '''

    if secret_name == 'postgres':
        return 'postgres'
    elif secret_name == 'secret_key':
        return 'dret5rdt6weqfdsterw'
    else:
        raise ValueError(f'Unknown secret: {secret_name}')
