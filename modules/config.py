"""
 * Copyright (c) 2020 
 * Anna Heinrich <anna.heinrich@stud.htwk-leipzig.de>, 
 * Luka Mutschler <luka.mutschler@stud.htwk-leipzig.de>
 * Philipp Rimmele <philipp.rimmele@stud.htwk-leipzig.de>
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of HTWK Leipzig nor the names of its
 *    contributors may be used to endorse or promote products derived from
 *    this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
"""

import tkinter
from tkinter import messagebox
import math

import libxml2
from libxml2mod import xmlDocSetRootElement

class ConfigData:
    
    """
    Konfiguration für verschiedene Abschnitte.
    Einträge mit Namen und Default-Wert
    Kann nacher gleich verwendet werden wie wenn mit 
    class dd:
        averageSlopeWidth = 7
        slopeMinReference = 0.001
    ...
    erstellt wurden.
    Also z.B.
    myconfig = Config("config.xml")
    myconfig.save()
    print(myconfig.dd.slopeMinReference)
    """
    
    #Name, Defaultwert, type
    ddConfig = [["averageSlopeWidth", 7, "int"], 
                ["slopeMinReference", 0.001, "float"],
                ["slopeMaxReference", 0.0025, "float"],
                ["minBrightness", 0, "float"],
                ["maxBrightness", 1, "float"],
                ["maxNerveTractWidth", 20, "int"]]
    
    clusterConfig =  [["maxDirectionDiff", 0.6, "float"], 
                      ["widthOverlook", 2, "int"],
                      ["lengthOverlook", 2, "int"],
                      ["maxWidthExpansion", 2, "int"],
                      ["maxPosCorrection", 2, "int"],
                      ["circuitRange", 1, "int"],
                      ["neededInCircuit", 4, "int"]]
    
    mergeConfig =  [["maxDirectionDiff", 0.05, "float"], 
                    ["minOverlappingPixels", 5, "int"]]
    
    
    
    #Kueruel, Name, Eintraege
    configs = [["dd", "directionDetection", ddConfig],
               ["cluster", "clustering", clusterConfig],
               ["merge", "clusterMerge", mergeConfig]]
    
    
    def __init__(self, path):
        self.path = path
        try:
            #Versuchen Datei zu oeffnen
            self.doc = libxml2.parseFile(path)
        except:
            #Wenn oeffnen nicht geklappt hat, neue XML-Datei erstellen
            self.doc = libxml2.newDoc("1.0")
        #Konfiguration laden
        self.load()

        
    
    def load(self):
        ctxt = self.doc.xpathNewContext()
        
        #Config-Knoten suchen und ggf. erstellen
        self.configNode = next(iter(ctxt.xpathEval("/config")), None);
        if(self.configNode == None):
            self.configNode = libxml2.newNode("config")
            self.doc.setRootElement(self.configNode)
                

        #Alle Abschnitte durchgehen
        for iType in range(len(self.configs)):   
            #Abschnitt ins XML eintragen
            tmpNode = next(iter(self.configNode.xpathEval(self.configs[iType][1])), None)
            if(tmpNode == None):
                tmpNode = libxml2.newNode(self.configs[iType][1])
                self.configNode.addChild(tmpNode)
            #XML-Knoten im configs-Array merken
            self.configs[iType].append(tmpNode)
            
            #Objekt fuer die Unterdaten    
            tmpClass = type(self.configs[iType][0]+'C', (), {})
            setattr(self, self.configs[iType][0], tmpClass)
            self.configs[iType].append(tmpClass)
            #Name fuer den Abschnitt
            setattr(self, self.configs[iType][0]+"Name", self.configs[iType][1])
            #Alle Werte des Abschnitts
            for val in self.configs[iType][2]:
                readNodeName = val[0]
                tmpNode = next(iter(self.configs[iType][3].xpathEval(readNodeName)), None)  
                if(tmpNode == None):
                    #Erstelle knoten im XML und lade Defaultwert
                    tmpNode = libxml2.newNode(readNodeName)
                    self.configs[iType][3].addChild(tmpNode)
                    setattr(tmpClass, readNodeName, val[1])
                else:
                    #Lade Wert aus XML
                    if(val[2]=="int"):
                        setattr(tmpClass, readNodeName, int(tmpNode.content))
                    else:
                        setattr(tmpClass, readNodeName, float(tmpNode.content))
            
        #Werte die besonders berechnet werden müsssen
        self.dd.diagonalMaxNerveTractWidth = int(float(self.dd.maxNerveTractWidth)/math.sqrt(2))
    
    def save(self):
        #Alle Abschnitte
        for tempType in self.configs: 
            for val in tempType[2]:
                tmpNode = tempType[3].xpathEval(val[0])[0]
                tmpNode.setContent(str(getattr(tempType[4], val[0])))
            
        #Parameter fuer andere Programmteile hier ins XML...
        
        #Speichere XML-Datei
        self.doc.saveFormatFile(self.path, 1)
    
    
class ConfigGUI:
    def __init__(self, master, c):
        self.c = c
        self.master = master
        master.title("Config")

        self.master.grab_set()
        
        self.secNames = []
        self.secs = []
        myrow = 0
        self.changed = False
        
        for mysec in c.configs:
            self.secNames.append(tkinter.Label(master, text=mysec[1]).grid(row=myrow, column=1))
            myrow += 1
            entrys = []
            for myentry in mysec[2]:
                tmpLabel = tkinter.Label(master, text=myentry[0]).grid(row=myrow, column=0)
                tmpEntry = tkinter.Entry(master)
                tmpEntry.insert(10, getattr(mysec[4], myentry[0]))
                tmpEntry.grid(row=myrow, column=1)
                tmpArr = (tmpLabel, tmpEntry)
                myrow += 1
                entrys.append(tmpArr)
            self.secs.append(entrys)

        self.close_button = tkinter.Button(master, text="Cancel", command=master.destroy)
        self.close_button.grid(row=myrow, column=1)

        self.greet_button = tkinter.Button(master, text="Accept", command=self.acceptValues)
        self.greet_button.grid(row=myrow, column=0)
        
        self.master.wait_window()

    def acceptValues(self):
        try:
            for iSec in range(len(self.secs)):
                for iVal in range(len(self.secs[iSec])):
                    newVal = 0
                    oldVal = 0
                    if(self.c.configs[iSec][2][iVal][2] == "float"):        
                        newVal = float(self.secs[iSec][iVal][1].get())
                        oldVal = float(getattr(self.c.configs[iSec][4], self.c.configs[iSec][2][iVal][0]))
                    else:
                        newVal = int(self.secs[iSec][iVal][1].get())
                        oldVal = int(getattr(self.c.configs[iSec][4], self.c.configs[iSec][2][iVal][0])) 
                    if(newVal != oldVal):
                        self.changed = True
                        setattr(self.c.configs[iSec][4], self.c.configs[iSec][2][iVal][0], newVal)
            self.master.destroy()
        except:      
            messagebox.showerror(title="Invalid Value", message="Einer der eingegebenen Werte ist ungueltig!")

    def greet(self):
        print("Greetings!")
        