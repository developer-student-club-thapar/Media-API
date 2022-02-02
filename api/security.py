from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# run openssl rand -hex 32
# get key from dotenv
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_passwd(plain_passwd, hashed_passwd):
    return pwd_context.verify(plain_passwd, hashed_passwd)

def hashMe(password):
    return pwd_context.hash(password)

def create_access_token(user_id):
    """
    Create a new access token
    :param user_id:
    :return:
    """
    payload = {
        "sub": user_id
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_user_id(token):
    """
    Get user id from token
    :param token:
    :return:
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None

def verify_token(token):
    """
    Verify the token
    :param token:
    :return:
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
    return payload.get("sub")

"""
password = "raghav123"
hashed_password = hashMe(password)
# create access token 
access_token = create_access_token("raghavTinker")
print(access_token)
print(verify_token(access_token))
"""