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

import math
from math import sqrt
import cmath

MAX_NERVE_TRACT_WIDTH = 300 #TODO: replace by global variable later
PI = math.pi

def calculateDirectionAndWidth(pixelsInWtoE, pixelsInSWtoNE, pixelsInStoN, pixelsInNWtoSO ):
    """
    Input: Anzahl der Pixel in den vier Durchläufen
    Output: Polarkoordinaten als Tupel (width, angle)
            width:  ist die Breite, die ein Slice an der Stelle des Pixels hat
            angle:  ist die Richtung in die die (eventuelle) Nervenbahn an dieser Stelle verläuft, also 90° gedreht zum slice
                    in Polardarstellung, also Wertebereich 0-PI
    """
    theta = 0;
    width = 0
    # polars is a list of tuples, where for each tuple the first value is the angle (key)
    # and the second value is the amount of pixels in that direction (value)
    # the amount of pixels in angles that are shifted by 45° towards the axes are multiplied by sqrt(2)
    polars = list()
    polars.append( (pixelsInWtoE,             0))
    #polars.append( (pixelsInSWtoNE * sqrt(2), PI/4))
    polars.append( (pixelsInStoN,             PI/2))
    #polars.append( (pixelsInNWtoSO * sqrt(2), 3/4*PI,))
    
    polars2 = list()
    polars2.append( (pixelsInSWtoNE * sqrt(2), PI/4))
    polars2.append( (pixelsInNWtoSO * sqrt(2), 3/4*PI,))

    #remove polars that are too wide
    polars = removePolarsThatAreTooWide(polars)
    polars2 = removePolarsThatAreTooWide(polars2)
    #sort the remaining polars by length (value); smallest length first
    polars.sort(key=lambda tup: tup[0])
    polars2.sort(key=lambda tup: tup[0])

    numberOfDirectionsNotZero = len(polars)
    numberOfDirectionsNotZero2 = len(polars2)
    #if (numberOfDirectionsNotZero>=3):
        #(width, theta) = polars[0]
    if (numberOfDirectionsNotZero>=2):
        if(numberOfDirectionsNotZero2 >= 1):
            (width, theta) = polars2[0]
        else:
            (width, theta) = polars[0]
        #(width, theta) = calculateDirectionAndWidthHelper(polars[0], polars[1])
        #(width, theta) = polars[0]
    elif (numberOfDirectionsNotZero==1):
        (width, theta) = polars[0]
    else:
        (width, theta) = (0, 0)

    angle = theta + math.pi/2

    #angle should be in the range from 0° to 180°
    if (angle >= PI):
        angle -= PI
    if (angle <0):
        angle += PI

    return(width, angle)

def removePolarsThatAreTooWide(polars):
    polarsWhithoutZeroLength = list()
    for length, angle in polars:
        if ( (length!=0) and (length!=MAX_NERVE_TRACT_WIDTH) ):
            polarsWhithoutZeroLength.append( (length, angle) )
    return polarsWhithoutZeroLength

def calculateDirectionAndWidthHelper(polar1, polar2):
    theta = 0;
    width = 0;
    (a, alpha)  = polar1
    (b, beta)   = polar2

    #rotate beta by 180 if diff_angle is too big
    if (beta-alpha) > PI/2:
        beta -= PI
    if (beta-alpha) < -PI/2:
        alpha -= PI

    #calculate angle and width whith different cases
    diff_angle = beta - alpha
    if ( (diff_angle == PI/4) or (diff_angle == -3/4*PI) ):
        delta = math.atan(sqrt(2)*a/b - 1)
        theta = alpha + delta
        width = a * math.cos(delta)
    elif ( (diff_angle == -PI/4) or (diff_angle == 3/4*PI) ):
        delta = math.atan(sqrt(2)*a/b - 1)
        theta = alpha - delta
        width = a * math.cos(delta)
    elif ( (diff_angle == PI/2) or (diff_angle == -PI/2) ):
        (width, theta) = polar1

    return (width, theta)
