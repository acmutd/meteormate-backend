import base64
import binascii
from typing import Optional

from pydantic import BaseModel, model_validator

from utils.exceptions import UnprocessableEntity


class UserReportCreate(BaseModel):
    reportee_uid: str
    description: str
    screenshots: Optional[list[str]] = None

    screenshot_bytes: Optional[list[bytes]] = None
    screenshot_exts: Optional[list[str]] = None

    @model_validator(mode="before")
    @classmethod
    def parse_and_validate_screenshots(cls, values):
        screenshots = values.get("screenshots")
        if screenshots is None:
            return values
        
        screenshot_bytes = []
        screenshot_exts = []

        for screenshot in screenshots:
            if "," not in screenshot:
                raise UnprocessableEntity("Each screenshot must be a base64 string with a header")

            header, data = screenshot.split(",", 1)
            if not header.startswith("data:image/") or ";base64" not in header:
                raise UnprocessableEntity("Invalid image base64 header in one of the screenshots")

            ext = header[len("data:image/"):header.index(";base64")]
            if ext not in {"jpeg", "jpg", "png", "webp"}:
                raise UnprocessableEntity("Not an acceptable image type in one of the screenshots")

            try:
                image_bytes = base64.b64decode(data, validate=True)
            except (ValueError, binascii.Error):
                raise UnprocessableEntity("Image data has incorrect padding or invalid characters")

            screenshot_bytes.append(image_bytes)
            screenshot_exts.append(ext)
        
        values["screenshot_bytes"] = screenshot_bytes
        values["screenshot_exts"] = screenshot_exts
        
        return values
