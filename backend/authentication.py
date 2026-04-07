from passlib.context import CryptContext


passwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get_hashed_passwd(password):
    return password #passwd_context.hash(password)




