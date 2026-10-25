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
| `maxus_eu()` | `https://gateway-maxus-eu.soimt.com/api.app/v1/` | `eu` | `590224` | `com.saicmaxus.ismarteu` |

MAXUS Europe vehicles use the same API. The `maxus_eu()` values were confirmed by a live traffic capture of the MAXUS app.

Supported functionality (partial list, check the code for more)

* login
* set alarm switches
* get message list
* get vehicle status
* get cached vehicle status (does not wake the car)
* get charging status
* lock vehicle
* unlock vehicle
* start rear window heating
* stop rear window heating
* remote climate
* heated seats


## Prerequisites

You have an iSMART account (can be created in the iSMART app)

## Errors

Every error is a `SaicApiException` (or a subclass). Besides the message text, it carries SAIC's reply as separate values, so you don't need to parse the text:

* `return_code`: SAIC's numeric code (see `SaicReturnCode`), or `None`
* `saic_message`: the message on its own
* checks for the common cases: `is_vehicle_unreachable` (code 4), `is_request_rejected` (code 8), `is_vehicle_not_locked`, `is_logged_out` and `is_unexpected_failure`
