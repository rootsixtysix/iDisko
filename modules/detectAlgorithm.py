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


import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib as mpl
import math
from matplotlib import cm
from sklearn import datasets
from scipy.stats import norm
from sklearn.naive_bayes import GaussianNB
#from debian.changelog import change
from _curses import BUTTON2_CLICKED
from skimage import filters
from multiprocessing import Process, Queue

from modules.geometrics import calculateDirectionAndWidth

import time
import skimage
from Crypto.SelfTest import SelfTestError




class SlopeDetection:
    """Klasse um die Steigungen zu suchen"""
    lastSlopes = []
    def __init__(self, c):
        self.c = c
    
    def averageStart(self):
        self.lastSlopes.clear()

    def calcAverage(self, val):
        if(len(self.lastSlopes) >= self.c.averageSlopeWidth):
            self.lastSlopes.pop(0)
        self.lastSlopes.append(val)
        if(len(self.lastSlopes) >= self.c.averageSlopeWidth):
            result = 0
            for tmpVal in self.lastSlopes:
                result += tmpVal
            tmpVal /= self.c.averageSlopeWidth
            return tmpVal
        else:
            return 0
        

    def checkSlopeUp(self, average):
        if((average > (self.c.slopeMinReference)) and (average < (self.c.slopeMaxReference))):
            return True
        else:
            return False
        
    def checkSlopeDown(self, average):
        if((average < (-self.c.slopeMinReference)) and (average > (-self.c.slopeMaxReference))):
            return True
        else:
            return False
        
    def checkBorderUp(self):
        return True
        if(len(self.lastSlopes) < self.c.averageSlopeWidth):
            return False
        if(#(lastSlopes[0] < lastSlopes[int(averageSlopeWidth/2)]) and 
           (self.lastSlopes[int(self.c.averageSlopeWidth/2)+1] < self.lastSlopes[int(self.c.averageSlopeWidth/2)])):
            return True
        else:
            return False
        
        
    def checkBorderDown(self):
        return True
        if(len(self.lastSlopes) < self.c.averageSlopeWidth):
            return False
        if(#(lastSlopes[0] > lastSlopes[int(averageSlopeWidth/2)]) and 
           (self.lastSlopes[int(self.c.averageSlopeWidth/2)+1] > self.lastSlopes[int(self.c.averageSlopeWidth/2)])):
            return True
        else:
            return False




def cleanBorders(sImg, c):
    #oben
    for iRow in range(0, int((c.averageSlopeWidth/2)+0.5)):
        for iCol in range(len(sImg[0])):
            sImg[iRow][iCol] = (0, 0, 1, 1)
    #unten        
    for iRow in range(len(sImg)-int((c.averageSlopeWidth/2)+0.5), len(sImg)):
        for iCol in range(len(sImg[0])):
            sImg[iRow][iCol] = (0, 0, 1, 1)
    #links        
    for iCol in range(0, int((c.averageSlopeWidth/2)+0.5)):
        for iRow in range(len(sImg)):
            sImg[iRow][iCol] = (0, 0, 1, 1)
    #rechts 
    for iCol in range(len(sImg[0])-int((c.averageSlopeWidth/2)+0.5), len(sImg[0])):
        for iRow in range(len(sImg)):
            sImg[iRow][iCol] = (0, 0, 1, 1)     
        
        
    return sImg


#Von links nach rechts
def runWtoE(sImg, resRGB, q, c):
    isInNerveTract = False
    nerveTractWidthCount = 0
    sd = SlopeDetection(c)
    for irow in range(len(sImg)):
        sd.averageStart()
        isInNerveTract = False
        for ival in range(int(c.averageSlopeWidth/2), len(sImg[irow])-1):
            div = sImg[irow][ival+1-int(c.averageSlopeWidth/2)] - sImg[irow][ival-int(c.averageSlopeWidth/2)]
            det = sd.calcAverage(div)
            if((not isInNerveTract) and     #nicht in der Nervenbahn
                sd.checkSlopeUp(det) and    #Steigung aufwaerz
                sd.checkBorderUp()):        #Kannte aufwaerz
                resRGB[irow][ival] = (0, 1, 0, 1)
                isInNerveTract = True
                nerveTractWidthCount = 0
            elif(isInNerveTract and
                sd.checkSlopeDown(det) and 
                sd.checkBorderDown()):
                resRGB[irow][ival] = (0, 1, 0, 1)
                isInNerveTract = False    
                #Breite eintragen
                tmp = ival-1
                while((resRGB[irow][tmp]==(1, 0, 0, 1)).all()):
                    resRGB[irow][tmp] = (nerveTractWidthCount*10, 0, 1, 1)
                    tmp -= 1
            elif(isInNerveTract==True):
                resRGB[irow][ival] = (1, 0, 0, 1)
                nerveTractWidthCount += 1
                tmp = ival
                if((nerveTractWidthCount > c.maxNerveTractWidth) or   #Maximale weite
                    (sImg[irow][ival] > c.maxBrightness) or            #Zu hell
                    (sImg[irow][ival] < c.minBrightness) or            #Zu dunkel
                    (ival == len(sImg[irow])-2)):                    #Rand
                    isInNerveTract = False
                    nerveTractWidthCount = 0
                    while((resRGB[irow][tmp]==(1, 0, 0, 1)).all()):
                        resRGB[irow][tmp] = (0, 0, 1, 1)
                        tmp -= 1
                    while((resRGB[irow][tmp]==(0, 1, 0, 1)).all()):
                        resRGB[irow][tmp] = (0, 0, 1, 1)
                        tmp -= 1
            else:
                resRGB[irow][ival] = (0, 0, 1, 1)
     
    q.put(cleanBorders(resRGB, c))
          
