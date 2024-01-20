from saic_ismart_client_ng.api.message import SaicMessageApi
from saic_ismart_client_ng.api.user import SaicUserApi
from saic_ismart_client_ng.api.vehicle import SaicVehicleApi
from saic_ismart_client_ng.api.vehicle.climate import SaicVehicleClimateApi
from saic_ismart_client_ng.api.vehicle.locks import SaicVehicleLocksApi
from saic_ismart_client_ng.api.vehicle.windows import SaicVehicleWindowsApi
from saic_ismart_client_ng.api.vehicle_charging import SaicVehicleChargingApi


class SaicApi(
    SaicUserApi,
    SaicMessageApi,
    SaicVehicleLocksApi,
    SaicVehicleWindowsApi,
    SaicVehicleClimateApi,
    SaicVehicleChargingApi
):
    """ The SAIC Api client """
