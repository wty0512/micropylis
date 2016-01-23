'''
Created on Dec 31, 2015

@author: chris
'''
import math
import pyglet
from pyglet.gl import *
from pyglet.window import mouse
import kytten
import engine
from engine import Engine, micropolistool, speed, tiles, tileConstants
from engine.micropolistool import MicropylisTool
from engine.cityRect import CityRect
from gui.cityView import CityView
import dialogs
from engine.toolResult import ToolResult
from gui.controlPanel import ControlPanel
import gui
from layout import LayoutWindow, HorizontalLayout
import dialogs
from dialogs import MainMenuDialog, CityEvalDialog, BudgetDialog



class Keys(pyglet.window.key.KeyStateHandler):
    '''
        responds to keypresses, notifying an event handler
        while storing the current state of the keys for querying.
    '''
    def __init__(self, parent):
        self.parent = parent

    def on_key_press(self, symbol, modifiers):
        try:
            self.parent.key_press(symbol, modifiers)
        except AttributeError:
            # parent does not impl key_press method
            pass
        super(Keys, self).on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        try:
            self.parent.key_release(symbol, modifiers)
        except AttributeError:
            # parent does not impl key_release method
            pass
        super(Keys, self).on_key_release(symbol, modifiers)






'''
class MicroWindow

The main window for micropylis.
handles tool dispatching.


'''
class MicroWindow(pyglet.window.Window, LayoutWindow):
    def __init__(self, animLoop):
        self.DEFAULT_WIDTH = int(gui.config.get('window','DEFAULT_WIDTH'))
        self.DEFAULT_HEIGHT = int(gui.config.get('window','DEFAULT_HEIGHT'))
        pyglet.window.Window.__init__(self, width=self.DEFAULT_WIDTH,
                                   height=self.DEFAULT_HEIGHT,
                                   resizable=True,
                                   vsync=False)
        
        # load in tile specs
        tiles.Tiles().readTilesSpec(gui.config.get('misc','TILES_SPEC_FILE')) 
        
        self.animLoop = animLoop
        self.engine = None
        
        self.cityView = CityView(self.animLoop.getClock())
        self.push_handlers(self.cityView.keys)
        self.controlPanel = ControlPanel()
        self.controlPanel.push_handlers(self)
        
        LayoutWindow.__init__(self,HorizontalLayout([
                                                   self.cityView,
                                                   self.controlPanel],
                                                  padding=0))
        
        # tool vars:
        self.dragStart = (0,0)
        self.currentTool = None
        self.toolStroke = None
        self.lastX = 0
        self.lastY = 0
        
        # window stuff
        self.icon = pyglet.image.load(gui.config.get('window','ICON_FILE')) # icon is set at resize
        self.set_minimum_size(640, 480)
        self.set_caption(gui.config.get('window','CAPTION'))
        self.fpsDisplay = pyglet.clock.ClockDisplay(color=(.2,.2,.2,0.6))
        self.initGuiComponents()
        
        self.set_location(40,40)
        
        # 
        for (name,font) in gui.config.items('font_files'):
            pyglet.font.add_file(font)

        pyglet.clock.schedule_interval(self.update, 1/60.)
        self.speedKeyMap = {
                pyglet.window.key._1 : speed.PAUSED,
                pyglet.window.key._2 : speed.SLOW,
                pyglet.window.key._3 : speed.NORMAL,
                pyglet.window.key._4 : speed.FAST,
                pyglet.window.key._5 : speed.SUPER_FAST}
        self.speed = None
        
        #self.newCity()
        self.loadCity('cities/hawkins.cty')
        


    def newCity(self):
        #newCityDialog = NewCityDialog(self)
        
        self.engine = Engine()
        self.cityView.reset(self.engine)
        self.controlPanel.reset(self.engine)
        self.setSpeed(speed.PAUSED)
        
    
    def loadCity(self, filePath):
        self.engine = Engine()
        self.engine.loadCity(filePath)
        self.cityView.reset(self.engine)
        self.controlPanel.reset(self.engine)
        self.setSpeed(speed.PAUSED)
        
    def initGuiComponents(self):
        self.setupDialogs()

        
    def setupDialogs(self):
        self.dialogBatch = pyglet.graphics.Batch()
        self.mainDialog = dialogs.ToolDialog(self)
        self.register_event_type('on_update')
        self.push_handlers(self.mainDialog)
        pyglet.clock.schedule_interval(self.updateKytten, 1/60.)
        self.dialogs = {'main_menu':None,
              'budget_menu':None,
              'city_eval':None,
              'city_graphs':None}
        self.dialogTypes = {'main_menu':MainMenuDialog,
              'budget_menu':BudgetDialog,
              'city_eval':CityEvalDialog,
              'city_graphs':None}
        
    def toggleFullscreen(self):
        if not self._fullscreen:
            self.set_fullscreen(True)
        else:
            self.set_fullscreen(False)
            
    def initGL(self, width, height):
        glClearColor(0.8,0.49,0.4,1)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glEnable(GL_LINE_SMOOTH)
        glEnable(GL_POLYGON_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        
        glViewport(0, 0, width, height)
        gl.glMatrixMode(gl.GL_PROJECTION)
        glLoadIdentity()
        gl.glOrtho(0, width, 0, height, -1, 1)
        gl.glMatrixMode(gl.GL_MODELVIEW)
            
    def on_resize(self, width, height):
        self.set_icon(self.icon)
        self.initGL(width,height)
        self.cityView.setRenderSize(width, height)
        LayoutWindow.doLayout(self, self.width, self.height)
        
        
    def on_close(self):
        self.animLoop.exit()
        return pyglet.window.Window.on_close(self)
        
    def on_key_release(self, symbol, modifiers):
        if (symbol == pyglet.window.key.X):
            #self.engine.testChange()
            self.loadCity('cities/hawkins.cty')
        elif (symbol == pyglet.window.key.S):
            self.newCity()
        if (modifiers & pyglet.window.key.MOD_ALT and
                symbol == pyglet.window.key.ENTER):
            self.toggleFullscreen()
        else:
            if symbol in self.speedKeyMap:
                self.setSpeed(self.speedKeyMap[symbol])
                
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.engine and self.cityView.hitTest(x, y):
            self.cityView.zoomToPoint(x, y, scroll_y)
            
    def on_mouse_motion(self, x, y, dx, dy):
        LayoutWindow.onMouseMotion(self, x, y, dx, dy)
        # set hand cursor if mouse over clickable widget
        widget = self.getWidgetAtPoint(x, y)
        if widget.isClickable():
            self.set_mouse_cursor(self.CURSOR_HAND)
        else:
            self.set_mouse_cursor()
        
        if self.engine and self.cityView.hitTest(x, y):
            self.onToolHover(x, y)
            
    def on_mouse_press(self, x, y, button, modifiers):
        LayoutWindow.onMousePress(self, x, y, button, modifiers)
        
        self.dragStart = (x,y)
        if self.engine and self.cityView.hitTest(x, y):
            self.onToolDown(x, y, button, modifiers)
        
    def on_mouse_release(self, x, y, button, modifiers):
        LayoutWindow.onMouseRelease(self, x, y, button, modifiers)
        
        self.set_mouse_cursor()
        if self.engine and self.cityView.hitTest(x, y):
            self.onToolUp(x, y, button, modifiers)
            
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        LayoutWindow.onMouseDrag(self, x, y, dx, dy, buttons, modifiers)
        
        if self.engine and self.cityView.hitTest(x, y):
            self.onToolDrag(x, y, dx, dy, buttons, modifiers)
    
    def set_mouse_cursor(self, cursor=None):
        if cursor == self.cursor:
            return
        self.cursor = cursor
        if cursor is not None:
            cursor = self.get_system_mouse_cursor(cursor)
        pyglet.window.Window.set_mouse_cursor(self, cursor)
        
        
    def gui_invoke(self, guiItemName):
        cityActive = True
        if self.dialogs[guiItemName] is None or\
                not self.dialogs[guiItemName].active:
            self.dialogs[guiItemName] = self.dialogTypes[guiItemName]\
                                            (self,cityActive)
        else:
            self.dialogs[guiItemName].teardown()
            
    def setSpeed(self, newSpeed):
        if newSpeed == self.speed:
            return
        pyglet.clock.unschedule(self.engine.animate)
        self.animLoop.setSpeed(self.speed, newSpeed)
        self.cityView.setSpeed(newSpeed)
        self.speed = newSpeed
        self.controlPanel.addInfoMessage(newSpeed.name + " Speed")
        if self.speed == speed.PAUSED:
            return
        pyglet.clock.schedule_interval(self.engine.animate, newSpeed.delay)

    
    def update(self, dt):
        LayoutWindow.update(self,self.width,self.height)
        self.cityView.update(dt)
        self.controlPanel.update(dt)
        
    def updateKytten(self, dt):
        self.dispatch_event('on_update', dt)
        
    def on_draw(self):
        self.clear()
        LayoutWindow.draw(self)
        self.dialogBatch.draw()
        self.fpsDisplay.draw()
            
            
            
    ''' Tools Functions '''

    def selectTool(self, toolType):
        '''
            selectTool(tooltype)
            accepts a string specifying what tool should
            be currently active. returns tool type object
        '''
        if self.currentTool is not None and \
                toolType == self.currentTool.name:
            return
        if toolType == "Pan":
            self.currentTool = None
            return
        
        tool = MicropylisTool.factory(toolType)
        self.currentTool = tool
        return tool
        
    def onToolDown(self, x, y, button, modifiers):
        loc = self.cityView.screenCoordsToCityLocation(x, y)
        self.lastX = loc.x
        self.lastY = loc.y
        self.drag = False
        if button == mouse.RIGHT:
            self.set_mouse_cursor(self.CURSOR_CROSSHAIR)
            return
        if self.currentTool == None:
            self.set_mouse_cursor(self.CURSOR_CROSSHAIR)
            return
        if button != mouse.LEFT:
            return
        if self.currentTool.type == micropolistool.QUERY:
            self.doQueryTool(loc.x, loc.y)
            self.toolStroke = None
        else:
            self.toolStroke = self.currentTool.beginStroke(
                                                self.engine,
                                                loc.x, loc.y)
            self.previewTool()
            self.set_mouse_cursor(self.CURSOR_HAND)
            
        
    def onToolDrag(self, x, y, dx, dy, buttons, modifiers):
        if not self.cityView.hitTest(self.dragStart[0], self.dragStart[1]):
            return
        self.drag = True
        if (self.currentTool is None or
                buttons & mouse.RIGHT):
            self.cityView.moveView(dx, dy)
            return
        loc = self.cityView.screenCoordsToCityLocation(x, y)
        tx = loc.x
        ty = loc.y
        if tx == self.lastX and ty == self.lastY:
            return
        if buttons & mouse.LEFT == 0:
            return
        self.lastX = tx
        self.lastY = ty
        if self.toolStroke is not None:
            self.toolStroke.dragTo(tx, ty)
            self.previewTool()
        elif self.currentTool == micropolistool.QUERY:
            self.doQueryTool(tx, ty)
        
        
    def onToolUp(self, x, y, button, modifiers):
        if self.toolStroke is not None:
            self.cityView.setToolPreview(None)
            self.showToolResult(self.toolStroke.getLocation(),
                                self.toolStroke.apply())
            self.toolStroke = None
            self.engine.tileUpdateCheck()
        loc = self.cityView.screenCoordsToCityLocation(x, y)
        tx = loc.x
        ty = loc.y
        if button == mouse.RIGHT and not self.drag:
            self.doQueryTool(tx, ty)
        self.set_mouse_cursor()  
        self.onToolHover(x,y)
        #TODO conditionally show budget window here?
        
            
    def onToolHover(self, x, y):
        if self.currentTool is None or\
            self.currentTool.type == micropolistool.QUERY:
                self.cityView.setToolCursor(None)
                return
            
        loc = self.cityView.screenCoordsToCityLocation(x,y)
        #print loc
        x = loc.x
        y = loc.y
        w = self.currentTool.getWidth()
        h = self.currentTool.getHeight()
        
        if w >= 3:
            x -= 1
        if h >= 3:
            y -= 1
        
        rect = CityRect(x,y,w,h)
        self.cityView.newToolCursor(rect, self.currentTool)
        
    def previewTool(self):
        assert self.toolStroke is not None
        assert self.currentTool is not None
        
        self.cityView.newToolCursor(self.toolStroke.getBounds(), 
                                        self.currentTool)
        self.cityView.setToolPreview(self.toolStroke.getPreview())
        
    def showToolResult(self, loc, result):
        if result.value == ToolResult.SUCCESS:
            formatString = gui.cityMessages.get('toolresults','SUCCESS')
            msg = formatString.format(cost=str(result.cost))
            self.controlPanel.addInfoMessage(msg)
        elif result.value == ToolResult.INSUFFICIENT_FUNDS:
            self.controlPanel.addInfoMessage(
                            gui.cityMessages.get('toolresults','INSUFFICIENT_FUNDS'))
        elif result.value == ToolResult.UH_OH:
            self.controlPanel.addInfoMessage(
                            gui.cityMessages.get('toolresults','BULLDOZE_FIRST'))
        elif result.value == ToolResult.NONE:
            self.controlPanel.addInfoMessage(
                            gui.cityMessages.get('toolresults','NONE'))
        
    
    def doQueryTool(self, xPos, yPos):
        ''' print tilevalue to infopane messages '''
        tileValue = self.engine.getTile(xPos,yPos)
        '''self.engine.setTile(xPos,yPos,tileConstants.DIRT)'''
        queryMsg = "Power of ({0},{1}): {2}".format(
                str(xPos), str(yPos), str(self.engine.hasPower(xPos, yPos)))
        '''queryMsg = "Power of ({0},{1}): {2}".format(
                str(xPos), str(yPos), str(self.engine.getTile(xPos, yPos)))'''
        self.controlPanel.addInfoMessage(queryMsg)
        





        