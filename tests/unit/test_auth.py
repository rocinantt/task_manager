from jose import jwt

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)


# --- hash_password --- 

def test_hash_password_returns_string():
    # Проверяем что функция возвращает непустую  строку
    plain_password = "qwerty12345"
    hashed_password = hash_password(plain_password)

    assert isinstance(hashed_password,  str)
    assert hashed_password != ""
    

def test_hash_password_differs_from_plain_password():
    # Хэш не должен совпадать с исходным паролем
    plain_password = "qwerty12345"
    hashed_password = hash_password(plain_password)

    assert hashed_password != plain_password


def test_hash_password_uses_salt():
    # Хэши одного пароля не  должны совпадать
    plain_password = "qwerty12345"

    hashed_password_1 = hash_password(plain_password)
    hashed_password_2 = hash_password(plain_password)

    assert hashed_password_1 != hashed_password_2


# --- verify_password --- 

def test_verify_password_accepts_correct():

    plain_password = "qwerty12345"
    hashed_password = hash_password(plain_password)

    assert verify_password(plain_password, hashed_password) is True


def test_verify_password_rejects_wrong():

    plain_password = "qwerty12345"
    wrong_password =  "password"
    hashed_password = hash_password(plain_password)

    assert verify_password(wrong_password, hashed_password) is False


# --- create_access_token --- 

def test_create_access_token_returns_string():
    # Проверяем что функция возвращает непустую  строку
    data  = {"user_id":  123}
    token = create_access_token(data=data)

    assert isinstance(token, str)
    assert token != ""


def test_create_access_token_payload_decodes_back():
    #  Проверяем  сорвпадение id после  декодирования
    data  = {"user_id":  123}
    token = create_access_token(data=data)

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get("user_id")

    assert user_id == 123



def test_create_access_token_contains_exp():
    # Проверяем наличие  exp в payload
    data  = {"user_id":  123}
    token = create_access_token(data=data)

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert 'exp' in payload