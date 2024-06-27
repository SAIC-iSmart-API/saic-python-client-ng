from datetime import datetime
from typing import Union

import httpx
from httpx import Request, Response
from httpx._content import encode_request

from saic_ismart_client_ng.net.crypto import encrypt_request, decrypt_request, decrypt_response


async def encrypt_httpx_request(
        *,
        modified_request: Request,
        request_timestamp: datetime,
        base_uri: str,
        region: str,
        tenant_id: str,
        user_token: str = "",
        class_name: str = "",
):
    new_content, new_headers = encrypt_request(
        original_request_url=str(modified_request.url),
        original_request_headers=modified_request.headers,
        original_request_content=modified_request.content.decode("utf-8"),
        request_timestamp=request_timestamp,
        base_uri=base_uri,
        region=region,
        tenant_id=tenant_id,
        user_token=user_token,
        class_name=class_name
    )
    update_httpx_request_with_content(modified_request, new_content)
    modified_request.headers.update(new_headers)


async def decrypt_httpx_request(req: Request, base_uri: str):
    charset = 'utf-8'
    req_content = (await req.aread()).decode(charset).strip()
    if req_content:
        return decrypt_request(
            original_request_url=str(req.url),
            original_request_headers=req.headers,
            original_request_content=req_content,
            base_uri=base_uri
        )
    return req_content


async def decrypt_httpx_response(resp: Response):
    if resp.is_success:
        charset = resp.encoding
        resp_content = (await resp.aread()).decode(charset).strip()
        if resp_content:
            new_resp_content, new_resp_headers = decrypt_response(
                original_response_content=resp_content,
                original_response_headers=resp.headers,
                original_response_charset=charset
            )
            update_httpx_request_with_content(resp, new_resp_content)
            resp.headers.update(new_resp_headers)
    return resp


def update_httpx_request_with_content(modified_request: Union[httpx.Request, httpx.Response], new_content: bytes):
    recomputed_headers, recomputed_stream = encode_request(content=new_content)
    modified_request.stream = recomputed_stream
    modified_request._content = new_content
    modified_request.headers.update(recomputed_headers)
