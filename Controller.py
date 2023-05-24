import base64
import json
import time
import WebUtils
from ConfigParams import *

def check_config_info() -> bool:
    buddyInfo = WebUtils.get_buddy_info()
    if buddyInfo.json()['code'] == 200:
        print(f"[√]同伴信息获取成功，可自行寻找同伴相关信息")
        print(f"-> {buddyInfo.text}")
    else:
        print(f"[×]同伴信息获取失败，{buddyInfo.json()['message']}")
        return False

    buddyUserId = WebUtils.buddyid_to_userid(buddyInfo, buddyIds)
    valid = WebUtils.check_buddy_valid(buddyUserId, "3", buddyNo)
    if valid:
        print("[√]同伴信息校验成功")
    else:
        print(f"[×]同伴信息校验失败")
        print("-> 请检查同伴码信息是否正确")
        return False

    score = WebUtils.get_yunma_score()
    if score >= 20:
        print(f"[√]云码平台校验成功，剩余积分{score}")
    else:
        print(f"[×]云码平台校验失败，剩余积分{score}")
        return False

    codeStartTimestamp = WebUtils.get_code_start_timestamp()
    codeStartDate = WebUtils.timestamp_to_date(codeStartTimestamp)

    header, payload, signature = cgAuthorization.split(".")
    decoded_payload = json.loads(base64.b64decode(payload + "==").decode("utf-8"))
    exp = decoded_payload['exp']
    if int(codeStartTimestamp) < int(exp):
        print("[√]登录信息校验成功")
    else:
        print(f"[×]登录信息校验失败")
        print(f"-> 登录信息失效时间：{WebUtils.timestamp_to_date(exp)}, 抢场地开始时间：{codeStartDate}, 请在抢场地时间前4小时内重新登陆")
        return False

    return True


def try_venue_space() -> bool:
    r1 = WebUtils.get_day_info(venueSiteId, searchDate)
    r1_res = r1.json()
    token = r1_res['data']['token']

    spaceTimeJson = r1_res['data']['spaceTimeInfo']
    timeIdList = []

    for begainTime in beginTimeList:
        for item in spaceTimeJson:
            if item["beginTime"] == begainTime:
                timeIdList.append(str(item["id"]))

    allSpaceJson = r1_res['data']['reservationDateSpaceInfo'][searchDate]

    pickTimeId = ""
    pickSpaceId = ""

    for timeId in timeIdList:
        if (pickTimeId != "" and pickSpaceId != ""):
            break
        for item in allSpaceJson:
            id = item['id']
            if item[timeId]["reservationStatus"] == 1:
                pickSpaceId = id
                pickTimeId = timeId
                break

    if (pickTimeId == "" or pickSpaceId == ""):
        print("抢场地失败，所选时段当前均无可用场地")
        return False

    time.sleep(0.5)

    r2 = WebUtils.get_order_info(pickSpaceId, pickTimeId, "null", venueSiteId, searchDate, token)
    print(r2.text)
    if r2.json()['code'] != 200:
        print("获取预订场地信息失败，请重试")
        return False

    time.sleep(0.5)
    captchaVerification = get_captchaVerification()

    if captchaVerification == "":
        print("验证码破解失败")
        return False

    r3 = WebUtils.order_summit(pickSpaceId, pickTimeId, "null", venueSiteId, searchDate, token, phone, buddyIds, buddyNo, captchaVerification)
    print(r3.text)
    if r3.json()['code'] != 200:
        return False
    return True

def get_captchaVerification() -> str:
    try:
        score = WebUtils.get_yunma_score()
        retry_num = min(2, score // 20)
        for i in range(retry_num):
            captchaVerification = crack_captcha()
            if captchaVerification != "":
                return captchaVerification
        return ""
    except:
        print("get_captchaVerification exception")
        return ""


def crack_captcha() -> str:
    try:
        captchaToken = config.get("captchaToken")
        r1 = WebUtils.get_captcha()
        print(r1.text)

        data = r1.json()['data']['repData']
        secretKey = data['secretKey']
        img = data['originalImageBase64']
        backToken = data['token']
        wordList = data['wordList']

        extra = ""
        for word in wordList:
            extra = extra + word + ","
        extra = extra[:-1]

        r2 = WebUtils.get_captcha_point(img, extra, captchaToken)
        print(r2.text)

        point = r2.json()['data']['data']
        point = WebUtils.get_json_point(point)
        pointJson = WebUtils.get_aes_decode(point, secretKey)

        r3 = WebUtils.check_captcha(pointJson, backToken)
        print(r3.text)
        if (r3.json()['data']['repCode']) == "0000":
            info = backToken + "---" + point
            return WebUtils.get_aes_decode(info, secretKey)
        return ""
    except:
        print("crack_captcha error")
        return ""
