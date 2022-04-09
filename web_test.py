import threading
from threading import Timer
import time

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.edge.service import Service


class Breakout:
    __i = 1

    def get_i(self):
        return self.__i

    def out(self):
        self.__i = 0


class dialogThread(threading.Thread):
    def __init__(self, page, breakout):
        super().__init__()
        self.page = page
        self.breakout = breakout

    def run(self):
        while self.breakout.get_i():
            WebDriverWait(self.page, 99 * 60, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'dialog-test'))
            )
            test = self.page.find_element(by=By.CLASS_NAME, value='dialog-test')
            if test.get_attribute("style").find("display: none") == -1:
                test.find_element_by_class_name('topic-item').click()
                test.find_element_by_class_name('btn').click()
                self.page.execute_script("if(document.getElementById('playButton')"
                                         ".getAttribute('class').includes('playButton')){"
                                         "document.getElementById('playButton').click()}")


class CountDown(threading.Thread):
    def __init__(self, breakout, sec):
        super().__init__()
        self.breakout = breakout
        self.sec = sec

    def run(self):
        time.sleep(self.sec)
        self.breakout.out()


def main(account, key):
    def get_courses(page):
        wait(EC.presence_of_element_located((By.CLASS_NAME, 'datalist')))
        time.sleep(1)
        return page.find_element(by=By.ID, value='sharingClassed').find_elements(by=By.CLASS_NAME, value="datalist")

    def play_video():
        time.sleep(2)
        op = "document.getElementsByClassName('volumeIcon')[0].click();" \
             "document.getElementsByClassName('speedTab15')[0].click();" \
             "document.getElementsByClassName('switchLine')[0].click();" \
             "setTimeout(function(){$('.videoArea').click()}, 1000);"
        driver.execute_script(op)

    def next_video():
        pause = "setTimeout(function(){$('.videoArea').click()}, 1500);"
        driver.execute_script(pause)
        time.sleep(1)
        op = "all = document.getElementsByClassName('video');" \
             "for(i = 0;i < all.length;i++){" \
             "if(all[i].getAttribute('class').includes('current_play')){" \
             "all[i+1].click();" \
             "break}}"
        driver.execute_script(op)

    def wait(element):
        time.sleep(1)
        while 1:
            try:
                WebDriverWait(driver, 20, 1).until(element)
                break
            except selenium.common.exceptions.TimeoutException:
                driver.refresh()

    options = webdriver.EdgeOptions()
    # options.add_experimental_option('excludeSwitches', ['enable-automation'])
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    # options.add_argument('--no-sandbox')

    s = Service(r"D:\Download\edgedriver\msedgedriver.exe")
    driver = webdriver.Edge(service=s)
    driver.set_window_size(860, 700)

    driver.get("https://passport.zhihuishu.com/login?service=https://onlineservice.zhihuishu.com/login/gologin")

    driver.find_element(by=By.XPATH, value='//*[@id="lUsername"]').send_keys(account)
    passwd = driver.find_element(by=By.XPATH, value='//*[@id="lPassword"]')
    passwd.send_keys(key)
    passwd.submit()

    print('loading')

    courses = get_courses(driver)

    count = 1
    while count < len(courses):
        allT = 0
        print("当前课程:", courses[count].find_element(by=By.CLASS_NAME, value='courseName').text)
        courses[count].find_element(by=By.CLASS_NAME, value='dd-in').click()

        out = Breakout()
        dialogT = dialogThread(driver, out)
        dialogT.start()
        countDown = CountDown(out, 17*60)
        if count == 1:
            countDown = CountDown(out, 7*60)

        countDown.start()

        while out.get_i():
            wait(EC.presence_of_element_located((By.ID, 'vjs_container_html5_api')))
            dialogs = driver.find_elements(by=By.CLASS_NAME, value='el-dialog__wrapper')
            for dialog in dialogs:
                if dialog.get_attribute("style").find("display: none") == -1:
                    dialog.find_element(by=By.CLASS_NAME, value='el-dialog__headerbtn').click()

            wait(EC.element_to_be_clickable((By.ID, 'playButton')))
            driver.execute_script("document.getElementsByClassName('dialog')[1].setAttribute('style','display: none')")
            videos = driver.find_element(by=By.CLASS_NAME, value="el-scrollbar__view")\
                .find_elements(by=By.CLASS_NAME, value="video")
            playing = 0
            for video in videos:
                if len(video.find_elements(by=By.CLASS_NAME, value='time_icofinish')) == 0:
                    driver.execute_script("document.getElementsByClassName('el-scrollbar__wrap')[0]"
                                          ".getElementsByClassName('video')[arguments[0]].click()", videos.index(video))
                    playing = video
                    break

            time.sleep(1)
            t0 = time.time()

            play_video()

            print("正在观看:", driver.find_element(by=By.CLASS_NAME, value='videotop_lesson_tit').text)

            WebDriverWait(playing, 15, 1).until(EC.presence_of_element_located((By.CLASS_NAME, 'progress-num')))
            time.sleep(1)
            percent = int(
                driver.execute_script("return document.getElementsByClassName('progress-num')[0].innerHTML")
                .replace('%', '')) * 0.01
            driver.execute_script("document.getElementsByClassName('controlsBar')[0].setAttribute("
                                  "'style','z-index: 2; overflow: inherit; display: block;')")
            bar = driver.find_element(by=By.CLASS_NAME, value='progressBar')
            x = int(bar.size.get('width') * percent)
            ActionChains(driver).move_to_element_with_offset(bar, x, 0).click().perform()

            while out.get_i():
                try:
                    WebDriverWait(playing, 30, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "time_icofinish")))
                except selenium.common.exceptions.TimeoutException:
                    continue
                next_video()
                break
            else:
                next_video()

            t = round(time.time() - t0)-3
            allT += t
            print("观看时间: ", str(round(t/60)) + ":" + str(round(t % 60)))

        driver.execute_script("$('.videoArea').click()")
        wait(EC.element_to_be_clickable((By.CLASS_NAME, 'back')))
        driver.find_element(by=By.CLASS_NAME, value='back').click()
        courses = get_courses(driver)
        count += 1
        print("课程时间:", str(round(allT/60)) + ":" + str(round(allT % 60)))

    driver.close()
    driver.quit()


