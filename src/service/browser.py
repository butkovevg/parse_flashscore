from selenium import webdriver


class BrowserService:
    @staticmethod
    def get_webdriver(is_headless: bool = True):
        """
        # from webdriver_manager.chrome import ChromeDriverManager
        # return webdriver.Chrome(executable_path=ChromeDriverManager().install())
        # https://sites.google.com/chromium.org/driver/downloads
        """
        options = webdriver.ChromeOptions()
        if is_headless:
            options.add_argument("--headless=new")
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        return webdriver.Chrome(options=options)
