import configparser

parser = configparser.ConfigParser()
parser.read("config.ini", encoding="UTF-8")
config = parser["config"]

cgAuthorization = config.get("cgAuthorization")
venueSiteId = config.get("venueSiteId")
searchDate = config.get("searchDate")
beginTimeList = config.get("beginTimeList").split(" ")
captchaToken = config.get("captchaToken")
phone = config.get("phone")
buddyIds = config.get("buddyIds")
buddyNo = config.get("buddyNo")
codeStartTime = config.get("codeStartTime")
