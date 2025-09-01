import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+mysqlconnector://root:YOUR_PASSWORD@localhost/mechanic_shop_api"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # set in env for prod
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    TOKEN_EXPIRES_IN = int(os.getenv("TOKEN_EXPIRES_IN", "3600"))  # seconds
