import time
import os, zipfile
from graphviz import Graph, Digraph
from collections import deque
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from IPython.core.display import Image
from multiprocessing import Process
from selenium.webdriver.common.keys import Keys
import pandas as pd
import lxml

class GraphScraper:
    def __init__(self):
        self.visited = set()
        self.BFSorder = []
        self.DFSorder = []

    def go(self, node):
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        self.visited.add(node)
        for child in self.go(node):
            if child not in self.visited:
                self.dfs_search(child)


    def bfs_search(self, node):
        todo = [node]
        while len(todo) > 0:
            curr = todo.pop(0)
            if not curr in self.visited:
                self.visited.add(curr)
            for child in self.go(curr):
                if not child in self.visited:
                    todo.append(child)
                    self.visited.add(child)
                    


class FileScraper(GraphScraper):
    def __init__(self):
        super().__init__()
        if not os.path.exists("Files"):
            with zipfile.ZipFile("files.zip") as zf:
                zf.extractall()

    def go(self, node):
        node_list = os.listdir('Files')
        for file_name in node_list:
            if file_name == f'{node}.txt':
                path = os.path.join('Files', file_name)
                with open(path,'r') as f:
                    node_info = f.read()
                    children = node_info.splitlines()[1]
                    BFS_info = node_info.splitlines()[2]
                    DFS_info = node_info.splitlines()[3]
                    BFS_list = BFS_info.split('BFS: ')
                    DFS_list = DFS_info.split('DFS: ')
                    child_list = children.split(' ')
                    self.BFSorder.append(BFS_list[1])
                    self.DFSorder.append(DFS_list[1])
                    return child_list

class WebScraper(GraphScraper):
    
    def	__init__(self, driver=None):
        super().__init__()
        self.driver = driver
        
        

    
    def go(self, url):
        page = self.driver.get(url)
        links = self.driver.find_elements_by_tag_name("a")
        children = [link.get_attribute("href") for link in links]
        bfs_btn = self.driver.find_element_by_id("BFS")
        bfs_btn.click()
        bfs_info = self.driver.find_element_by_id("BFS")
        self.BFSorder.append(bfs_info.text)
        dfs_btn = self.driver.find_element_by_id("DFS")
        dfs_btn.click()
        dfs_info = self.driver.find_element_by_id("DFS")
        self.DFSorder.append(dfs_info.text)
        return children
        

    def dfs_pass(self, start_url):
        self.visited.clear()
        self.DFSorder.clear()
        self.dfs_search(start_url)
        dpass = "".join(self.DFSorder)
        return dpass
        

    def bfs_pass(self, start_url):
        self.visited.clear()
        self.BFSorder.clear()
        self.bfs_search(start_url)
        bpass = "".join(self.BFSorder)
        return bpass

    
    def protected_df(self, url, password):
        page = self.driver.get(url)
        psswrd = self.driver.find_element_by_id("password-input")
        psswrd.send_keys(Keys.CONTROL + "a")
        psswrd.send_keys(Keys.BACKSPACE)
        psswrd.send_keys(password)
        go_btn = self.driver.find_element_by_id('attempt-button')
        go_btn.click()
        time.sleep(0.5)
        more_loc = self.driver.find_element_by_id('more-locations-button')
        more_loc.click()
        time.sleep(0.5)
        more_loc = self.driver.find_element_by_id('more-locations-button')
        more_loc.click()
        time.sleep(0.5)
        more_loc = self.driver.find_element_by_id('more-locations-button')
        more_loc.click()
        time.sleep(0.5)       
        df = pd.read_html(self.driver.page_source)
        return pd.concat(df)
        


     
