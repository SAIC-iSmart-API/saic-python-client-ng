import base64
import logging
from typing import Optional

__LOGGER = logging.getLogger(__name__)


def decode_bytes(*, input_value: Optional[str | int], field_name: str) -> Optional[bytes]:
    try:
        if isinstance(input_value, str):
            return base64.b64decode(input_value)
        elif isinstance(input_value, int):
            return input_value.to_bytes((input_value.bit_length() + 7) // 8, 'big')
    except Exception as e:
        __LOGGER.error("Failed to decode %s: %s", field_name, input_value, exc_info=e)
    return None
