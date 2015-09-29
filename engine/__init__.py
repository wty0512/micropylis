'''
    main engine module
    
'''

import struct
from array import *
from engine.tileConstants import *

''' misc functions '''
def readShort(aFile):
    '''map is stored big endian'''
    return struct.unpack('>H',aFile.read(2))[0]

def readInt(aFile):
    '''map is stored big endian'''
    return struct.unpack('>I', aFile.read(4))[0]

def create2dArray(width, height):
    return [[0 for y in range(height)] for x in range(width)]

'''
class History
structure to encapsulate census history
'''
class History(object):
    def __init__(self):
        self.cityTime = 0
        self.res = array('H')
        self.com = array('H')
        self.ind = array('H')
        self.money = array('H')
        self.pollution = array('H')
        self.crime = array('H')
        self.resMax = 0
        self.comMax = 0
        self.indMax = 0

'''
    class Engine
    city simulation engine
    
    instance data:
    map data
    census data
    history data
'''
class Engine(object):
    DEFAULT_WIDTH = 120
    DEFAULT_HEIGHT = 100
    
    def __init__(self, width=None, height=None):
        ''' mapdata is stored as [column][row] '''
        if (width == None):
            width = self.DEFAULT_WIDTH
        if (height == None):
            height = self.DEFAULT_HEIGHT
        self.map = create2dArray(height, width)
        self.history = History()
        #self.load('maponly.cty')
        self.load('corner1.cty')
        
    def getTile(self, x, y):
        return self.map[y][x] & LOMASK
        
    def getWidth(self):
        return len(self.map[0])
    
    def getHeight(self):
        return len(self.map)
        
    def newCity(self):
        pass
    
    def clearCensus(self):
        pass
    
    ''' given a filename will load saved city data '''
    def load(self, fileName):
        saveFile = open(fileName, "rb")
        try:
            self.loadHistoryArray(saveFile, self.history.res)
            self.loadHistoryArray(saveFile, self.history.com)
            self.loadHistoryArray(saveFile, self.history.ind)
            self.loadHistoryArray(saveFile, self.history.crime)
            self.loadHistoryArray(saveFile, self.history.pollution)
            self.loadHistoryArray(saveFile, self.history.money)
            self.loadMisc(saveFile)
            self.loadMap(saveFile)
        except IOError as err:
            print str(err)
        finally:
            saveFile.close()
        pass
    
    def loadHistoryArray(self, saveFile, array):
        for i in range(240):
            array.append(readShort(saveFile))
        
    def loadMisc(self, saveFile):
        readShort(saveFile)
        readShort(saveFile)
        self.resPop = readShort(saveFile)
        self.comPop = readShort(saveFile)
        self.indPop = readShort(saveFile)
        self.resValve = readShort(saveFile)
        self.comValve = readShort(saveFile)
        self.indValve = readShort(saveFile)
        self.cityTime = readInt(saveFile)
        self.crimeRamp = readShort(saveFile)
        self.polluteRamp = readShort(saveFile)
        self.landValueAverage = readShort(saveFile)
        self.crimeAverage = readShort(saveFile)
        self.pollutionAverage = readShort(saveFile)
        self.gameLevel = readShort(saveFile)
        readShort(saveFile) #evaluation.cityClass
        readShort(saveFile) #evaluation.cityScore
        
        for i in range(18,50):
            readShort(saveFile)
            
        readInt(saveFile) # budget.totalFunds
        readShort(saveFile) # autoBulldoze
        readShort(saveFile) # autoBudget
        readShort(saveFile) # autoGo
        readShort(saveFile) # userSoundOn
        readShort(saveFile) # cityTax
        readShort(saveFile) # simSpeedAsInt
        ''' budget numbers '''
        readInt(saveFile) # police
        readInt(saveFile) # fire
        readInt(saveFile) # road
        
        for i in range(64,120):
            readShort(saveFile)
            
    def loadMap(self, saveFile):
        for x in range(self.DEFAULT_WIDTH):
            for y in range(self.DEFAULT_HEIGHT):
                z = readShort(saveFile)
                # clear 6 most significant bits (leaving 10 lsb's)
                z &= ~(1024 | 2048 | 4096 | 8192 | 16384)
                self.map[y][x] = z
    
    def step(self):
        pass
    
    def simulate(self, mod16):
        pass
    
    
    
    
    
    
    
    
    
    