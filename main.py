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


import os
import time
from multiprocessing import Process, Queue
import matplotlib.image as mpimg
import matplotlib as mpl
import numpy as np
from skimage import io
from skimage.viewer import ImageViewer
from skimage import filters

from modules.preprocessing import preprocess_image
from modules.model import Pixel, createDataStructureForProcessedImage
from modules.detectAlgorithm import *
from modules.clustering import Cluster
from modules.utility import PixelPos, Statistics
from modules.classification import classificate, exportClusterData

from matplotlib.widgets import Button, TextBox

from modules.config import ConfigData, ConfigGUI

import random

import tkinter
import tkinter.ttk as TTK
from _ast import Or
try:
    from matplotlib.backends.backend_tkagg import (
        FigureCanvasTkAgg, NavigationToolbar2Tk)
except:
        from matplotlib.backends.backend_tkagg import (
        FigureCanvasTkAgg, NavigationToolbar2TkAgg)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from tkinter import IntVar
from xcffib.xproto import ExposeEvent
import copy
import sys


commandlineErrorMsg = \
"Fehlerhafter Aufruf!\n \
Korrekter Aufruf: python3 main.py inputFile [configFile]\n \
z.B.: python3 main.py images/Test/part.tif\n"

"""
Kommandozeilenparameter lesen
"""
if(len(sys.argv) < 2 or len(sys.argv) > 3):
    print(commandlineErrorMsg)
    sys.exit(2)

imagePath = sys.argv[1]
configPath = "config.xml"
if(len(sys.argv) == 3):
    configPath = sys.argv[2]

"""
Konfigurationswerte
"""
myconfig = ConfigData(configPath)
myconfig.save()


"""
open image
"""
img = mpimg.imread(imagePath)
#img = mpimg.imread('part180.tif')
#image = io.imread(IMAGEPATH+FILENAME, as_gray=True)

"""
preprocess image
"""
#preprocessedImage = preprocess_image(image)
img = filters.gaussian(img)

"""
Create RGBA-Images for editing and viewing
"""
mycolormap = cm.get_cmap()
norm = mpl.colors.Normalize()
norm.autoscale_None(img)
rgbaWtoO = mycolormap(norm(img))
rgbaNtoS = rgbaWtoO.copy()
rgbaNWtoSO = rgbaWtoO.copy()
rgbaSWtoNO = rgbaWtoO.copy()
rgbaDirection = rgbaWtoO.copy()
rgbaWidth = rgbaWtoO.copy()
allDirections = rgbaWtoO.copy()
resultImg = rgbaWtoO.copy()
clusterImg = rgbaWtoO.copy()
crossingsImg = rgbaWtoO.copy()


"""
Geht das Bild 4mal in unterschiedlichen Richtungen durch um die Richtungen der Nervenbahnen zu ermitteln
Dies läuft ggf. Paralell auf bis zu 4 Prozessorkernen
"""
def doDirectionRuns():
    global rgbaWtoO
    global rgbaNtoS
    global rgbaNWtoSO
    global rgbaSWtoNO

    qWtoE = Queue()
    qNtoS = Queue()
    qNWtoSE = Queue()
    qSWtoNE = Queue()
    threadWtoE = Process(target=runWtoE, args=(img, rgbaWtoO, qWtoE, myconfig.dd))
    threadNtoS = Process(target=runNtoS, args=(img, rgbaNtoS, qNtoS, myconfig.dd))
    threadNWtoSE = Process(target=runNWtoSE, args=(img, rgbaNWtoSO, qNWtoSE, myconfig.dd))
    threadSWtoNE = Process(target=runSWtoNE, args=(img, rgbaSWtoNO, qSWtoNE, myconfig.dd))

    threadWtoE.start()
    threadNtoS.start()
    threadNWtoSE.start()
    threadSWtoNE.start()

    rgbaWtoO = qWtoE.get()
    rgbaNtoS = qNtoS.get()
    rgbaNWtoSO = qNWtoSE.get()
    rgbaSWtoNO = qSWtoNE.get()

    threadWtoE.join()
    threadNtoS.join()
    threadNWtoSE.join()
    threadSWtoNE.join()



