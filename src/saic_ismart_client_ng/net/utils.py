import httpx
from httpx._content import encode_request


def update_request_with_content(modified_request: httpx.Request, new_content: bytes):
    recomputed_headers, recomputed_stream = encode_request(content=new_content)
    modified_request.stream = recomputed_stream
    modified_request._content = new_content
    modified_request.headers.update(recomputed_headers)


def normalize_content_type(original_content_type: str):
    if 'multipart' in original_content_type:
        return 'multipart/form-data'
    elif 'x-www-form-urlencoded' in original_content_type:
        return 'application/x-www-form-urlencoded'
    else:
        return 'application/json'
