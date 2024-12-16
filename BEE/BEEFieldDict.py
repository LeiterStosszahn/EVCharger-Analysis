# 所有#标注的字段网站中没有用到，可以考虑删除？
BEEField = {
    "id": "充电站编号",
    # "cpo_id": 1052,
    "state_id": "省/邦编号",
    "city_id": "城市编号",
    # "discom_id": null,
    "station_name": "充电站名称",
    "address": "充电站地址",
    # "pincode": null,
    "lat": "纬度",
    "lng": "经度",
    "state_name": "省/邦名称", # Map by state_id
    "companyname": "运营公司",
    "st_owner": "所有人",
    "mobile_no": "联系电话",
    "contactPerson": "联系人",
    "amenities": "是否有便利设施",
    # "avg_cost_discom": null,
    "opening_time": "开放时间",
    "closing_time": "关闭时间",
    # "is_tweenty_four_seven": "f",
    "city_name": "城市名称",
    "wkStatus": "充电站状态", #True is Available, False is Not Available
    "is_fourwheeler": "是否支持大型四轮车",
}

# 所有的字段后面会加上ChargerX，X是充电枪的顺序编号
BEEFieldCharger = {
    # "id": 165582,
    "chargerRatedCapacityId": "充电功率（kW）",
    "typeOfChargerId": "充电器种类", 
    #####
    # 1,6: https://evyatra.beeindia.gov.in/wp-content/themes/bee/assets/images/mapImages/BharatAC001_1.png
    # 5,8: mapImages/Chademo_1.png
    # 2,7: mapImages/BharatDC001_1.png
    # 4: mapImages/Type2Ac_1.png
    # 3,9: mapImages/ccs2_1.png
    # Other:
    # if chargerType include T2 and power_type is DC: ccs.png
    # if chargerType include T2 and power_type is AC: type-2-ac.png
    #####
    # "ocpi_tariff_rate_id": null,
    # "noOfChargers": null,
    "chargerType": "充电器类型（名称）",
    "ratedCapacity": "充电功率（kW）",
    # "serviceCharge": null,
    "power_type": "供电类型",
    "connector_working_status": "充电桩可用状态", #AVAILABLE is available, UNAVAILABLE is NOT KNOWN, Other is OCCUPIED
    # "wkStatus": false,
    "tariff_rate": "收费标准"
}