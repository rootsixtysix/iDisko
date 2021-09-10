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
from itertools import combinations
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn import svm
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
#from sklearn.model_selection import train_test_split
#from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import csv
import json

class scanData():
    def __init__(self):
        self.data = np.array([])
        self.target = np.array([])
        print(self.data.size)

    def append(self, toAppend):
        for row in toAppend['data']:
            if (len(self.data) == 0):
                self.data = [ row ]
            else:
                self.data = np.append(self.data, [row], axis=0)

        for row in toAppend['target']:
            if (len(self.target) == 0):
                self.target = [ row ]
            else:
                self.target = np.append(self.target, [row], axis=0)

def classificate(clusters, resultImg, algorithm, subset, filelist, masszahlCalculation):
    learnData = scanData()
    testData = scanData()

    #load training data
    learnData = importLearnData(filelist)
    scaler = preprocessing.StandardScaler().fit(learnData.data)
    learnData.data = scaler.transform(learnData.data)

    #choose classification algorithm
    if (algorithm == 'svm'):
        classificator = svm.SVC()
    elif (algorithm == 'gnb'):
        classificator = GaussianNB()
    else:
        classificator = GaussianNB()

    #train with training data
    classificator.fit(learnData.data[:, subset], learnData.target)

    #classificate with test data from current cluster
    testData.append(clustersToDataTarget(clusters))
    testData.data = scaler.transform(testData.data)
    testData.target = classificator.predict(testData.data[:, subset])

    #colorize result Image
    nerveTracts = []
    for i in range(len(testData.target)):
        if (testData.target[i] == 1):
            nerveTracts.append(clusters[i])

    #Merkmalsauswahl
    if (masszahlCalculation == True):
        calculateMasszahl(learnData, algorithm)

    return nerveTracts

def clustersToDataTarget(clusters):
    #export clusters to file
    X = []
    t = []
    for cluster in clusters:
        x = [
            len(cluster.clusterPixels),     #0
            cluster.length,                 #1
            cluster.length / cluster.widthStat.avg, #2
            cluster.widthStat.min,          #3
            cluster.widthStat.max,          #4
            cluster.widthStat.avg,          #5
            cluster.widthStat.variance,     #6
            cluster.dirStat.max - cluster.dirStat.min,  #7
            cluster.dirStat.variance,       #8
            cluster.brightStat.min,         #9
            cluster.brightStat.max,         #10
            cluster.brightStat.avg,         #11
            cluster.brightStat.variance     #12
        ]
        X.append(x)

        if (cluster.isNerveTract == True):
            t.append(1)
        else:
            t.append(0)

    scan = {
        "data": X,
        "target": t
    }
    return(scan)

def exportClusterData(clusters, nerveTractIndices):
    for i in nerveTractIndices:
        clusters[i].isNerveTract = True

    scan = clustersToDataTarget(clusters)

    with open('referenceData/data.json', 'w+') as outfile:
        json.dump(scan, outfile)

    outputData = scanData()
    outputData.append(scan)

def importLearnData(filelist):
    learnData = scanData()
    for file in filelist:
        input = open('referenceData/'+file+'.json', "r")
        scan = json.load(input)
        learnData.append(scan)
    return learnData

def importAsArray(filelist):
    data = []
    target = []
    for file in filelist:
        input = open('referenceData/'+file+'.json', "r")
        scan = json.load(input)
        if (data == []):
            data = scan['data']
            target = scan['target']
        else:
            data.append(scan['data'])
            target.append(scan['target'])
    return (data, target)

def calculateMasszahl(dataset, algorithm):
    X= dataset.data
    t= dataset.target

    results = []
    for card in range(1, X.shape[1]+1):
        subsets= combinations([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], card)
        for subset in subsets:
            X1= X[:,subset]

            X11= X1[t==0, :]
            X12= X1[t==1, :]

            # Kovarianzmatrizen berechnen
            S_M1= np.cov(X1.transpose())
            S_W1= 1/2*(np.cov(X11.transpose())+np.cov(X12.transpose()))
            S_B1= S_M1 - S_W1

            if S_B1.size==1:
                J1_= S_B1/S_W1
            else:
                J1_= np.trace(S_B1)/np.trace(S_W1)

            X_train, X_test, t_train, t_test = train_test_split(X1, t, test_size=.4, random_state=1)

            #choose classification algorithm
            if (algorithm == 'svm'):
                classificator = svm.SVC()
            elif (algorithm == 'gnb'):
                classificator = GaussianNB()
            else:
                classificator = GaussianNB()

            classificator.fit(X_train, t_train)
            score = classificator.score(X_test, t_test)

            results.append( (subset, J1_, score) )

    results.sort(key=lambda tup: tup[2])
    #print(results)

    for r in results:
        print(r[0], '\t', r[1], '\t', r[2])