#Von oben nach unten  
def runNtoS(sImg, resRGB, q, c):
    isInNerveTract = False
    nerveTractWidthCount = 0
    sd = SlopeDetection(c)
    for icol in range(len(sImg[0])):
        sd.averageStart()
        isInNerveTract = False
        for ival in range(int(c.averageSlopeWidth/2), len(sImg)-1):
            div = sImg[ival+1-int(c.averageSlopeWidth/2)][icol] - sImg[ival-int(c.averageSlopeWidth/2)][icol]
            det = sd.calcAverage(div)
            if((not isInNerveTract) and
                sd.checkSlopeUp(det) and 
                sd.checkBorderUp()):
                resRGB[ival][icol] = (0, 1, 0, 1)
                isInNerveTract = True
                nerveTractWidthCount = 0
            elif(isInNerveTract and
                sd.checkSlopeDown(det) and 
                sd.checkBorderDown()):
                resRGB[ival][icol] = (0, 1, 0, 1)
                isInNerveTract = False     
                tmp = ival-1
                while((resRGB[tmp][icol]==(1, 0, 0, 1)).all()):
                    resRGB[tmp][icol] = (nerveTractWidthCount*10, 0, 1, 1)
                    tmp -= 1
            elif(isInNerveTract==True):
                resRGB[ival][icol] = (1, 0, 0, 1)
                nerveTractWidthCount += 1
                tmp = ival
                if((nerveTractWidthCount > c.maxNerveTractWidth) or   #Maximale weite
                   (sImg[ival][icol] > c.maxBrightness) or             #zu hell
                   (sImg[ival][icol] < c.minBrightness) or            #Zu dunkel
                   (ival == len(sImg)-2)):                           #Rand
                    isInNerveTract = False
                    nerveTractWidthCount = 0
                    while((resRGB[tmp][icol]==(1, 0, 0, 1)).all()):
                        resRGB[tmp][icol] = (0, 0, 1, 1)
                        tmp -= 1
                    while((resRGB[tmp][icol]==(0, 1, 0, 1)).all()):
                        resRGB[tmp][icol] = (0, 0, 1, 1)
                        tmp -= 1
            else:
                resRGB[ival][icol] = (0, 0, 1, 1)
    q.put(cleanBorders(resRGB, c))




#Von links oben nach rechts unten
#Starte unten links
def runNWtoSE(sImg, resRGB, q, c):
    isInNerveTract = False
    nerveTractWidthCount = 0
    sd = SlopeDetection(c)
    srow = len(sImg)-2 #startrow
    end = False
    icol = 0
    scol = 0
    while(end == False):
        if(srow >= 0):
            icol = 0
            irow = srow
            srow -= 1
        else:
            irow = 0
            icol = scol
            scol += 1
        sd.averageStart()
        isInNerveTract = False
        while((irow < len(sImg)-1) and (icol < len(sImg[0])-1)):
            div = sImg[irow+1-int(c.averageSlopeWidth/2)][icol+1-int(c.averageSlopeWidth/2)] - sImg[irow-int(c.averageSlopeWidth/2)][icol-int(c.averageSlopeWidth/2)]
            det = sd.calcAverage(div)
            if((not isInNerveTract) and
                sd.checkSlopeUp(det) and 
                sd.checkBorderUp()):
                resRGB[irow][icol] = (0, 1, 0, 1)
                isInNerveTract = True
                nerveTractWidthCount = 0
            elif(isInNerveTract and
                sd.checkSlopeDown(det) and 
                sd.checkBorderDown()):
                resRGB[irow][icol] = (0, 1, 0, 1)
                isInNerveTract = False     
                tmpIRow = irow-1
                tmpICol = icol-1
                while((resRGB[tmpIRow][tmpICol]==(1, 0, 0, 1)).all()):
                    resRGB[tmpIRow][tmpICol] = (int(nerveTractWidthCount*10), 0, 1, 1)
                    tmpIRow -= 1
                    tmpICol -= 1
            elif(isInNerveTract==True):
                resRGB[irow][icol] = (1, 0, 0, 1)
                nerveTractWidthCount += 1
                tmpIRow = irow
                tmpICol = icol
                if((nerveTractWidthCount > c.diagonalMaxNerveTractWidth) or    #Maximale Weite
                   (sImg[irow][icol] > c.maxBrightness) or                 #Zu hell
                   (sImg[irow][icol] < c.minBrightness) or            #Zu dunkel
                   ((irow == len(sImg)-2) or (icol == len(sImg[0])-2))):  #Rand (unten und rechts)                                              #Rand
                    isInNerveTract = False
                    nerveTractWidthCount = 0
                    while((resRGB[tmpIRow][tmpICol]==(1, 0, 0, 1)).all()):
                        resRGB[tmpIRow][tmpICol] = (0, 0, 1, 1)
                        tmpIRow -= 1
                        tmpICol -= 1
                    while((resRGB[tmpIRow][tmpICol]==(0, 1, 0, 1)).all()):
                        resRGB[tmpIRow][tmpICol] = (0, 0, 1, 1)
                        tmpIRow -= 1
                        tmpICol -= 1
            else:
                resRGB[irow][icol] = (0, 0, 1, 1)
            #nächstes Element
            irow += 1
            icol += 1
        #Oben rechts angekommen
        if((irow == 0) and (icol == len(sImg[0])-1)):
            end = True
     
    q.put(cleanBorders(resRGB, c))
        
