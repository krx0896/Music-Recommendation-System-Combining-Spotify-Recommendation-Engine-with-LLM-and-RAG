import sys
import os
import time
from datetime import datetime
from threading import Timer
from multiprocessing import Process, Queue

from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QVBoxLayout, QDateEdit, QSpinBox, QComboBox, QButtonGroup, QMainWindow, QTableView, QWidget, QTableWidget, QTableWidgetItem,QHeaderView,QFileDialog,QLabel
from PyQt5.QtCore import QThread, pyqtSignal, QObject, QDate, Qt, QTimer, QTime, QDateTime
from PyQt5.QtGui import QStandardItemModel
from PyQt5 import QtCore

from PyQt5 import uic

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QProgressDialog

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException
import keyboard
import requests
import json
import pyautogui
from bs4 import BeautifulSoup
from selenium.common.exceptions import StaleElementReferenceException
import json
import schedule
import threading
from threading import Timer

import time
import requests
import threading

import re

import csv


# Specify the path to the ChromeDriver executable
def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    # sys.exit(1)

# Back up the reference to the exceptionhook
sys._excepthook = sys.excepthook

# Set the exception hook to our wrapping function
sys.excepthook = my_exception_hook


options = Options()
options.add_experimental_option("detach", True) # 크롬 꺼짐 방지
options.add_experimental_option("prefs", {"profile.default_content_setting_values.notifications": 1})# 알림창 끄기
options.add_argument('disable-infobars')
options.add_experimental_option("excludeSwitches", ["enable-automation"]) # 자동화된 소프트웨어 문구 제거
# 비밀번호 저장 팝업을 끄기 위한 옵션 추가
prefs = {
    "profile.default_content_setting_values.notifications": 2,
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False
}
options.add_experimental_option("prefs", prefs)
service = Service(ChromeDriverManager().install()) #chromeDriver 자동 설치 및 업데이트


# UI 파일 경로 설정
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# UI 파일 로드
form = resource_path("lyrics_Google.ui")
form_class = uic.loadUiType(form)[0]
# .py 파일을 pyinstaller로 실행파일 만들고 생성된 spec file에 datas=[('lyrics_Google.ui', '.')], 수정하고 spec 파일로 실행파일 만들면 됨,  console=False, 콘솔창 안뜨게 spec 파일 수정

# 시그널 클래스
class WidgetSignals(QObject):

    input_1 = pyqtSignal(str)

# 첫 번째 쓰레드 클래스
class Thread1(QThread):
    def __init__(self, window_instance, driver):
        super().__init__()
        self.window_instance = window_instance
        self.stopped = False
        self.driver = driver

    def stop(self):
        self.stopped = True

    def run(self):

        print("Value from WindowClass in Thread1:", self.window_instance)

        self.driver = webdriver.Chrome(service=service, options=options)
        # JavaScript를 통해 WebDriver 탐지 방지
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
                })


        # CSV 파일 경로
        csv_file = self.window_instance.input_1.text()
        re_csv_file = f'lyrics_{self.window_instance.input_1.text()}'

        # 이미 처리된 track_id 확인
        processed_track_ids = set()
        try:
            with open(re_csv_file, newline='', encoding='utf-8-sig') as outfile:
                reader = csv.DictReader(outfile)
                processed_track_ids = {row['track_id'] for row in reader if row.get('track_id')}
        except FileNotFoundError:
            # 파일이 없을 경우 무시 (새 파일을 생성하는 경우)
            pass

        # 원본 CSV 파일 읽기 (ISO-8859-1로 인코딩 설정, 인코딩 오류 무시)
        with open(csv_file, newline='', encoding='ISO-8859-1', errors='replace') as infile:
            reader = csv.DictReader(infile)

            # 'lyrics' 열이 있는지 확인하고 없으면 추가
            fieldnames = reader.fieldnames
            if 'lyrics' not in fieldnames:
                fieldnames = list(fieldnames) + ['lyrics']

            for row in reader:
                track_id = row.get('track_id')

                # 이미 처리된 track_id는 건너뛰기
                if track_id in processed_track_ids:
                    self.window_instance.log.append(f"{datetime.now().strftime('%Y.%m.%d %H:%M:%S')} : Track ID {track_id} already processed, skipping.")
                    time.sleep(0.1)
                    continue

                artist = row['artists_pre']
                track_name = row['track_name']

                self.window_instance.log.append(f"{datetime.now().strftime('%Y.%m.%d %H:%M:%S')} : {artist} / {track_name}")
                time.sleep(0.1)

                # Musixmatch에서 가사 크롤링
                self.driver.get(f"https://www.google.com/")

                # 가사 검색
                element = wait(self.driver, 3).until(
                    EC.visibility_of_element_located((By.XPATH, '//textarea[@aria-label="검색"]'))
                )
                element.send_keys(artist + " " + track_name + " lyrics")
                element.send_keys(Keys.ENTER)

                try:
                    # 가사 요소 찾기
                    element = wait(self.driver, 3).until(
                        EC.visibility_of_element_located((By.XPATH, '//div[@data-attrid="kc:/music/recording_cluster:lyrics"]'))
                    )
                    lyrics = element.text.split('한국어로')[0]

                    self.window_instance.log.append(f"{datetime.now().strftime('%Y.%m.%d %H:%M:%S')} : 가사 크롤링 완료\n {lyrics}")
                    time.sleep(0.1)


                except Exception as e:
                    print(f"Error occurred: {e}")
                    self.window_instance.log.append(f"{datetime.now().strftime('%Y.%m.%d %H:%M:%S')} : Error occurred: {e}")
                    time.sleep(0.1)
                    lyrics = ""

                # 가사 값을 추가
                row['lyrics'] = lyrics

                # 업데이트된 행을 CSV에 바로바로 쓰기
                with open(re_csv_file, mode='a', newline='', encoding='utf-8-sig') as outfile:
                    writer = csv.DictWriter(outfile, fieldnames=fieldnames)

                    # 헤더는 처음 파일을 생성할 때만 기록
                    if outfile.tell() == 0:
                        writer.writeheader()

                    writer.writerow(row)

                print(f"Artist: {artist}, Track Name: {track_name}, Lyrics Updated")

                # 처리된 track_id를 기록
                processed_track_ids.add(track_id)

                # 너무 빠르게 요청하면 차단될 수 있으므로, 잠시 대기
                time.sleep(1)

            # WebDriver 종료
            self.driver.quit()


