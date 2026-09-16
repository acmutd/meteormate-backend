# Created by Atharva Mishra
# ACM MeteorMate | All Rights Reserved

from fastapi import Depends
from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter

# Survey, Profiles, and Auth Routes
sensitive_updates_limit = Limiter(Rate(1, Duration.MINUTE * 2))  # 1 request every 2 minutes for sensitive update endpoints
regular_updates_limit = Limiter(Rate(5, Duration.MINUTE))  # 5 requests per minute for regular update endpoints
get_limit = Limiter(Rate(10, Duration.MINUTE))  # 10 requests per minute for get endpoints

sensitive_updates_limiter = Depends(RateLimiter(sensitive_updates_limit))
regular_updates_limiter = Depends(RateLimiter(regular_updates_limit))
get_rate_limiter = Depends(RateLimiter(get_limit))
