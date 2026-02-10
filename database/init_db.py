from database.db import Base, engine


def init_db():
    Base.metadata.create_all(bind=engine)
    print("DATABASE TABLES CREATED / VERIFIED")
#@roshhellwett makaut tele bot