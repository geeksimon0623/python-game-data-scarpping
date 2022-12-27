import time
import pytesseract
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1200x600')
driver = webdriver.Chrome('chromedriver.exe', options=options)

driver.get('https://baseattackforce.com/')
driver.execute_script("document.getElementById('loginname').value='your name';document.getElementById('your password').value='your password';ppdga();")
try:
    canvas = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "canvas")))
except:
    print("Not respond")
    exit()
pytesseract.pytesseract.tesseract_cmd = r'bin/tesseract.exe'
t=0
for no in range(11,1481):
    driver.execute_script("gotomap({0});".format(no))
    while True:
        time.sleep(1)
        t+=1
        if t > 10:
            t=0
            break
        png = driver.get_screenshot_as_png()
        im = Image.open(BytesIO(png))
        try:
            text = pytesseract.image_to_string(im.crop((1000,301,1100,320)))
        except:
            text = "no detection"
            pass
        print(no)
        print(text)
        if not "MAP{0}".format(no) in text:
            continue
        time.sleep(2)
        im = im.crop((900,0,1200,320))
        im.save('Maps/MAP{0}.png'.format(no))
        t=0
        break