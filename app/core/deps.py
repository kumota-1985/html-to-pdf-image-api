from slowapi import Limiter
from slowapi.util import get_remote_address

# Limiter configuration for SlowAPI
limiter = Limiter(key_func=get_remote_address)
