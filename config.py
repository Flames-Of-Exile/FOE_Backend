import os

main_config = {}
main_config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
main_config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
main_config['SECRET_KEY'] = os.environ['SECRET_KEY']
main_config['JWT_ACCESS_TOKEN_EXPIRES'] = 300  # 5 minutes
main_config['JWT_REFRESH_TOKEN_EXPIRES'] = 86400  # 1 day
main_config['SECURITY_PASSWORD_SALT'] = os.environ['SECURITY_PASSWORD_SALT']

test_config = {}
test_config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
test_config['SECRET_KEY'] = "SUPER-SECRET"
test_config['JWT_ACCESS_TOKEN_EXPIRES'] = 300  # 5 minutes
test_config['JWT_REFRESH_TOKEN_EXPIRES'] = 86400  # 1 day
test_config['SECURITY_PASSWORD_SALT'] = 'super-secret'
test_config['TESTING'] = True
test_config['WTF_CSRF_ENABLED'] = False
test_config['DEBUG'] = False
test_config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flamesofexile:flamesofexile@test-db:5432/flamesofexile'
