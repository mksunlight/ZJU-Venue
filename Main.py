import time
import schedule
import WebUtils
from ConfigParams import codeStartTime
import Controller

def main():
    try:
        maxRetry = 5
        res = False
        for i in range(maxRetry):
            res = Controller.try_venue_space()
            if res:
                print("抢场地成功，请手动支付订单，有效期5分钟")
                break
        if not res:
            print("抢场地失败，请根据控制台输出定位问题")
    except:
        print("抢场地异常，请根据控制台输出定位问题")


if __name__ == '__main__':
    res = Controller.check_config_info()
    if res:
        print(f'程序准备就绪，运行时间：{WebUtils.timestamp_to_date(WebUtils.get_code_start_timestamp())}')
        try:
            schedule.every().day.at(codeStartTime).do(main)
            while True:
                schedule.run_pending()
                # print('当前时间: ', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                time.sleep(0.5)
        except Exception as e:
                print(e)

