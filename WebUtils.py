from datetime import datetime, timedelta
import hashlib
import requests
import time
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from ConfigParams import cgAuthorization, captchaToken, codeStartTime


header = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "app-key": "8fceb735082b5a529312040b58ea780b",
    "Content-Type": "application/x-www-form-urlencoded",
    "Connection": "keep-alive",
    "Proxy-Connection": "keep-alive",
    "Host": "www.tyys.zju.edu.cn",
    "Referer": "http://www.tyys.zju.edu.cn/venue/reservation",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "cgAuthorization": cgAuthorization,
    "sign": "",
    "timestamp": ""
}


def get_day_info(venueSiteId, searchDate):
    timestamp = get_timestamp()
    uri = "/api/reservation/day/info"
    data = {
        "venueSiteId": venueSiteId,
        "searchDate": searchDate,
        "nocache": timestamp
    }
    header["sign"] = get_sign_from_data(data, uri, timestamp)
    header["timestamp"] = timestamp
    return requests.get(
        f"{get_url(uri)}?venueSiteId={venueSiteId}&searchDate={searchDate}&nocache={timestamp}",
        headers=header)


def get_order_info(spaceId, timeId, venueSpaceGroupId, venueSiteId, searchDate, token):
    timestamp = get_timestamp()
    uri = "/api/reservation/order/info"
    json_str = '[{'
    json_str += f'"spaceId":"{spaceId}","timeId":"{timeId}","venueSpaceGroupId":{venueSpaceGroupId}'
    json_str += '}]'
    data = {
        "venueSiteId": venueSiteId,
        "reservationDate": searchDate,
        "weekStartDate": searchDate,
        "reservationOrderJson": json_str,
        "token": token
    }
    header["sign"] = get_sign_from_data(data, uri, timestamp)
    header["timestamp"] = timestamp
    return requests.post(f"{get_url(uri)}", data=data, headers=header)


def order_summit(spaceId, timeId, venueSpaceGroupId, venueSiteId, searchDate, token, phone, buddyIds, buddyNo,
                 captchaVerification):
    timestamp = get_timestamp()
    uri = "/api/reservation/order/submit"
    json_str = '[{'
    json_str += f'"spaceId":"{spaceId}","timeId":"{timeId}","venueSpaceGroupId":{venueSpaceGroupId}'
    json_str += '}]'
    data = {
        "venueSiteId": venueSiteId,
        "reservationDate": searchDate,
        "weekStartDate": searchDate,
        "reservationOrderJson": json_str,
        "token": token,
        "phone": phone,
        "buddyIds": buddyIds,
        "buddyNo": buddyNo,
        "isOfflineTicket": "1",
        "captchaVerification": captchaVerification
    }
    header["sign"] = get_sign_from_data(data, uri, timestamp)
    header["timestamp"] = timestamp
    return requests.post(f"{get_url(uri)}", data=data, headers=header)

def get_buddy_info():
    timestamp = get_timestamp()
    uri = "/api/buddies"
    data = {
        "page": "0",
        "size": "100",
        "nocache": timestamp
    }
    header["sign"] = get_sign_from_data(data, uri, timestamp)
    header["timestamp"] = timestamp
    return requests.get(
        f"{get_url(uri)}?page=0&size=100&nocache={timestamp}",
        headers=header)

def buddyid_to_userid(buddyInfo, buddyid) -> str:
    buddyData = buddyInfo.json()['data']['content']
    for item in buddyData:
        if str(item['id']) == buddyid:
            return str(item['userId'])
    return ""

def check_buddy_valid(buddyUserId, buddyRoleId, buddyNo) -> bool:
    timestamp = get_timestamp()
    uri = "/api/vip/check/buddy_no"
    data = {
        "buddyUserId": buddyUserId,
        "buddyRoleId": buddyRoleId,
        "buddyNo": buddyNo
    }
    header["sign"] = get_sign_from_data(data, uri, timestamp)
    header["timestamp"] = timestamp
    r = requests.post(f"{get_url(uri)}", data=data, headers=header)
    try:
        return r.json()['data']['checkResult']
    except:
        return False


def get_sign_from_data(data, uri, timestamp):
    fixed_str = "c640ca392cd45fb3a55b00a63a86c618"
    final_str = fixed_str + uri
    sorted_dict = dict(sorted(data.items()))
    for key, value in sorted_dict.items():
        final_str += key
        final_str += value
    final_str += timestamp
    final_str += ' '
    final_str += fixed_str
    hash_object = hashlib.md5(final_str.encode())
    hash_value = hash_object.hexdigest()
    return str(hash_value)


def get_captcha():
    timestamp = get_timestamp()
    uri = "/api/captcha/get"
    data = {
        "captchaType": "clickWord",
        "ts": timestamp,
        "nocache": timestamp
    }
    header["sign"] = get_sign_from_data(data, uri, timestamp)
    header["timestamp"] = timestamp
    return requests.get(
        f"{get_url(uri)}?captchaType=clickWord&ts={timestamp}&nocache={timestamp}",
        headers=header)


def check_captcha(pointJson, token):
    timestamp = get_timestamp()
    uri = "/api/captcha/check"
    data = {
        "captchaType": "clickWord",
        "pointJson": pointJson,
        "token": token,
    }
    header["sign"] = get_sign_from_data(data, uri, timestamp)
    header["timestamp"] = timestamp
    return requests.post(f"{get_url(uri)}", data=data, headers=header)


def get_timestamp():
    return str(int(time.time() * 1000))


def get_url(uri):
    root = "http://www.tyys.zju.edu.cn/venue-server"
    return root + uri


def get_aes_decode(info, key):
    if (key is None or key == ""):
        key = "XwKsGlMcdPMEhR1B"
    info = info.encode('utf-8')
    key = key.encode('utf-8')
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted = cipher.encrypt(pad(info, AES.block_size))
    return base64.b64encode(encrypted).decode()


def get_captcha_point(img, extra, token):
    request_url = "http://api.jfbym.com/api/YmServer/customApi"
    params = {"image": img,
              "type": "300010",
              "extra": extra,
              "token": token}
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    return requests.post(request_url, data=params, headers=headers)

def get_yunma_score() -> int:
    try:
        request_url = "http://api.jfbym.com/api/YmServer/getUserInfoApi"
        params = {"type": "score",
                  "token": captchaToken}
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        return int(requests.post(request_url, data=params, headers=headers).json()['data']['score'])
    except:
        print("获取云码平台积分失败")
        return 0


def get_json_point(coordinates_str):
    pairs = coordinates_str.split("|")
    coordinates = []

    for pair in pairs:
        x, y = pair.split(",")
        coordinate = {"x": int(x), "y": int(y)}
        coordinates.append(coordinate)

    output_str = ""
    for coordinate in coordinates:
        output_str += f'{{"x":{coordinate["x"]},"y":{coordinate["y"]}}},'

    output_str = "[" + output_str.rstrip(",") + "]"

    return output_str

def get_code_start_timestamp():
    current_time = datetime.now()
    time_str = codeStartTime
    target_time = datetime.strptime(time_str, "%H:%M").replace(year=current_time.year, month=current_time.month,
                                                               day=current_time.day)
    if current_time >= target_time:
        target_time = target_time + timedelta(days=1)
    timestamp = int(target_time.timestamp())

    return timestamp

def timestamp_to_date(timestamp):
    dt_object = datetime.fromtimestamp(timestamp)
    formatted_datetime = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_datetime
