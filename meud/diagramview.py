# TODO: Move labels, when delete node
import os.path

from fca import write_xml

import wx

import images
import subprocess
from globals_ import dot_path as graphviz_path
from fca.readwrite import uread_xml

class ConceptNode(object):
    
    def get_position(self):
        return self._pos
    
    def set_position(self, value):
        self._pos = value
    
    pos = property(get_position, set_position)
    
    def get_X(self):
        return self._pos[0]
    
    def set_X(self, value):
        self._pos[0] = value
    
    def get_Y(self):
        return self._pos[1]
    
    def set_Y(self, value):
        self._pos[1] = value
        
    X = property(get_X, set_X)
    Y = property(get_Y, set_Y)
    
    def get_concept(self):
        return self._concept
        
    concept = property(get_concept)
    
    is_highlighted = False
    
    def __init__(self, concept=None, pos=(100, 100), top_labels=["Top"],
                    bottom_labels=["Bottom"]):
        self._pos = pos
        self._concept = concept
        self._t_labels = top_labels
        self._b_labels = bottom_labels
        self.CIRCLE_RADIUS = 14
        
    def draw(self, dc):
        if self.is_highlighted:
            pen = wx.RED_PEN
        else:
            pen = wx.BLACK_PEN
        pen.SetWidth(1)
        dc.SetPen(pen)
        
        # brush = wx.Brush(wx.Color(67, 110, 234))
        brush = wx.Brush("WHITE")
        dc.SetBrush(brush)
        dc.DrawCircle(self.X, self.Y, self.CIRCLE_RADIUS)
        
        h_step = dc.GetCharHeight()
        
        if len(self._t_labels) != 0:
            # TODO:
            _t_labels = self._t_labels
            
            rect_width = 0
            for i in range(len(_t_labels)):
                lwidth, lheight, ldescent, el = \
                                    dc.GetFullTextExtent(_t_labels[i])
                if lwidth > rect_width:
                    rect_width = lwidth
            
            pen = wx.WHITE_PEN
            pen.SetWidth(1)
            dc.SetPen(pen)
            dc.SetBrush(wx.Brush("WHITE"))
            # dc.DrawRectangle(self.X - rect_width / 2 - 3, 
            #                  self.Y - h_step * len(_t_labels) - self.CIRCLE_RADIUS, 
            #                  rect_width + 6,
            #                  h_step * len(_t_labels) + 2)
                         
            dc.SetTextBackground("WHITE")
            dc.SetBackgroundMode(wx.SOLID)
            for i in range(len(_t_labels)):
                horizontal_offset = rect_width / 2
                dc.DrawText(_t_labels[i], self.X - horizontal_offset, 
                    self.Y - self.CIRCLE_RADIUS - h_step * (i + 1) - 5)
        
        if len(self._b_labels) != 0:
            # TODO:
            _b_labels = self._b_labels        
                
            rect_width = 0
            for i in range(len(_b_labels)):
                lwidth, lheight, ldescent, el = \
                                    dc.GetFullTextExtent(_b_labels[i])
                if lwidth > rect_width:
                    rect_width = lwidth
            pen = wx.WHITE_PEN
            pen.SetWidth(1)
            dc.SetPen(pen)
            dc.SetBrush(wx.Brush("WHITE"))
            dc.SetBackgroundMode(wx.SOLID)
            # dc.DrawRectangle(self.X - rect_width / 2 - 3, 
            #                  self.Y + self.CIRCLE_RADIUS - 2, 
            #                  rect_width + 6,
            #                  h_step * len(_b_labels) + 2)
            dc.SetTextBackground("WHITE")
            for i in range(len(_b_labels)):
                horizontal_offset = rect_width / 2
                dc.DrawText(_b_labels[i], self.X - horizontal_offset, 
                    self.Y + self.CIRCLE_RADIUS + h_step*i + 5)
        
    def hit_test(self, x, y):
        if ((x-self.X) ** 2 + (y - self.Y) ** 2) <= self.CIRCLE_RADIUS * self.CIRCLE_RADIUS:
            return True
        else:
            return False
            
    def set_labels(self, top_labels, bottom_labels):
        """docstring for set_labels"""
        self._t_labels = top_labels
        self._b_labels = bottom_labels
        

