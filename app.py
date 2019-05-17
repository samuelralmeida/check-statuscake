#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
import requests
import json
import time
import webbrowser
import config

class Application:
    def __init__(self, master):
        self.master = master
        self.master.wm_attributes('-type', 'splash')
        self.master.geometry("+{}+{}".format(config.x_position, config.y_position))
        self.master.attributes('-topmost', 'true')
        # self.master.resizable(True, True)
        # self.master.update_idletasks()
        # self.master.overrideredirect(True)
        
        # data
        self.paused = 0
        self.up = 0
        self.down = 0
        self.down_checks = []
        self.button_list = []
        
        # labels
        self.labelPaused = tk.Label(master, text="")
        self.labelUp = tk.Label(master, text="")
        self.labelDown = tk.Label(master, text="")
        self.buttonDown = tk.Button(master, text="", command=self.toggle_downs)
        self.buttonExit = tk.Button(master, text="Sair", command=master.destroy).grid(row=0, column=0)

        self.visible = False
        self.makeAnalysis()

    def makeAnalysis(self):
        self.resetData()
        results = self.getData()
        self.checkData(results)
        self.buildStatus()
        self.printDowns()
        
        self.master.after(config.time_ms_request, self.makeAnalysis)
        
    def resetData(self):
        self.up = 0
        self.down = 0
        self.down_checks = []
        self.hide_button()
        self.button_list = []
    
    def getData(self):
        URL = config.url_request
        API_KEY = config.api_key
        USERNAME = config.username
        HEADER = {"User-Agent": "teste", "API": API_KEY, "Username": USERNAME}
        r = requests.get(URL, headers=HEADER)
        return json.loads(r.content)
    
    def checkData(self, results):
        for result in results:
            if result["Paused"] or len(set(config.teams).intersection(result["ContactGroup"])) == 0:
                continue
            
            if result["Status"] == "Up":
                self.up += 1
                continue
            
            if result["Status"] == "Down":
                self.down_checks.append(result)
                self.down += 1
                continue

    def buildStatus(self):      
        self.labelUp.configure(text="▲ {} ".format(self.up))
        self.labelUp.grid(row=0, column=1)

        self.labelDown.grid_forget()
        self.buttonDown.grid_forget()

        if self.down > 0:
            self.buttonDown.configure(text="▼ {}".format(self.down))
            self.buttonDown.grid(row=0, column=2)
        else:
            self.labelDown.configure(text="▼ {} ".format(self.down))
            self.labelDown.grid(row=0, column=2)

    def printDowns(self):
        if len(self.down_checks) > 0:
            for check in self.down_checks:               
                button = tk.Button(
                    self.master,
                    text=check["WebsiteName"].encode('raw_unicode_escape').decode('utf-8'),
                    command=lambda testID=check["TestID"]: self.open_link(testID)
                )
                self.button_list.append(button)
            if self.visible:
                self.show_button()
    
    def toggle_downs(self):
        count = 1
        if self.visible:
            self.hide_button()
            self.visible = False
        else:
            self.show_button()
            self.visible = True
    
    def hide_button(self):
        for button in self.button_list:
            button.grid_forget()
    
    def show_button(self):
        count = 1
        for button in self.button_list:
            button.grid(row=count, columnspan=3, sticky='nesw')
            count += 1

    def open_link(self, testID):
        url = "https://app.statuscake.com/AllStatus.php?tid={}".format(testID)
        webbrowser.open_new_tab(url)

root = tk.Tk()
window = Application(root)
root.mainloop()
