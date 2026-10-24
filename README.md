# SAIC Python client library

## About

A Python package for interacting with the MG iSMART API.

MG iSMART is the connectivity system in your MG car (MG5 MG4, ZS...).

Presets: `SaicApiConfiguration.mg_eu()`, `mg_au()` (Australia and New Zealand), `mg_tr()` (Türkiye).
Each takes `(username, password, **overrides)`.

MAXUS Europe vehicles use the same API. Use `SaicApiConfiguration.maxus_eu(username, password)`.
The preset values were confirmed by a live traffic capture of the MAXUS app.

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