"""
Berechnet aus den 4 Einzelbildern ein Bild mit den entsprechenden Richtungen
und eine mit den entsprechenden Breiten
"""
def calcDirections():
    (width, height, colors) = rgbaWtoO.shape
    global processedImage
    global rgbaDirection
    rgbaDirection = mycolormap(norm(img))
    processedImage = createDataStructureForProcessedImage(width, height)
    for irow in range(len(rgbaDirection)):
        for ival in range(len(rgbaDirection[irow])):
            pixel = Pixel()
            count = 0
            if(rgbaWtoO[irow][ival][0] != 0):
                count += 1
            if(rgbaNtoS[irow][ival][0] != 0):
                count += 1
            if(rgbaNWtoSO[irow][ival][0] != 0):
                count += 1
            if(rgbaSWtoNO[irow][ival][0] != 0):
                count += 1
            mylist = [rgbaWtoO[irow][ival][0],
                      rgbaNtoS[irow][ival][0],
                      rgbaNWtoSO[irow][ival][0],
                      rgbaSWtoNO[irow][ival][0]]
            mylist.sort()
            #print(mylist)
            allDirections[irow][ival] = (rgbaWtoO[irow][ival][0], rgbaNtoS[irow][ival][0], rgbaNWtoSO[irow][ival][0]+rgbaSWtoNO[irow][ival][0], 1)
            (width, direction) = calculateDirectionAndWidth(rgbaWtoO[irow][ival][0]/10,
                                            rgbaSWtoNO[irow][ival][0]/10,
                                            rgbaNtoS[irow][ival][0]/10,
                                            rgbaNWtoSO[irow][ival][0]/10)
            if(width == 0):
                rgbaDirection[irow][ival] = [0, 0, 1, 1]
                rgbaWidth[irow][ival] = [0, 0, 1, 1]

            else:
                #rgbaDirection[irow][ival] = [int(direction*180/math.pi), 0, 0, 1]
                rgbaDirection[irow][ival] = [direction/math.pi, 0, 0, 1]
                if(irow==88 and ival==78):
                    print(direction/math.pi)
                    print(width)
                rgbaWidth[irow][ival] = [width, 0, 0, 1]
                processedImage[irow][ival].probablyInNerveTract = True
                processedImage[irow][ival].width = width
                processedImage[irow][ival].direction = direction



"""
Sucht Cluster die Nervenbahnen repräsentieren könnten
"""
def findClusters(directionImg, widthImg, resImg):
    global clusters
    clusters = []
    for irow in range(len(rgbaDirection)):
        for ival in range(len(rgbaDirection[irow])):
            #ist noch nicht in block und hat breite
            if(resImg[irow][ival][1] == 0 and rgbaWidth[irow][ival][0] != 0):
                tmpCluster = Cluster(img, directionImg, widthImg, resImg, (random.randint(1, 255), random.randint(1, 255), random.randint(1, 255), 1), myconfig.cluster)
                tmpPos = PixelPos(ival, irow)
                tmpCluster.findCluster(tmpPos)
                if (len(tmpCluster.clusterPixels) > 100 ):
                    clusters.append(tmpCluster)



def mergeClusters(clusters):
    for cluster in clusters:
        for cluster2 in clusters:
            pix1 = cluster.clusterPixels
            pix2 = cluster2.clusterPixels
            if(pix1 != pix2):
                samePixels = list(set(pix1).intersection(pix2))
                if(len(samePixels) > myconfig.merge.minOverlappingPixels and 
                   ((cluster.dirStat.avg - myconfig.merge.maxDirectionDiff) < cluster2.dirStat.avg and 
                   (cluster.dirStat.avg + myconfig.merge.maxDirectionDiff) > cluster2.dirStat.avg)):
                    print("c1="+str(cluster.dirStat.avg)+" c2="+str(cluster2.dirStat.avg))
                    cluster.clusterPixels = cluster.clusterPixels + cluster2.clusterPixels
                    cluster.clusterPixels = list(set(cluster.clusterPixels))
                    clusters.remove(cluster2)
    return clusters


