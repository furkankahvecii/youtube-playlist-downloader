from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException 

import time
import re

'''
    CSS selectors perform far better than Xpath and it is well documented in Selenium community.
    https://stackoverflow.com/questions/16788310/what-is-the-difference-between-cssselector-xpath-and-which-is-better-with-resp
'''
class YoutubeLocators(object):
    ALL_LIST = (By.XPATH,'/html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/ytd-playlist-video-list-renderer/div[3]//ytd-playlist-video-renderer')
    EACH_VIDEO = (By.CSS_SELECTOR,'#content > a')
    ISSET_DOWNLOAD = (By.CSS_SELECTOR, '#buttons')
    COUNT_VIDEO = (By.CSS_SELECTOR,'#stats > yt-formatted-string:nth-child(1)')
    VIDEO_TITLE = (By.CSS_SELECTOR, '#title')

class DownloadLocators(object):
    PRIVATE_ERROR = (By.XPATH, '//*[@id="container"]/yt-formatted-string')
    LINK_INPUT = (By.CSS_SELECTOR,'#input')
    SUBMIT_INPUT = (By.CSS_SELECTOR,'#submit')
    DOWNLOAD = (By.CSS_SELECTOR,'#buttons > a:nth-child(1)')
    ERROR_MESSAGE = (By.CSS_SELECTOR, '#error')

class YoutubePlaylistDownload():
    def __init__(self, driver, url, start = 0):
        self.driver = driver
        self.links = {}
        self.url = url
        self.start = start
        self.get_videos()

    def control_url(self):
        try:
            self.driver.get(self.url)
            return self.driver.current_url != "https://www.youtube.com/oops" if True else False
        except:
            return False

    def get_videos(self):
        self.driver.implicitly_wait(3)
        assert self.control_url(), "Invalid url!"
        assert self.driver.find_element(*DownloadLocators().PRIVATE_ERROR).get_attribute('innerHTML') != "This playlist is private.", "Playlist is private."

        playlist_video_count = re.search(r'\d+', self.driver.find_element(*YoutubeLocators().COUNT_VIDEO).get_attribute('innerHTML')).group(0)
        for i in range(0,int(int(playlist_video_count) / 100)):
            self.driver.maximize_window()
            self.driver.execute_script("var scrollingElement = (document.scrollingElement || document.body);scrollingElement.scrollTop = scrollingElement.scrollHeight;")  
            time.sleep(3) 

        self.check_private_delete()
        self.download_all()

    def check_private_delete(self):
        all_videos = self.calculate_start_video()
        for video in all_videos:
            video_title = video.find_element_by_css_selector('#video-title').get_attribute('innerHTML').strip() # strip == trim
            if video_title != '[Deleted video]' and video_title != '[Private video]' :
                self.links[video.find_element(*YoutubeLocators().EACH_VIDEO).get_attribute('href')] = None

    def calculate_start_video(self):
        all_videos = self.driver.find_elements(*YoutubeLocators().ALL_LIST)
        if(len(all_videos) > self.start and self.start >= 0):
            del all_videos[0:self.start]
        return all_videos

    def download_all(self):
        assert len(self.links) != 0 , "Not found video that downloadable"
        print(str(len(self.links)) + " videos will be converted to mp3 format.\nDownload begins.")

        for link in self.links:
            self.links[link] = self.download(link) if True else None

        print("\nTrying to download videos that cannot be downloaded.")
        for link in filter(lambda i: self.links[i] == False, self.links):
            self.links[link] = self.download(link) if True else False
        
        self.success_print()
    
    def download(self,link):
        try:
            self.driver.get("https://ytmp3.cc/en13/")
            self.driver.find_element(*DownloadLocators  ().LINK_INPUT).send_keys(link)
            self.driver.find_element(*DownloadLocators().SUBMIT_INPUT).click()
            time.sleep(2)
        except:
            print(link + " download failed.")
            return False

        while True:
            if self.check_exists_element(DownloadLocators().ERROR_MESSAGE):
                print(link + " download failed.")
                return False
            elif self.driver.find_element(*YoutubeLocators().ISSET_DOWNLOAD).get_attribute('style') == "display: block;":
                self.driver.implicitly_wait(1)
                self.driver.execute_script("arguments[0].click();",self.driver.find_element(*DownloadLocators().DOWNLOAD))
                print(self.driver.find_element(*YoutubeLocators().VIDEO_TITLE).get_attribute('innerHTML') + " download successfull.")         
                break

        time.sleep(2)
        return True

    def check_exists_element(self, element):
        try:
            self.driver.find_element(*element)
        except NoSuchElementException:
            return False
        return True
    
    def success_print(self):
        success_download_count = len([x for x in self.links if self.links[x] == True])
        print ("\n" + str(success_download_count) + " of the " + str(len(self.links)) + " videos on the playlist have been successfully downloaded.")


url = input("Enter your playlist url: ")
brow = webdriver.Chrome(executable_path="C:/Users/Furkan Kahveci/Desktop/deneme/alzare/chromedriver.exe")
start = 0

instance = YoutubePlaylistDownload(brow, url, start)