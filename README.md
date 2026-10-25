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
* heated steering wheel


## Prerequisites

You have an iSMART account (can be created in the iSMART app)