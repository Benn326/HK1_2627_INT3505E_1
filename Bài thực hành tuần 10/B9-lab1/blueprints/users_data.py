USERS = {
    1: {"first_name": "Đỗ", "last_name": "Trung Hiếu", "email": "dth@example.com"},
    2: {"first_name": "Cù", "last_name": "Văn Cương", "email": "cvc@example.com"},
    42: {"first_name": "Bùi", "last_name": "Đình Cấn", "email": "bdc@example.com"},
}


def get_user(uid: int):
    return USERS.get(uid)
