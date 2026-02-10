from core.config import Config

def is_admin(user_id):
    return int(user_id) == Config.ADMIN_ID
#@roshhellwett makaut tele bot