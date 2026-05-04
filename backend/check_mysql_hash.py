import bcrypt
hash = '$2b$12$/s.iRIiLa38PyZg/TtVDSuewLBJWiffwE/GkKouu.TDsQkJNy6vgq'
passwords = ['123456', 'admin', 'admin123', 'admin123456', 'password', '']
for pwd in passwords:
    try:
        result = bcrypt.checkpw(pwd.encode('utf-8'), hash.encode('utf-8'))
        print(f'Password {repr(pwd)}: {result}')
    except Exception as e:
        print(f'Password {repr(pwd)}: ERROR {e}')
