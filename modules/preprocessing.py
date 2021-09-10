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
from skimage import filters
from skimage import io
from skimage.viewer import ImageViewer
from skimage import exposure

from skimage import data

"""
global variables
"""
max_lightness_value = 65000

"""
methods
"""
def preprocess_image(image):
    #image = normalize_lightness(image)
    #image = filters.gaussian(image, 2)
    image = exposure.equalize_adapthist(image, clip_limit=0.03)
    return image

def normalize_lightness(image):
    average_lightness_value = calculate_average_lightness(image)
    while(average_lightness_value < max_lightness_value/2):
        image = exposure.adjust_gamma(image, gamma=0.5)
        average_lightness_value = calculate_average_lightness(image)
        print(average_lightness_value)
    return image

def calculate_average_lightness(image):
    average_lightness_value = 0
    (height, width) = np.shape(image)
    for h in range(0, height):
        for w in range(0, width):
            average_lightness_value += image[h][w]
    return average_lightness_value / (height*width)