def drawRect(targetImg, pos):
    for i in range(pos.xPos-7, pos.xPos+7):
        for j in range(pos.yPos-7, pos.yPos+7):
            if((targetImg[j][i] == (1,0,0,1)).all()):
                return
    for i in range(pos.xPos-7, pos.xPos+7):
        for j in range(pos.yPos-7, pos.yPos+7):
            targetImg[j][i] = (1,0,0,1)
            
            
def findCrossings(clusters, resImg):
    for cluster in clusters:
        for cluster2 in clusters:
            pix1 = cluster.clusterPixels
            pix2 = cluster2.clusterPixels
            if(pix1 != pix2):
                samePixels = list(set(pix1).intersection(pix2))
                if(len(samePixels) >= 1):
                    print("c1="+str(cluster.dirStat.avg)+" c2="+str(cluster2.dirStat.avg))
                    drawRect(resImg, samePixels[0])
    return clusters

#Richtungsbilder erstellen
doDirectionRuns()
#Aus den 4 einzelbildern ein Bild mit den Richtungen berechnen
calcDirections()
#Cluster suchen
clusterImg = rgbaDirection.copy()
findClusters(rgbaDirection, rgbaWidth, clusterImg)

"""
Klassifizierung
"""
nerveTractIndices = [0, 1, 3, 13, 14, 15]    #for part.tif
nerveTractIndices = [4, 6, 16, 17, 19, 20, 24, 27, 28, 29, 30, 31, 44, 46]    #for part3.tif 26
#exportClusterData(clusters, nerveTractIndices)

#Klassifizierung
algorithm = 'svm'  #'svm'-> SVM, 'gnb'->Naive Bayes
attributes = (2,6,8,12)  #Attribute Selection
filelist = ['/v4/part', '/v4/part2']
masszahlCalculation = False
nerveTracts = classificate(clusters, resultImg, algorithm, attributes, filelist, masszahlCalculation)


nerveTracts = mergeClusters(nerveTracts)
for cluster in nerveTracts:
    cluster.colorizeInRgbaImg(resultImg)
    
crossingsImg = resultImg.copy()
findCrossings(nerveTracts, crossingsImg)