#Von links unten nach rechts oben
#Starte oben links
def runSWtoNE(sImg, resRGB, q, c):
    isInNerveTract = False
    nerveTractWidthCount = 0
    sd = SlopeDetection(c)
    srow = 0
    end = False
    icol = 0
    scol = 0
    while(end == False):
        if(srow < len(sImg)-1-int(c.averageSlopeWidth/2)):
            icol = 0
            irow = srow
            srow += 1
        else:
            irow = srow
            icol = scol
            scol += 1
        sd.averageStart()
        isInNerveTract = False
        while((irow > int(c.averageSlopeWidth/2)) and (icol < len(sImg[0])-1)):
            div = sImg[irow-1+int(c.averageSlopeWidth/2)][icol+1-int(c.averageSlopeWidth/2)] - sImg[irow+int(c.averageSlopeWidth/2)][icol-int(c.averageSlopeWidth/2)]
            det = sd.calcAverage(div)
            if((not isInNerveTract) and
                sd.checkSlopeUp(det) and 
                sd.checkBorderUp()):
                resRGB[irow][icol] = (0, 1, 0, 1)
                isInNerveTract = True
                nerveTractWidthCount = 0
            elif(isInNerveTract and
                sd.checkSlopeDown(det) and 
                sd.checkBorderDown()):
                resRGB[irow][icol] = (0, 1, 0, 1)
                isInNerveTract = False  
                tmpIRow = irow+1
                tmpICol = icol-1
                while((resRGB[tmpIRow][tmpICol]==(1, 0, 0, 1)).all()):
                    resRGB[tmpIRow][tmpICol] = (int(nerveTractWidthCount*10), 0, 1, 1)
                    tmpIRow += 1
                    tmpICol -= 1
            elif(isInNerveTract==True):
                resRGB[irow][icol] = (1, 0, 0, 1)
                nerveTractWidthCount += 1
                tmpIRow = irow
                tmpICol = icol
                if((nerveTractWidthCount > c.diagonalMaxNerveTractWidth) or    #Maximale Weite
                   (sImg[irow][icol] > c.maxBrightness) or                 #zu hell
                   (sImg[irow][icol] < c.minBrightness) or            #Zu dunkel
                   ((irow == 1+int(c.averageSlopeWidth/2)) or (icol == len(sImg[0])-2))):           #Rand (oben und rechts)
                    isInNerveTract = False
                    nerveTractWidthCount = 0
                    while((resRGB[tmpIRow][tmpICol]==(1, 0, 0, 1)).all()):
                        resRGB[tmpIRow][tmpICol] = (0, 0, 1, 1)
                        tmpIRow += 1
                        tmpICol -= 1
                    while((resRGB[tmpIRow][tmpICol]==(0, 1, 0, 1)).all()):
                        resRGB[tmpIRow][tmpICol] = (0, 0, 1, 1)
                        tmpIRow += 1
                        tmpICol -= 1
            else:
                resRGB[irow][icol] = (0, 0, 1, 1)
            #nächstes Element
            irow -= 1
            icol += 1
        #Unten Rechts
        if((irow == len(sImg)-1-int(c.averageSlopeWidth/2)) and (icol == len(sImg[0])-1)):
            end = True

    q.put(cleanBorders(resRGB, c))
    

    
