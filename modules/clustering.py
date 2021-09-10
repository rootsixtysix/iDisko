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

from modules.utility import PixelPos, Statistics
import copy
import math

sqrt2 = math.sqrt(2)

class Cluster:
    def __init__(self, orgImg, dirImg, widthImg, resImg, clusterColor, c):
        self.startPos = PixelPos(0, 0)
        self.endPos = PixelPos(0, 0)
        self.clusterPixels = []
        self.dirStat = Statistics()
        self.widthStat = Statistics()
        self.brightStat = Statistics()
        self.orgImg = orgImg
        self.dirImg = dirImg
        self.widthImg = widthImg
        self.resImg = resImg
        self.clusterColor = clusterColor
        self.isNerveTract = False
        self.length = None
        self.c = c


    def addPixel(self, pos):
        self.clusterPixels.append(copy.copy(pos))
        self.dirStat.addValue(self.dirImg[pos.yPos][pos.xPos][0])
        self.widthStat.addValue(self.widthImg[pos.yPos][pos.xPos][0])
        self.brightStat.addValue(self.orgImg[pos.yPos][pos.xPos])
        self.resImg[pos.yPos][pos.xPos]=self.clusterColor

    def isInCluster(self, pos):
        direction = self.dirImg[pos.yPos][pos.xPos][0]
        minoverflowVal = (self.dirStat.avg-(self.c.maxDirectionDiff/2))
        minoverflow = False
        if(minoverflowVal < 0):
            minoverflowVal += 1
            minoverflow = True
        maxoverflowVal = (self.dirStat.avg+(self.c.maxDirectionDiff/2))
        maxoverflow = False
        if(maxoverflowVal > 1):
            maxoverflowVal -= 1
            maxoverflow = True
        if((self.widthImg[pos.yPos][pos.xPos][0] != 0) and  #Wert nicht 0
              ((direction > (self.dirStat.avg-(self.c.maxDirectionDiff/2))) or #größer als untere Grenze
              (maxoverflow and direction < maxoverflowVal)) and #kleiner als Überlauf über 1
              ((direction < (self.dirStat.avg+(self.c.maxDirectionDiff/2))) or #kleiner als obere Grenze
               (minoverflow and direction > minoverflowVal))): #größer als Überlauf unter 0
            return True
        else:
            return False

    def isInClusterWithCircuit(self, pos):
        count  = 0
        if(not self.isInCluster(pos)):
            return False
        count += 1
        for i in range(self.c.circuitRange):
            dist = i+1
            #Darüber schauen
            if(pos.yPos-dist >= 0):
                #direkt
                tmpPos = copy.copy(pos)
                tmpPos.yPos -= dist
                if(self.isInCluster(tmpPos)):
                    count += 1
                #links
                if(tmpPos.xPos-dist >= 0):
                    tmpPos2 = copy.copy(tmpPos)
                    tmpPos2.xPos -= dist
                    if(self.isInCluster(tmpPos2)):
                        count += 1
                #rechts
                if(tmpPos.xPos+dist < len(self.widthImg[0])):
                    tmpPos2 = copy.copy(tmpPos)
                    tmpPos2.xPos += dist
                    if(self.isInCluster(tmpPos2)):
                        count += 1
            #darunter schauen
            if(pos.yPos+dist < len(self.widthImg)):
                #direkt
                tmpPos = copy.copy(pos)
                tmpPos.yPos += dist
                if(self.isInCluster(tmpPos)):
                    count += 1
                #links
                if(tmpPos.xPos-dist >= 0):
                    tmpPos2 = copy.copy(tmpPos)
                    tmpPos2.xPos -= dist
                    if(self.isInCluster(tmpPos2)):
                        count += 1
                #rechts
                if(tmpPos.xPos+dist < len(self.widthImg[0])):
                    tmpPos2 = copy.copy(tmpPos)
                    tmpPos2.xPos += dist
                    if(self.isInCluster(tmpPos2)):
                        count += 1
            #Auf gleicher Ebene schauen
            tmpPos = copy.copy(pos)
            #links
            if(tmpPos.xPos-dist >= 0):
                tmpPos2 = copy.copy(tmpPos)
                tmpPos2.xPos -= dist
                if(self.isInCluster(tmpPos2)):
                    count += 1
            #rechts
            if(tmpPos.xPos+dist < len(self.widthImg[0])):
                tmpPos2 = copy.copy(tmpPos)
                tmpPos2.xPos += dist
                if(self.isInCluster(tmpPos2)):
                    count += 1
        if(count < self.c.neededInCircuit):
            return False
        else:
            return True

    def searchDirection(self, startPos, directionChange):
        steps = 0
        startPos += directionChange
        olArr = []
        end = False
        while(end == False):
            if(startPos.xPos < 0 or startPos.xPos >= len(self.widthImg[0]) or
               startPos.yPos < 0 or startPos.yPos >= len(self.widthImg)):
                break
            if(self.isInClusterWithCircuit(startPos)):
                #Pixel im overlook-Bereich aufnehmen
                for e in olArr:
                    self.addPixel(e)
                olArr.clear()
                #Aktuelles Pixel hinzufuegen
                self.addPixel(startPos)
                steps += 1
                if(self.widthStat.avg != 0):
                    if(directionChange.yPos != 0 and directionChange.xPos != 0):
                        if(steps*sqrt2 > (self.widthStat.avg/2)+self.c.maxWidthExpansion):
                            end = True
                    else:
                        if(steps > (self.widthStat.avg/2)+self.c.maxWidthExpansion):
                            end = True
            else:
                if(len(olArr) < self.c.widthOverlook):
                    olArr.append(copy.deepcopy(startPos))
                else:
                    end = True
            startPos += directionChange


        return steps

    def findCluster(self, pos):
        startPos = PixelPos(pos.xPos, pos.yPos)
        if(self.widthImg[pos.yPos][pos.xPos][0] != 0):
            self.addPixel(pos)

        self.endPos = self.findClusterInDirection(pos, False)
        self.startPos = self.findClusterInDirection(startPos, True)
        #Duplikate in Pixelliste loeschen
        self.clusterPixels = list(set(self.clusterPixels))
        #Metriken berechnen
        self.calculateMetrics()
        
        print("cluster found: "+str(len(self.clusterPixels)))

    def findClusterInDirection(self, pos, revers):
        end = False
        olCount = 0
        nextPos = None
        lastPos = copy.copy(pos)
        olArr = []
        while(end == False):
            #Nicht über den rand und abbruch bei Kreisen
            if(pos.xPos < 0 or pos.xPos >= len(self.widthImg[0]) or
               pos.yPos < 0 or pos.yPos >= len(self.widthImg)or 
               len(self.clusterPixels) > 30000):
                if(len(self.clusterPixels) > 30000):
                    print("cluster abort")
                break
            if(self.isInClusterWithCircuit(pos)):
                olCount = 0
                for e in olArr:
                    self.findSlice(e)
                olArr.clear()
                lastPos = copy.copy(pos)
                (posCorrection, nextPos) = self.findSlice(pos)
                if(revers == True):
                    nextPos.xPos *= -1
                    nextPos.yPos *= -1

            else:
                if(olCount < self.c.lengthOverlook):
                    olCount += 1
                    olArr.append(copy.deepcopy(pos))
                else:
                    end = True

            if(nextPos != None):
                if(nextPos.yPos != 0):
                    pos.yPos += nextPos.yPos
                else:
                    if(posCorrection.yPos > self.c.maxPosCorrection):
                        posCorrection.yPos = self.c.maxPosCorrection
                    if(posCorrection.yPos < -self.c.maxPosCorrection):
                        posCorrection.yPos = -self.c.maxPosCorrection
                    pos.yPos += posCorrection.yPos

                if(nextPos.xPos != 0):
                    pos.xPos += nextPos.xPos
                else:
                    if(posCorrection.xPos > self.c.maxPosCorrection):
                        posCorrection.xPos = self.c.maxPosCorrection
                    if(posCorrection.xPos < -self.c.maxPosCorrection):
                        posCorrection.xPos = -self.c.maxPosCorrection
                    pos.xPos += posCorrection.xPos
        return copy.copy(lastPos)

    def findSlice(self, pos):
        self.addPixel(pos)
        #direction = self.dirImg[pos.yPos][pos.xPos][0]
        direction = self.dirStat.avg
        if(direction >= 0 and direction < 0.25):
            #Suche nach oben
            directionChange = PixelPos(0, -1)
            nWidth = self.searchDirection(pos, directionChange)
            #nach unten
            directionChange = PixelPos(0, 1)
            sWidth = self.searchDirection(pos, directionChange)
            #nach links oben
            directionChange = PixelPos(-1, -1)
            nwWidth = self.searchDirection(pos, directionChange)
            #nach rechts unten
            directionChange = PixelPos(1, 1)
            soWidth = self.searchDirection(pos, directionChange)
            if((nwWidth + soWidth)/sqrt2 > nWidth + sWidth):
                posCorrection = PixelPos(0, int((sWidth - nWidth)/2))
            else:
                posCorrection = PixelPos(int((soWidth - nwWidth)/2), int((soWidth - nwWidth)/2))
            #if(self.dirStat.avg <= 0.125):
            nextPos = PixelPos(1, 0)
            # else:
            #     nextPos = PixelPos(1, -1)
        elif(direction >= 0.25 and direction < 0.5):
            #nach rechts
            directionChange = PixelPos(1, 0)
            oWidth = self.searchDirection(pos, directionChange)
            #nach links
            directionChange = PixelPos(-1, 0)
            wWidth = self.searchDirection(pos, directionChange)
            #nach links oben
            directionChange = PixelPos(-1, -1)
            nwWidth = self.searchDirection(pos, directionChange)
            #nach rechts unten
            directionChange = PixelPos(1, 1)
            soWidth = self.searchDirection(pos, directionChange)
            if((nwWidth + soWidth)/sqrt2 > oWidth + wWidth):
                posCorrection = PixelPos(int((oWidth - wWidth)/2), 0)
            else:
                posCorrection = PixelPos(int((soWidth - nwWidth)/2), int((soWidth - nwWidth)/2))
            #if(self.dirStat.avg > 0.375):
            nextPos = PixelPos(0, -1)
            #else:
                # nextPos = PixelPos(1, -1)
        elif(direction >= 0.5 and direction < 0.75):
            directionChange = PixelPos(1, 0)
            oWidth = self.searchDirection(pos, directionChange)
            directionChange = PixelPos(-1, 0)
            wWidth = self.searchDirection(pos, directionChange)
            directionChange = PixelPos(1, -1)
            noWidth = self.searchDirection(pos, directionChange)
            directionChange = PixelPos(-1, 1)
            swWidth = self.searchDirection(pos, directionChange)
            if((noWidth + swWidth)/sqrt2 > oWidth + wWidth):
                posCorrection = PixelPos(int((oWidth - wWidth)/2), 0)
            else:
                posCorrection = PixelPos(int((noWidth - swWidth)/2), int((swWidth - noWidth)/2))
            #if(self.dirStat.avg <= 0.625):
            nextPos = PixelPos(0, -1)
            #else:
                #nextPos = PixelPos(-1, -1)
        else: #(direction >= 0.75 and direction < 1):
            directionChange = PixelPos(0, -1)
            nWidth = self.searchDirection(pos, directionChange)
            directionChange = PixelPos(0, 1)
            sWidth = self.searchDirection(pos, directionChange)
            directionChange = PixelPos(1, -1)
            noWidth = self.searchDirection(pos, directionChange)
            directionChange = PixelPos(-1, 1)
            swWidth = self.searchDirection(pos, directionChange)
            if((noWidth + swWidth)/sqrt2 > nWidth + sWidth):
                posCorrection = PixelPos(0, int((sWidth - nWidth)/2))
            else:
                posCorrection = PixelPos(int((noWidth - swWidth)/2), int((swWidth - noWidth)/2))
            #if(self.dirStat.avg > 0.875):
            nextPos = PixelPos(1, 0)
            #else:
                #nextPos = PixelPos(-1, -1)
        return (posCorrection, nextPos)

    def calculateMetrics(self):
        self.length = math.sqrt( (self.endPos.xPos - self.startPos.xPos )**2 + (self.endPos.yPos - self.startPos.yPos)**2)

    def colorizeInRgbaImg(self, img):
        for pixel in self.clusterPixels:
            img[pixel.yPos][pixel.xPos] = self.clusterColor
