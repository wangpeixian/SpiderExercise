import re
from selenium import webdriver
from pyquery import PyQuery as pq


browser = webdriver.Chrome()

def search_content(keyword="男装"):
    browser.get("https://login.taobao.com/member/login.jhtml")  # 进入登陆页面
    browser.implicitly_wait(5)
    browser.find_element_by_id("J_Quick2Static").click()  # 点击用密码登陆
    browser.find_element_by_class_name("weibo-login").click()  # 点击用微博登陆
    browser.implicitly_wait(5)
    browser.find_element_by_name("username").send_keys("your username")  # 在这里输入你的微博用户名
    browser.find_element_by_name("password").send_keys("your password")  # 在这里输入你微博密码
    browser.find_element_by_class_name("W_btn_g").click()  # 登陆
    browser.implicitly_wait(5)
    browser.find_element_by_id("q").clear()  # 清空搜索框中内容
    browser.find_element_by_id("q").send_keys("男装")  # 搜索栏中填入文字
    browser.find_element_by_class_name("btn-search").click()  # 点击搜索

def total_page():
    """
    :return: 获取总页数
    """
    page_total = browser.find_element_by_class_name("total").text  # 总页数
    page_total = re.compile('(\d+)').search(page_total).group(1)
    return int(page_total)

def next_page(page):
    browser.find_element_by_class_name("J_Input").clear()
    browser.find_element_by_class_name("J_Input").send_keys(page)  # 填入新的页数
    browser.find_element_by_class_name("J_Submit").click()  # 点击翻页

def main():
    search_content()
    pages = total_page()

    for page in range(2, pages+1):
        html = browser.page_source
        doc = pq(html)
        products = doc(".J_MouserOnverReq").items()
        print(products)
        for item in products:
            product = {
                "image": item.find(".pic .img").attr("src"),
                "price": item.find(".price").text()[3:],
                "title": item.find(".title").text(),
            }
            print(product)
        next_page(page)
    browser.close()

if __name__ == '__main__':
    main()


