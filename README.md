# SAIC Python client library

## About

A Python package for interacting with the MG iSMART API.

MG iSMART is the connectivity system in your MG car (MG5 MG4, ZS...).

Presets are classmethods on `SaicApiConfiguration`. Each takes `(username, password, **overrides)`.

| Preset | `base_uri` | `region` | `tenant_id` | `device_app_id` |
|---|---|---|---|---|
| `mg_eu()` | `https://gateway-mg-eu.soimt.com/api.app/v1/` | `eu` | `459771` | `com.saicmotor.europecar` |
| `mg_au()` | `https://gateway-mg-au.soimt.com/api.app/v1/` | `au` | `459771` | `com.saicmotor.europecar` |
| `mg_tr()` | `https://gateway-mg-tr.soimt.com/api.app/v1/` | `tr` | `459771` | `com.saicmotor.europecar` |
| `mg_th()` | `https://gateway-mg-th.soimt.com/api.app/v1/` | `th` | `459771` | `com.saicmotor.ismartthai` |
| `mg_br()` | `https://gateway-mg-br.soimt.com/api.app/v1/` | `br` | `459771` | `com.saicmotor.europecar` |
| `maxus_eu()` | `https://gateway-maxus-eu.soimt.com/api.app/v1/` | `eu` | `590224` | `com.saicmaxus.ismarteu` |

MAXUS Europe vehicles use the same API. The `maxus_eu()` values were confirmed by a live traffic capture of the MAXUS app.

For Thailand, supply `login_authorization` as the complete `Authorization` header
(`Basic ...`) from the app's login request. Keep it secret; do not commit it or the
traffic capture. For phone login, also set `username_is_email=False` and
`phone_country_code="66"`. For example:

```python
import os

from saic_ismart_client_ng.model import SaicApiConfiguration

config = SaicApiConfiguration.mg_th(
    os.environ["SAIC_USERNAME"],
    os.environ["SAIC_PASSWORD"],
    username_is_email=False,
    phone_country_code="66",
    login_authorization=os.environ["SAIC_LOGIN_AUTHORIZATION"],
)
```

For the Thailand example, copy `examples/.env.example` to `examples/.env` and
set the complete authorization header there:

```dotenv
SAIC_LOGIN_AUTHORIZATION="Basic ..."
```

Existing environment variables take precedence over `.env`. The example's
username and password are configured separately in `examples/main.py`.
The example requests both vehicle status and charging management data for each
vehicle. If SAIC reports that vehicle access has been revoked, restore the
account's authorization to that vehicle in the app before retrying.

Supported functionality (partial list, check the code for more)

* login
* set alarm switches
* get message list
* get vehicle status
* get cached vehicle status (does not wake the car)
* get charging status
* lock vehicle
* unlock vehicle
* unlock the tailgate (releases the latch), or open and close a power tailgate
* door windows: close, ventilate (open a few centimetres) or fully open
* start rear window heating
* stop rear window heating
* remote climate
* heated seats: each seat on its own, front and rear, plus rear seat status
* heated steering wheel


## Prerequisites

You have an iSMART account (can be created in the iSMART app)

## Errors

Every error is a `SaicApiException` (or a subclass). Besides the message text, it carries SAIC's reply as separate values, so you don't need to parse the text:

* `return_code`: SAIC's numeric code (see `SaicReturnCode`), or `None`
* `saic_message`: the message on its own
* checks for the common cases: `is_vehicle_unreachable` (code 4), `is_request_rejected` (code 8), `is_vehicle_not_locked`, `is_logged_out` and `is_unexpected_failure`
