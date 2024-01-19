from dataclasses import dataclass, field


@dataclass
class LoginResp():
    @dataclass
    class LoginRespDetail():
        languageType: str = field(init=False),

    access_token: str = field(init=False),
    account: str = field(init=False),
    avatar: str = field(init=False)
    client_id: str = field(init=False),
    dept_id: str = field(init=False),
    detail: LoginRespDetail = field(init=False),
    expires_in: int = field(init=False),
    jti: str = field(init=False),
    languageType: str = field(init=False),
    license: str = field(init=False),
    oauth_id: str = field(init=False),
    post_id: str = field(init=False),
    refresh_token: str = field(init=False),
    role_id: str = field(init=False),
    role_name: str = field(init=False),
    scope: str = field(init=False),
    tenant_id: str = field(init=False),
    token_type: str = field(init=False),
    user_id: str = field(init=False),
    user_name: str = field(init=False),
