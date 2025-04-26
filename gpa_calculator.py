import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# 给出所需的url
url_login_page = "https://jw.sdpei.edu.cn"
url_cjcx = "https://jw.sdpei.edu.cn/Student/MyMark.aspx"

# 启动Edge驱动，开始模拟
options = Options()
options.add_argument("--headless")  # 最大化窗口
options.add_argument("--disable-images")  # 禁用图片加载提高速度
options.add_experimental_option("detach", True)  # 保持浏览器打开

# 初始化浏览器
driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)
print("正在访问教务系统...")
driver.get(url_login_page)

# 自动输入账号密码
username = input("请输入学号: ")
password = input("请输入密码: ")

driver.find_element(By.ID, "txtUserName").send_keys(username)
driver.find_element(By.ID, "txtPassword").send_keys(password)

# 找到并点击登录按钮，实现登录
print("正在登录...")
login_button = driver.find_element(By.ID, "mlbActive")
actions = ActionChains(driver)
actions.key_down(Keys.CONTROL).click(login_button).key_up(Keys.CONTROL).perform()

# 等待新窗口打开
time.sleep(2)
driver.switch_to.window(driver.window_handles[-1])

# 直接访问成绩查询页面
print("正在访问成绩查询页面...")
driver.get(url_cjcx)

# 等待页面加载
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//tr[@onclick='changeSelectedLine(this)']"))
    )
    print("成绩数据加载成功！")
except Exception as e:
    print(f"等待页面加载时出错: {e}")

# 获取页面内容并解析
data = driver.page_source
soup = BeautifulSoup(data, 'html.parser')
trs = soup.find_all("tr", onclick="changeSelectedLine(this)")

# 初始化courses列表
courses = []

# 提取表格中的信息
for tr in trs:
    tds = tr.find_all("td")
    if len(tds) >= 7:  # 确保有足够的列
        course_info = {
            "课程号": tds[0].text.strip(),
            "课程名": tds[1].text.strip(),
            "课程学分": tds[2].text.strip(),
            "课序号": tds[3].text.strip(),
            "成绩": tds[4].text.strip(),
            "绩点": tds[5].text.strip(),
            "获得学分": tds[6].text.strip()
        }
        courses.append(course_info)

# 输出课程信息
print(f"\n共找到 {len(courses)} 门课程:")
for course in courses:
    print(f"{course['课程名']} - 成绩: {course['成绩']} 绩点: {course['绩点']}")

# 计算平均绩点
try:
    total_credit = 0
    total_gpa = 0
    for course in courses:
        credit = float(course['获得学分'])
        gpa = float(course['绩点']) if course['绩点'] else 0
        total_credit += credit
        total_gpa += credit * gpa

    if total_credit > 0:
        average_gpa = total_gpa / total_credit
        print(f"\n平均绩点: {average_gpa:.2f}")
except Exception as e:
    print(f"计算绩点时出错: {e}")