class MyCanvas(wx.ScrolledWindow):
    
    def __init__(self, parent, id, size = wx.DefaultSize):
        wx.ScrolledWindow.__init__(self, parent, id, (0, 0),
                                    size=size, style=wx.SUNKEN_BORDER)
        self.parent = parent
        self.SetBackgroundColour("WHITE")
        self._dragged = None
        self.cs = None
        self.maxWidth  = 1000
        self.maxHeight = 1000
        self.old_size = None
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouse)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
        self._show_full_extent = True
        self._show_full_intent = True
        
        # TODO:
        font = wx.Font(14, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Verdana')
        self._font_size = font.GetPointSize()
        self._base_size = self._font_size - 1
        
    def getWidth(self):
        return self.maxWidth

    def getHeight(self):
        return self.maxHeight
        
    def ChangeExtentLabelView(self):
        self._show_full_extent = not self._show_full_extent
        self.RedrawLabels()
        
    def ChangeIntentLabelView(self):
        self._show_full_intent = not self._show_full_intent
        self.RedrawLabels()
        
    def RedrawLabels(self):
        """docstring for RedrawLabels"""
        top_concept = self.cs.top_concept
        objects_number = len(top_concept.extent)
        for node in self.nodes:
            if self._show_full_extent:
                b_labels = self._own_objects[node._concept]
            else:
                label = "{0:.0f}".format(round(len(node._concept.extent) * 100 / float(objects_number)))
                b_labels = [label]
            if self._show_full_intent:
                t_labels = self._own_attributes[node._concept]
            else:
                t_labels = [str(len(node._concept.intent))]
            node.set_labels(t_labels, b_labels)
        self.Refresh()
        
    def SaveCoordinates(self):
        for concept in self.cs:
            for node in self.nodes:
                if node.concept == concept:
                    concept.meta['X'] = node.X
                    concept.meta['Y'] = node.Y
        
    def SetConceptSystem(self, cl):
        self.cs = cl
        self._own_objects = find_own_objects(cl)
        self._own_attributes = find_own_attributes(cl)
        if cl[0].meta.has_key('X'):
            max_x = -1
            max_y = -1
            for concept in cl:
                if concept.meta['X'] > max_x:
                    max_x = concept.meta['X']
                if concept.meta['Y'] > max_y:
                    max_y = concept.meta['Y']
                size = (max_x + 20, max_y + 20)
        else:
            self._positions = get_coordinates(cl)
            size = (640, 480)
        
        self.nodes = []
        self.old_size = size
        for concept in cl:
            if concept.meta.has_key('X'):
                new_coords = (concept.meta['X'], concept.meta['Y'])
            else:
                new_coords = (10 + self._positions[concept][0] * (size[0] - 20),
                    size[1] - 10 - self._positions[concept][1] * (size[1] - 20))
            if self._show_full_extent:
                b_labels = self._own_objects[concept]
            else:
                b_labels = str(len(concept.extent))
            if self._show_full_intent:
                t_labels = self._own_attributes[concept]
            else:
                t_labels = str(len(concept.intent))
            self.nodes.append(ConceptNode(concept, new_coords, t_labels,
                                b_labels))
        
        self.lines = []
        for i in range(len(cl)):
            for concept in cl.children(cl[i]):
                j = cl.index(concept)
                self.lines.append((self.nodes[i], self.nodes[j]))
        
    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self)
        self.DoDrawing(dc)

        
    def DoDrawing(self, dc):
        dc.BeginDrawing()

        bg = wx.Brush(self.GetBackgroundColour())
        dc.SetBackground(bg)
        dc.Clear()
        
        font = wx.Font(14, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Verdana')
        font.SetPointSize(self._font_size)
        dc.SetFont(font)
        
        for line in self.lines:
            if line[0].is_highlighted and line[1].is_highlighted:
                pen = wx.RED_PEN
            else:
                pen = wx.BLACK_PEN
            pen.SetWidth(1)
            dc.SetPen(pen)
            dc.DrawLine(line[0].X, line[0].Y, line[1].X, line[1].Y)
            
        for node in self.nodes:
            node.draw(dc)
            
        dc.EndDrawing()
        
    def OnSize(self, event):
        if self.cs:
            size = self.GetClientSize()
            for i in range(len(self.cs)):
                X = self.nodes[i].X * size[0] / float(self.old_size[0])
                Y = self.nodes[i].Y * size[1] / float(self.old_size[1])
                self.nodes[i].pos = (X, Y)
            self.old_size = size
        
        
    def highlight_node(self, node):
        
        def highlight_upper_node(node):
            node.is_highlighted = True
            current_concept = self.cs[self.nodes.index(node)]
            
            for concept in self.cs.parents(current_concept):
                j = self.cs.index(concept)
                highlight_upper_node(self.nodes[j])
                
        def highlight_lower_node(node):
            node.is_highlighted = True
            current_concept = self.cs[self.nodes.index(node)]

            for concept in self.cs.children(current_concept):
                j = self.cs.index(concept)
                highlight_lower_node(self.nodes[j])
        
        node.is_highlighted = True
        current_concept = self.cs[self.nodes.index(node)]
        
        for concept in self.cs.parents(current_concept):
            j = self.cs.index(concept)
            highlight_upper_node(self.nodes[j])
            
        for concept in self.cs.children(current_concept):
            j = self.cs.index(current_concept)
            highlight_lower_node(self.nodes[j])
        
    def OnMouse(self, event):
        if event.LeftDown():
            (x, y) = (event.GetX(), event.GetY())
            for node in self.nodes:
                node.is_highlighted = False
            self.Refresh()
            for node in self.nodes:
                if node.hit_test(x, y):
                    self._dragged = node
                    self.highlight_node(node)
                    self._last_pos = (x, y)
                    is_breaked = True
                    break
        elif event.Dragging() or event.LeftUp():
            if self._dragged:
                (x, y) = self._last_pos
                dx = event.GetX() - x
                dy = event.GetY() - y
                new_xy = (self._dragged.X + dx, self._dragged.Y + dy)
                if self.TryDrag(new_xy):
                    self._dragged.pos = new_xy
                    self._last_pos = (event.GetX(),event.GetY())
                self.Refresh()
            if event.LeftUp():     
                self._dragged = None
        elif event.RightDown():
            (x, y) = (event.GetX(), event.GetY())
            for node in self.nodes:
                if node.hit_test(x, y):
                    for n in self.nodes:
                        n.is_highlighted = False
                    self.nodes.remove(node)
                    self.cs.remove(node.concept)
                    self.lines = []
                    for i in range(len(self.cs)):
                        for concept in self.cs.children(self.cs[i]):
                            j = self.cs.index(concept)
                            self.lines.append((self.nodes[i], self.nodes[j]))
                    break
            self.Refresh()
                
    def TryDrag(self, pos):
        concept = self._dragged.concept
        for child in self.cs.children(concept):
            i = self.cs.index(child)
            if pos[1] > self.nodes[i].Y:
                return False
        for parent in self.cs.parents(concept):
            i = self.cs.index(parent)
            if pos[1] < self.nodes[i].Y:
                return False
        return True
    
    def saveSVG(self, path):
        """docstring for saveSVG"""
        NODE_RADIUS = 14
        dcSource = wx.PaintDC(self)
        
        import pysvg
        s = pysvg.svg()
        
        sb = pysvg.ShapeBuilder()
        
        for line in self.lines:
            element = sb.createLine(line[0].X, 
                                    line[0].Y, 
                                    line[1].X, 
                                    line[1].Y,
                                    strokewidth=2,
                                    stroke="black")
            s.addElement(element)
        
        h_step = self._font_size
        font_style = pysvg.StyleBuilder()
        font_style.setFontFamily(fontfamily="Verdana")
        font_style.setFontSize("{0}".format(self._font_size))
        font_style.setFilling("black")
        
        for node in self.nodes:
            s.addElement(sb.createCircle(node.X, node.Y, NODE_RADIUS,
                            strokewidth=2, fill='#436EEA'))
            if len(node._t_labels) != 0:
                # TODO:
                _t_labels = node._t_labels

                rect_width = 0
                for i in range(len(_t_labels)):
                    lwidth, lheight, ldescent, el = \
                                    dcSource.GetFullTextExtent(_t_labels[i])
                    if lwidth > rect_width:
                        rect_width = lwidth * self._font_size / self._base_size
                
                horizontal_offset = rect_width / 2
                    
                # element = sb.createRect(node.X - rect_width / 2 - 3, 
                #                         node.Y - h_step * len(_t_labels) - NODE_RADIUS, 
                #                         rect_width + 6, 
                #                         h_step * len(_t_labels) + 2,
                #                         strokewidth=1,
                #                         stroke="black",
                #                         fill="white")
                # s.addElement(element)
 
                for i in range(len(_t_labels)):
                    t = pysvg.text(_t_labels[i], node.X - horizontal_offset,
                            node.Y - NODE_RADIUS - h_step * i - 5)
                    t.set_style(font_style.getStyle())
                    s.addElement(t)

            if len(node._b_labels) != 0:
                # TODO:
                _b_labels = node._b_labels        

                rect_width = 0
                for i in range(len(_b_labels)):
                    lwidth, lheight, ldescent, el = \
                                        dcSource.GetFullTextExtent(_b_labels[i])
                    if lwidth > rect_width:
                        rect_width = lwidth * self._font_size / self._base_size
                
                horizontal_offset = rect_width / 2

                # element = sb.createRect(node.X - rect_width / 2 - 3, 
                #                         node.Y + NODE_RADIUS - 2, 
                #                         rect_width + 6, 
                #                         h_step * len(_b_labels) + 2,
                #                         strokewidth=1,
                #                         stroke="black",
                #                         fill="white")
                # s.addElement(element)

                for i in range(len(_b_labels)):
                    t = pysvg.text(unicode(_b_labels[i]), node.X - horizontal_offset,
                            node.Y + NODE_RADIUS + h_step * (i + 0.8) + 5)
                    t.set_style(font_style.getStyle())
                    s.addElement(t)          
                            
        s.save(path)
    
    def saveSnapshot(self, path):
        dcSource = wx.PaintDC(self)
        
        # based largely on code posted to wxpython-users by Andrea Gavana 2006-11-08
        size = dcSource.Size

        # Create a Bitmap that will later on hold the screenshot image
        # Note that the Bitmap must have a size big enough to hold the screenshot
        # -1 means using the current default colour depth
        bmp = wx.EmptyBitmap(size.width, size.height)

        # Create a memory DC that will be used for actually taking the screenshot
        memDC = wx.MemoryDC()

        # Tell the memory DC to use our Bitmap
        # all drawing action on the memory DC will go to the Bitmap now
        memDC.SelectObject(bmp)

        # Blit (in this case copy) the actual screen on the memory DC
        # and thus the Bitmap
        memDC.Blit( 0, # Copy to this X coordinate
            0, # Copy to this Y coordinate
            size.width, # Copy this width
            size.height, # Copy this height
            dcSource, # From where do we copy?
            0, # What's the X offset in the original DC?
            0  # What's the Y offset in the original DC?
            )

        # Select the Bitmap out of the memory DC by selecting a new
        # uninitialized Bitmap
        memDC.SelectObject(wx.NullBitmap)

        img = bmp.ConvertToImage()
        img.SaveFile(path, wx.BITMAP_TYPE_PNG)
        
    def OnPrint(self, event):
        printData = wx.PrintData()
        printData.SetPaperId(wx.PAPER_LETTER)
        printData.SetPrintMode(wx.PRINT_MODE_PRINTER)
        pdd = wx.PrintDialogData(printData)
        printer = wx.Printer(pdd)
        printout = MyPrintout(self)

        if not printer.Print(self.parent, printout, True):
            wx.MessageBox("There was a problem printing.\nPerhaps your current printer is not set correctly?", "Printing", wx.OK)
        else:
            printData = wx.PrintData( printer.GetPrintDialogData().GetPrintData() )
        printout.Destroy()
        
class DiagramWindow(wx.Panel):
    
    def __init__(self, parent, id, filename, path):
        """docstring for __init__"""
        wx.Panel.__init__(self, parent, -1)
        self.canvas = MyCanvas(self, -1)
        
        self.toolBar = self.CreateToolBar()
        self.toolBar.Realize()
        self.filename = filename
        self.path = path
        self.canvas.SetConceptSystem(uread_xml(path))
        
    def CreateToolBar(self):
        tb = wx.ToolBar(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, 0, wx.EXPAND)
        sizer.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(sizer)

        tool = tb.AddLabelTool(wx.NewId(), "Save", images.GetBitmap("Save"),
                shortHelp="Save image")
        self.Bind(wx.EVT_TOOL, self.OnSave, tool)
        
        tool = tb.AddLabelTool(wx.NewId(), "Objects", 
                               images.GetBitmap("Dummy"),
                               shortHelp="Toggle extent label view")
        self.Bind(wx.EVT_TOOL, self.OnToggleExtentView, tool)
        
        tool = tb.AddLabelTool(wx.NewId(), "Attributes", 
                               images.GetBitmap("Dummy"),
                               shortHelp="Toggle intent label view")
        self.Bind(wx.EVT_TOOL, self.OnToggleIntentView, tool)
        
        tool = tb.AddLabelTool(wx.NewId(), "Increase font size", 
                               images.GetBitmap("Plus"),
                               shortHelp="Increase font size")
        self.Bind(wx.EVT_TOOL, self.OnIncreaseFontSize, tool)
        
        tool = tb.AddLabelTool(wx.NewId(), "Decrease font size", 
                               images.GetBitmap("Minus"),
                               shortHelp="Decrease font size")
        self.Bind(wx.EVT_TOOL, self.OnDecreaseFontSize, tool)
        
        tool = tb.AddLabelTool(wx.NewId(), "Print", 
                               images.GetBitmap("Dummy"),
                               shortHelp="Print")
        self.Bind(wx.EVT_TOOL, self.canvas.OnPrint, tool)
        
        tool = tb.AddLabelTool(wx.NewId(), "Store coordinates", 
                               images.GetBitmap("Dummy"),
                               shortHelp="Store coordinates")
        self.Bind(wx.EVT_TOOL, self.OnSaveXML, tool)

        return tb
        
    def OnIncreaseFontSize(self, event):
        """docstring for OnIncreaseFontSize"""
        self.canvas._font_size += 1
        self.canvas.Refresh()
        
    def OnDecreaseFontSize(self, event):
        if self.canvas._font_size - 1 > 4:
            self.canvas._font_size -= 1
            self.canvas.Refresh()
        
    def OnToggleExtentView(self, event):
        """docstring for OnToggleExtentView"""
        self.canvas.ChangeExtentLabelView()
        
    def OnToggleIntentView(self, event):
        """docstring for OnToggleIntentView"""
        self.canvas.ChangeIntentLabelView()
        
    def OnSave(self, event):
        head, tail = os.path.split(self.filename)
        default_file = "".join([tail[:-3], "png"])
        dlg = wx.FileDialog(self, "Choose a file name to save the image as a PNG to",
                            defaultDir = "",
                            defaultFile = default_file,
                            wildcard = "PNG files (*.png)|*.png|SVG files (*.svg)|*.svg",
                            style=wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            if dlg.GetFilterIndex() == 0:
                self.canvas.saveSnapshot(dlg.GetPath())
            else:
                self.canvas.saveSVG(dlg.GetPath())
        dlg.Destroy()
        
    def OnSaveXML(self, event):
        self.canvas.SaveCoordinates()
        write_xml(self.path, self.canvas.cs)
        
        
def find_own_objects(cs):
    """Return set of own objects for current concept"""
    own_objects = {}
    for con in cs:
        own_objects[con] = []
        for obj in con.extent:
            own_objects[con].append(obj)
            for sub_con in cs:
                if sub_con.extent < con.extent and\
                        obj in sub_con.extent:
                    own_objects[con].pop()
                    break
    return own_objects

def find_own_attributes(cs):
    """Return set of own attributes for current concept"""
    own_attributes = {}
    for con in cs:
        own_attributes[con] = []
        for attr in con.intent:
            own_attributes[con].append(attr)
            for sub_con in cs:
                if sub_con.intent < con.intent and\
                        attr in sub_con.intent:
                    own_attributes[con].pop()
                    break
    return own_attributes  
    
               
def get_coordinates(concept_system):
    import tempfile
    import os
    import fca
    temp_dot_path = tempfile.mktemp()
    temp_plain_path = tempfile.mktemp()
    
    coordinates = {}
    
    from fca.readwrite import uwrite_dot
    uwrite_dot(concept_system, temp_dot_path)
    
    try:
        dot_path = os.path.join(graphviz_path, "dot")
        subprocess.call([dot_path, "-Tplain", 
                        "-o{0}".format(temp_plain_path),
                        temp_dot_path])
    except:
        dot_path = os.path.join(graphviz_path, "dot.exe")
        subprocess.call([dot_path, "-Tplain", 
                        "-o{0}".format(temp_plain_path),
                        temp_dot_path])
    
    import codecs
    plain_dot_file = codecs.open(temp_plain_path, "r", "utf-8")
    
    for line in plain_dot_file:
        spl_line = line.split(" ")
        if spl_line[0] == "graph":
            canvas_width = float(spl_line[2])
            canvas_height = float(spl_line[3])
        elif spl_line[0] == "node":
            i = int(spl_line[1][1:])
            xy = (float(spl_line[2])/canvas_width, float(spl_line[3])/canvas_height)
            coordinates[concept_system[i]] = xy
    
    plain_dot_file.close()
    
    # now clean for ourselves
    os.unlink(temp_plain_path)
    os.unlink(temp_dot_path)
    
    return coordinates

class MyPrintout(wx.Printout):
    def __init__(self, canvas):
        wx.Printout.__init__(self)
        self.canvas = canvas

    def OnPrintPage(self, page):
        dc = self.GetDC()

        #-------------------------------------------
        # One possible method of setting scaling factors...

        maxX = self.canvas.getWidth()
        maxY = self.canvas.getHeight()

        # Let's have at least 50 device units margin
        marginX = 50
        marginY = 50

        # Add the margin to the graphic size
        maxX = maxX + (2 * marginX)
        maxY = maxY + (2 * marginY)

        # Get the size of the DC in pixels
        (w, h) = dc.GetSizeTuple()

        # Calculate a suitable scaling factor
        scaleX = float(w) / maxX
        scaleY = float(h) / maxY

        # Use x or y scaling factor, whichever fits on the DC
        actualScale = min(scaleX, scaleY)

        # Calculate the position on the DC for centering the graphic
        posX = (w - (self.canvas.getWidth() * actualScale)) / 2.0
        posY = (h - (self.canvas.getHeight() * actualScale)) / 2.0

        # Set the scale and origin
        dc.SetUserScale(actualScale, actualScale)
        dc.SetDeviceOrigin(int(posX), int(posY))

        #-------------------------------------------
        self.canvas.DoDrawing(dc)

        return True
          
if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = wx.Frame(parent=None, title="Test Window")
    win = DiagramWindow(frame, wx.ID_ANY)
    frame.Show()
    from fca import (Context, Concept, ConceptLattice)
    ct = [[True, False, False, True],\
          [True, False, True, False],\
          [False, True, True, True],\
          [False, True, True, True]]
    objs = ['1', '2', '3', '4']
    attrs = ['a', 'b', 'c', 'd']
    c = Context(ct, objs, attrs)
    cl = ConceptLattice(c)
    win.canvas.SetConceptSystem(cl)
    app.MainLoop()