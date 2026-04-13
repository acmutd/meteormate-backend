# Created by Atharva Mishra
# ACM MeteorMate | All Rights Reserved

from fastapi import Depends
from pyrate_limiter import Duration, Limiter, Rate
from fastapi_limiter.depends import RateLimiter

# Survey, Profiles, and Auth Routes
update_limiter = Limiter(Rate(1, Duration.MINUTE * 2))  # 1 request every 2 minutes for update/create endpoints
get_limiter = Limiter(Rate(10, Duration.MINUTE))  # 10 requests per minute for get endpoints

update_rate_limit = Depends(RateLimiter(update_limiter))
get_rate_limit = Depends(RateLimiter(get_limiter))
