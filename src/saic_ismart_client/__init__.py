from saic_ismart_client.api.login import SaicLoginApi
from saic_ismart_client.api.vehicle import SaicVehicleApi


class SaicApi(SaicLoginApi, SaicVehicleApi):
    """ The SAIC Api client """
