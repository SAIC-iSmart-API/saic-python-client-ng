from dataclasses import dataclass, field
from typing import List


@dataclass
class LoginResp():
    @dataclass
    class LoginRespDetail():
        languageType: str

    access_token: str
    account: str
    avatar: str
    client_id: str
    dept_id: str
    detail: LoginRespDetail
    expires_in: int
    jti: str
    languageType: str  # Assuming you want to include this as well
    license: str
    oauth_id: str
    post_id: str
    refresh_token: str
    role_id: str
    role_name: str
    scope: str
    tenant_id: str
    token_type: str
    user_id: str
    user_name: str


@dataclass
class VehicleListResp:
    @dataclass
    class VinListDTO:
        @dataclass
        class SubAccountListDTO:
            authorizationCardType: int
            btKeyStatus: int
            locationAuthorization: int
            modelName: str
            operationType: int
            status: int
            subaccountId: int
            subscriberId: int
            userAccount: str
            userName: str
            validityEndTime: int
            validityStartTime: int
            vin: str

        @dataclass
        class VehicleModelConfigurationDTO:
            itemCode: str
            itemName: str
            itemValue: str

        bindTime: int
        brandName: str
        colorName: str
        isActivate: bool
        isCurrentVehicle: bool
        isSubaccount: bool
        modelName: str
        modelYear: str
        name: str
        series: str
        vin: str
        # subAccountList: List[SubAccountListDTO] = field(default_factory=list) # TODO: Try with something that has this field
        vehicleModelConfiguration: List[VehicleModelConfigurationDTO] = field(default_factory=list)

    vinList: List[VinListDTO] = field(default_factory=list)
