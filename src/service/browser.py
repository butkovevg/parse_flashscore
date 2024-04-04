from selenium import webdriver


class BrowserService:
    @staticmethod
    def get_webdriver():
        """
        # from webdriver_manager.chrome import ChromeDriverManager
        # return webdriver.Chrome(executable_path=ChromeDriverManager().install())
        # https://sites.google.com/chromium.org/driver/downloads
        """
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        return webdriver.Chrome(options=options)
