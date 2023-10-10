class Config:
    SECRET_KEY = 'natalia16'

class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_HOST = "localhost"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = ""
    MYSQL_DB = "login"

config = {
    'development': DevelopmentConfig
}
