from selenium import webdriver


class BrowserService:
    @staticmethod
    def get_webdriver():
        """
        # from webdriver_manager.chrome import ChromeDriverManager
        # return webdriver.Chrome(executable_path=ChromeDriverManager().install())
        # https://sites.google.com/chromium.org/driver/downloads
        """
        path_webdriver = r"C:\Users\evgeniy.butkov\PycharmProjects\parse_flashscore\src\configs\chromedriver.exe"
        return webdriver.Chrome()
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
#
# service = Service(executable_path='./chromedriver.exe')
# options = webdriver.ChromeOptions()
# driver = webdriver.Chrome(service=service, options=options)
# # ...
# driver.quit()