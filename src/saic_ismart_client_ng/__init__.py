from saic_ismart_client_ng.api.login import SaicLoginApi
from saic_ismart_client_ng.api.vehicle import SaicVehicleApi
from saic_ismart_client_ng.api.vehicle_charging import SaicVehicleChargingApi


class SaicApi(SaicLoginApi, SaicVehicleApi, SaicVehicleChargingApi):
    """ The SAIC Api client """