# 화면 클래스
class WindowClass(QDialog, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 시그널 객체 생성
        self.widget_signals = WidgetSignals()

        # 시스템 메뉴 아이콘
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        # 최소화 버튼   
        self.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
        # 최대화 버튼 
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        # 버튼에 기능을 연결하는 코드
        self.start_btn.clicked.connect(self.start_threads)

        self.excel_btn.clicked.connect(self.openFileDialog)

        # 텍스트가 변경될 때마다 자동으로 스크롤 하단으로 이동
        self.log.textChanged.connect(self.scroll_to_bottom)

        self.driver =  None

    def scroll_to_bottom(self):
        # 스크롤바의 값을 최대로 설정하여 하단으로 이동
        scrollbar = self.log.verticalScrollBar()
        
        # 현재 스크롤 위치와 최대 스크롤 위치를 저장
        current_value = scrollbar.value()
        max_value = scrollbar.maximum()
        
        # 스크롤바의 값을 최대로 설정
        scrollbar.setValue(max_value)
        
        # 스크롤 동작 후 UI가 업데이트될 시간을 줍니다.
        # 여기에서 sleep을 사용해 UI가 업데이트될 시간을 주도록 합니다.
        QThread.msleep(100)  # 0.1초 대기 (필요에 따라 조정 가능)

         # 100ms 후에 한 번 더 최대값으로 설정하여 스크롤이 완전히 내려가도록 함
        QTimer.singleShot(100, lambda: scrollbar.setValue(scrollbar.maximum()))

        # 현재 스크롤 위치로 다시 설정하여 지워지는 현상 방지
        scrollbar.setValue(current_value)


    def openFileDialog(self):
        global base_name, file_name
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose File", "", "All Files (*);;Text Files (*.txt)", options=options)

        if file_name:
            base_name = os.path.basename(file_name)  # 파일 경로에서 파일 이름만 추출

            # self.input_1.setText(file_name)  # 전체 경로
            self.input_1.setText(base_name)  # 파일 이름

            print("파일 이름:", base_name)
            print("파일 경로:", file_name)


    def on_spin_box_value_changed(self, value):
        self.spin_box_value = value
        print(self.spin_box_value)

    def start_threads(self):
        # 기존 스레드가 실행 중인지 확인하고 종료
        if hasattr(self, "thread1") and self.thread1.isRunning():
            if self.thread1.driver:
                self.thread1.driver.quit()
                print("기존 브라우저 종료")

            self.thread1.stop()
            self.thread1.wait()
            print("기존 쓰레드 종료")

        # 새로운 스레드 시작
        self.driver = None
        self.thread1 = Thread1(self, self.driver)
        self.thread1.start()

    def stop_threads(self):
        self.thread1.stop()
        # self.thread2.stop()

    #pyqt5 창닫힘 이벤트 추가
    def closeEvent(self, event):

        reply = QMessageBox.question(self, '확인', '프로그램을 종료하시겠습니까?',
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept() 

        else:
            event.ignore()

        try:
            self.thread1.driver.quit()
        except:
            pass


if __name__ == '__main__':

    app = QApplication(sys.argv)
    main_dialog = WindowClass()
    main_dialog.show()
    sys.exit(app.exec_())