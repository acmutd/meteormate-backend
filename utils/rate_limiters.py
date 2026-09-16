# Created by Atharva Mishra
# ACM MeteorMate | All Rights Reserved

from fastapi import Depends
from fastapi_limiter.depends import RateLimiter
from pyrate_limiter import Duration, Limiter, Rate

from config import settings

if settings.DEBUG:
    sensitive_updates_limit = Limiter(Rate(6, Duration.MINUTE))
    regular_updates_limit = Limiter(Rate(30, Duration.MINUTE))
    get_limit = Limiter(Rate(120, Duration.MINUTE))
    verification_send_limit = Limiter(Rate(5, Duration.MINUTE * 15))
    verification_submit_limit = Limiter(Rate(20, Duration.MINUTE * 15))
else:
    sensitive_updates_limit = Limiter(Rate(2, Duration.MINUTE * 10))
    regular_updates_limit = Limiter(Rate(10, Duration.MINUTE))
    get_limit = Limiter(Rate(60, Duration.MINUTE))
    verification_send_limit = Limiter(Rate(2, Duration.MINUTE * 15))
    verification_submit_limit = Limiter(Rate(8, Duration.MINUTE * 15))

sensitive_updates_limiter = Depends(RateLimiter(sensitive_updates_limit))
regular_updates_limiter = Depends(RateLimiter(regular_updates_limit))
get_rate_limiter = Depends(RateLimiter(get_limit))
verification_send_limiter = Depends(RateLimiter(verification_send_limit))
verification_submit_limiter = Depends(RateLimiter(verification_submit_limit))