"""
GUI Handling
"""
class MyPanel:
    def __init__(self, master):
        self.master = master

        self.imageSelections = [
                        ("WtoE", 1, 1),
                        ("NtoS", 2, 0),
                        ("SWtoNE", 3, 0),
                        ("NWtoSE", 4, 0),
                        ("allDir", 5, 0),
                        ("Directions", 6, 1),
                        ("Widths", 7, 0),
                        ("Clusters", 8, 0),
                        ("orig", 9, 0),
                        ("result", 10, 0),
                        ("crossings", 11, 0),
                        ("singleCluster", 12, 1),
                        ]

        self.selectVar = tkinter.IntVar(self.master)
        self.selectVar.set(7)

        optionButton = tkinter.Button(master, text="config", command=self.showConfig)
        optionButton.pack(side = tkinter.LEFT)
        for txt, val, nextframe in self.imageSelections:
            if(nextframe == 1):
                frame = tkinter.Frame(master)
                frame.pack(side = tkinter.LEFT)
            tmpButton = tkinter.Radiobutton(frame,
                        text=txt,
                        padx = 20,
                        variable=self.selectVar,
                        command=self.redraw,
                        value=val)

            tmpButton.pack(anchor=tkinter.W, side = tkinter.BOTTOM)



        #Combobox erstellen
        self.cbClusters = TTK.Combobox(frame, textvariable="Cluster")
        self.cbClusters.pack(anchor=tkinter.W, side = tkinter.BOTTOM)
        self.cbClusters.bind("<<ComboboxSelected>>", self.cbClustersCallback)
        self.cbClustersUpdate()


    def cbClustersCallback(self, event):
        self.redraw()

    def cbClustersUpdate(self):
        #Werte für Combobox erstellen
        cbClustersEntrys=[]
        for i in range(len(clusters)):
            cbClustersEntrys.append(i)
            self.cbClusters['values'] = cbClustersEntrys

        if(len(clusters) != 0):
            self.cbClusters.current(0)

    def showConfig(self):
        cGUI = ConfigGUI(tkinter.Toplevel(self.master), myconfig)
        if(cGUI.changed):
            myconfig.save()
            doDirectionRuns()
            calcDirections()
            global clusterImg
            clusterImg = rgbaDirection.copy()
            global resultImg
            resultImg = mycolormap(norm(img))
            findClusters(rgbaDirection, rgbaWidth, clusterImg)
            global nerveTracts
            nerveTracts = classificate(clusters, resultImg, algorithm, attributes, filelist, masszahlCalculation)
            nerveTracts = mergeClusters(nerveTracts)
            for cluster in nerveTracts:
                cluster.colorizeInRgbaImg(resultImg)
            
            global crossingsImg  
            crossingsImg = resultImg.copy()
            findCrossings(nerveTracts, crossingsImg)
            self.cbClustersUpdate()
            self.redraw()

    def redraw(self):
        val = self.selectVar.get()
        fig.clear()
        if(val == 1):
            fig.add_subplot(111).imshow(rgbaWtoO)
        elif(val == 2):
            fig.add_subplot(111).imshow(rgbaNtoS)
        elif(val == 3):
            fig.add_subplot(111).imshow(rgbaSWtoNO)
        elif(val == 4):
            fig.add_subplot(111).imshow(rgbaNWtoSO)
        elif(val == 5):
            fig.add_subplot(111).imshow(allDirections)
        elif(val == 6):
            fig.add_subplot(111).imshow(rgbaDirection)
        elif(val == 7):
            fig.add_subplot(111).imshow(rgbaWidth)
        elif(val == 8):
            fig.add_subplot(111).imshow((clusterImg*255).astype('uint8'))
        elif(val == 9):
            fig.add_subplot(111).imshow(img)
        elif(val == 10):
            fig.add_subplot(111).imshow((resultImg*255).astype('uint8'))
        elif(val == 11):
            fig.add_subplot(111).imshow(crossingsImg)
        elif(val == 12):
            #singleBlockImg = mycolormap(norm(img))
            singleBlockImg = rgbaDirection.copy()
            clusters[int(self.cbClusters.get())].colorizeInRgbaImg(singleBlockImg)
            startPos = clusters[int(self.cbClusters.get())].startPos
            endPos = clusters[int(self.cbClusters.get())].endPos
            tmpCluster = clusters[int(self.cbClusters.get())]
            print("bright: avg="+str(tmpCluster.brightStat.avg)+" var="+str(tmpCluster.brightStat.variance))
            print("startpos: x="+str(startPos.xPos)+" y="+str(startPos.yPos)+" endpos: x="+str(endPos.xPos)+" y="+str(endPos.yPos))
            fig.add_subplot(111).imshow((singleBlockImg*255).astype('uint8'))
        canvas.draw()

root = tkinter.Tk()
root.wm_title("Embedding in Tk")

fig = Figure(figsize=(5, 4), dpi=150)
t = np.arange(0, 3, .01)
#fig.add_subplot(111).imshow(rgbaWidth)


#Infos aus: https://matplotlib.org/3.1.0/gallery/user_interfaces/embedding_in_tk_sgskip.html

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

try:
    toolbar = NavigationToolbar2Tk(canvas, root)
except:
    toolbar = NavigationToolbar2TkAgg(canvas, root)
toolbar.update()

panel = MyPanel(root)
panel.redraw()




def on_key_press(event):
    print("you pressed {}".format(event.key))
    key_press_handler(event, canvas, toolbar)


canvas.mpl_connect("key_press_event", on_key_press)

def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

root.protocol("WM_DELETE_WINDOW", _quit)

tkinter.mainloop()

"""
show image
(for test purpose only)
"""
#plt.title("Bild und so")
#plt.show()
#viewer = ImageViewer(processed_image)
#viewer.show()
