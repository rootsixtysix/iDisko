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

def colorPixelsInRgbaImage(image, pixels, rgbaColor):
    for p in pixels:
        (x, y) = p
        image[y][x] = rgbaColor

    return image


class Statistics:
    def __init__(self):
        self.count = 0
        self.min = 0
        self.max = 0
        self.avg = 0
        self.sum = 0
        self.varianceSum = 0
        self.variance = 0
    def addValue(self, val):
        if(self.count == 0):
            self.min = val
            self.max = val
        else:
            if(val < self.min):
                self.min = val
            if(val > self.max):
                self.max = val
        self.count += 1
        self.sum += val
        self.avg = self.sum / self.count
        self.varianceSum += (val - self.avg) ** 2
        self.variance = self.varianceSum / self.count



class PixelPos:
    def __init__(self, xPos, yPos):
        self.xPos = xPos
        self.yPos = yPos

    def copy_constructor(self, orig):
        self.xPos = orig.xPos
        self.yPos = orig.yPos

    def __add__(self, other):
        xPos = self.xPos + other.xPos
        yPos = self.yPos + other.yPos
        return PixelPos(xPos, yPos)

    def __sub__(self, other):
        xPos = self.xPos - other.xPos
        yPos = self.yPos - other.yPos
        return PixelPos(xPos, yPos)
    
    #eq and hash to delete Duplicates in List via list(set(orginalList))
    def __eq__(self, other):
        if(other == None):
            return False
        else:
            return (self.xPos == other.xPos) and (self.yPos == other.yPos)
    
    def __hash__(self):
        return hash(('xPos', self.xPos,
                 'yPos', self.yPos))
    
    