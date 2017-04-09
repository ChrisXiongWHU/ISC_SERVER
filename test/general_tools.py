#coding:utf-8

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import chardet
from time import sleep



def receive_all(client):
    msgs = []
    c = ""
    while True:
        c = client.receive(json=False)
        if c is None:
            break
        msgs.append(c)
    return msgs

def send_websocket(dest,content,driver=None,handle=None):
    if driver is None:
        driver = webdriver.Chrome()
    if handle is None:
        driver.get('http://www.blue-zero.com/WebSocket/')
        handle = driver.current_window_handle

    #本机发送会增加消息数
    length1 = len(__get_messages(driver))
   
    input = driver.find_element_by_id("inp_url")
    connect = driver.find_element_by_id("btn_conn")
    close = driver.find_element_by_id("btn_close")
    input.clear()
    dest = "ws://%s" %dest
    input.send_keys(dest)
    connect.click()

    WebDriverWait(driver,5,1).until(lambda x:len(__get_messages(x))>length1)
  

    msgs = __get_messages(driver)
    new_msg = []
    for idx,msg in enumerate(msgs):
        if idx >= length1:
            new_msg.append(str(idx)+"   "+msg.text.split()[-1])
    
    driver.close()
    return driver,handle,new_msg


def __get_messages(driver):
        msg_divs = driver.find_element_by_id("div_msg")
        msgs = msg_divs.find_elements_by_tag_name("div")
        return msgs   

    




# driver,handle,new_msg = send_websocket("localhost:8000/api-123a/12345adf","")
# for msg in new_msg:
#     print msg





    

