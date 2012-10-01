# This program is written for Python 2.6-2.7.
# It requires the wxpython library
# It allows the user to load an image and mark the coordinates of objects
# (cells for my uses), as well as moving the image around using click and 
# drag. The coordinates of cells in the image can then be saved.
# Examples of these files in both .mat and .txt format, with the accompanying
# images, are in the associated folders in the github distribution.

# I want to emphasize: this is an alpha version. The code needs to be cleaned 
# up. I wrote this years ago, and I know the overall program design could be 
# dramatically improved.

# Current todo:
# Reduce dependence on global variables.
# Break things up into more component parts.
# Fix whitespace on side of screen on high resolution monitors
# Add more complete documentation.
# Improve data redraw after dialog window opened or data point deleted. 
# Currently you need to move the image to get a full redraw.

# I plan to clean this up soon, but I have a ton of other things to learn 
# that are critical for my immediate career goals.
# Please look at other files in my Github account to get a sense of my current 
# programming approach.

############################################################################## 
# These are program variables to be manipulated by a slightly savvy user.
# Some day, I would like to make them more easily manipulated via the GUI.

# Library imports
import wx
import csv

# Determine whether image being studied is scaled
# This is used for achieving consistent output between scaled and unscaled 
# images
# I use unscaled as the variable instead of scaled because it should be the 
# most common format
unscaled_image = False

# Default cell type is none (type 0).
# Neuron = 1, glia = 2, blood vessel cell = 3.
cell_type = 0

# Drawing mode. The default, 1, is boxes
# Switch to point drawing using the menu system
draw_type = 1

# Set default scaled image size very small so it works with most screens
# I will be looking into libraries to get the current screen resolution
scale_bmp_width = 640
scale_bmp_height = 480

# Default drawing object parameters.
rect_line_width = 1
cross_width = 1
cross_length = 15

# Set pen colors. 
pen_color = ("BLACK")
pen_color_0 = "BLACK"
pen_color_1 = "BLUE"
pen_color_2 = "GREEN"
pen_color_3 = "PURPLE"

# Starting cell number, used to locate counting records
cell_counter = 0

# All arrays used have a blank header line because I found it easiest with my 
# limited Python skills when I wrote this - DO NOT CHANGE
cell_record, cell_record_scale = [], []
cell_record_pt, cell_record_pt_scale = [], []

##############################################################################

# This is the main class in which cell marking and image movement takes place.
class CellCounter(wx.Frame):
    
    def __init__(self, parent, mysize):
        wx.Frame.__init__(self, parent, wx.ID_ANY, size=mysize, 
                          title="Cell Counter Alpha")
        # Used to add locations
        self.points = []
        self.scaledpoints = []
  
##############################################################################
# menu setup
        
        # create menu, statusbar
        status = self.CreateStatusBar()
        menu_bar = wx.MenuBar()
        file_menu = wx.Menu()
        cell_type_select_menu = wx.Menu()
        count_select_menu = wx.Menu()
        marker_ctrl_menu = wx.Menu()
        image_ctrl_menu = wx.Menu()
        

        # assign first menu values
        FILE_SCALED_OPEN = 101
        FILE_UNSCALED_OPEN = 102
        EXPORT_TXT_ALL = 103
        EXPORT_TXT_NEURON = 104
        EXPORT_TXT_GLIA = 105
        EXPORT_TXT_BV = 106
        IMPORT_TXT = 107

        # assign second menu values
        NEURON_SELECT = 201
        GLIA_SELECT = 202
        BV_SELECT = 203

        # assign third menu values
        DOT_SWITCH = 301
        RECT_SWITCH = 302

        # assign fourth menu values
        RECTSIZE_SET = 401
        CROSSWIDE_SET = 402
        CROSSLONG_SET = 403

        # assign fifth menu values
        IMAGEMOVE_ON = 501
        IMAGEMOVE_OFF = 502

        # create menu contents
        # menu 1 - file handling menu
        file_menu.Append(FILE_SCALED_OPEN, "Open Scaled Image",
                        "Open an image file and scale it")
        file_menu.Append(FILE_UNSCALED_OPEN, "Open Unscaled Image",
                        "Open an image file without scaling")
        file_menu.Append(EXPORT_TXT_ALL, "Save all data",
                        "Export tab-delimited .txt file with all data")
        file_menu.Append(EXPORT_TXT_NEURON, "Save neuron data",
                        "Export tab-delimited .txt file with neuronal data")
        file_menu.Append(EXPORT_TXT_GLIA, "Save glia data",
                        "Export tab-delimited .txt file with glial data")
        file_menu.Append(EXPORT_TXT_BV, "Save BV data",
                        "Export tab-delimited .txt file with bv cell data")
        file_menu.Append(IMPORT_TXT, "Import data from .txt",
                        "Import .txt file")
        
        self.Bind(wx.EVT_MENU, self.scaled_image_open, id=FILE_SCALED_OPEN)
        self.Bind(wx.EVT_MENU, self.unscaled_image_open, id=FILE_UNSCALED_OPEN)
        self.Bind(wx.EVT_MENU, self.save_txt_all, id=EXPORT_TXT_ALL)
        self.Bind(wx.EVT_MENU, self.save_neuron, id=EXPORT_TXT_NEURON)
        self.Bind(wx.EVT_MENU, self.save_glia, id=EXPORT_TXT_GLIA)
        self.Bind(wx.EVT_MENU, self.save_bv, id=EXPORT_TXT_BV)
        self.Bind(wx.EVT_MENU, self.import_txt, id=IMPORT_TXT)


        # menu 2 - counting target selection menu
        cell_type_select_menu.Append(NEURON_SELECT, "Neurons",
                             "Mark neurons")
        cell_type_select_menu.Append(GLIA_SELECT, "Glia", 
                             "Mark glia")
        cell_type_select_menu.Append(BV_SELECT, "Blood Vessel",
                             "Mark blood vessel cells")
        
        self.Bind(wx.EVT_MENU, self.neuron_button, id=NEURON_SELECT)
        self.Bind(wx.EVT_MENU, self.glia_button, id=GLIA_SELECT)
        self.Bind(wx.EVT_MENU, self.bv_button, id=BV_SELECT)

        # menu 3 - counting methods menu
        count_select_menu.Append(DOT_SWITCH, "Point Mode",
                               "Mark objects with a single point")
        count_select_menu.Append(RECT_SWITCH, "Rect Mode",
                               "Mark objects with a surrounding box")
        
        self.Bind(wx.EVT_MENU, self.dot_switch, id=DOT_SWITCH)
        self.Bind(wx.EVT_MENU, self.rect_switch, id=RECT_SWITCH)

        # menu 4 - pen color and cursor control tools
        marker_ctrl_menu.Append(RECTSIZE_SET, "Change box size",
                              "Change thickness of tracing lines")
        marker_ctrl_menu.Append(CROSSWIDE_SET,"Change cross width",
                              "Change thickness of cursor lines")
        marker_ctrl_menu.Append(CROSSLONG_SET, "Change cross length",
                              "Change length of cursor lines")
        
        self.Bind(wx.EVT_MENU, self.rect_size_set, id=RECTSIZE_SET)
        self.Bind(wx.EVT_MENU, self.cross_wide_set, id=CROSSWIDE_SET)
        self.Bind(wx.EVT_MENU, self.cross_long_set, id=CROSSLONG_SET)
        
        # menu 5 - movement and macro view menu
        image_ctrl_menu.Append(IMAGEMOVE_ON, "Move Image", 
                             "Turn on image move mode and turn off marking")
        image_ctrl_menu.Append(IMAGEMOVE_OFF, "Mark Objects",
                             "Turn on marking and turn off image move")
        
        self.Bind(wx.EVT_MENU, self.image_move_on, id=IMAGEMOVE_ON)
        self.Bind(wx.EVT_MENU, self.image_move_off, id=IMAGEMOVE_OFF)
        
        # menu headers
        menu_bar.Append(file_menu, "File")
        menu_bar.Append(cell_type_select_menu, "Select Pop")
        menu_bar.Append(count_select_menu, "Count Objects")
        menu_bar.Append(marker_ctrl_menu, "Change Markers")
        menu_bar.Append(image_ctrl_menu, "Move Image")
        self.SetMenuBar(menu_bar)
              
        # mouseclick setup - default is rectangle counting mode
        self.Bind(wx.EVT_LEFT_DOWN, self.draw_rect)
        self.Bind(wx.EVT_RIGHT_DOWN, self.erase_rect)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_ENTER_WINDOW, self.create_crosshair)

        # keyboard setup for fast cell type switching
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        # load default frame
        self.SetBackgroundColour("WHITE")
        self.Centre()
        self.Show(True)
        self.buffer = wx.EmptyBitmap(1600, 1200) # draw to this
        image_buffer = wx.EmptyBitmap(1600, 1200) # for image repair/move
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.Clear() # black window otherwise
        dc.SetPen(wx.Pen(pen_color, 2, wx.SOLID))


##############################################################################
# functions for program below this point

    def scaled_image_open(self, event):
        global scale_bmp_width
        global scale_bmp_height
        global unscaled_image
        global image_buffer
        
        self.photoTxt = wx.TextCtrl(self, size=(200,-1))
        wildcard = "JPEG files (*.jpg)|*.jpg"
        dialog = wx.FileDialog(None, "Choose a file",
                               wildcard=wildcard,
                               style=wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.photoTxt.SetValue(dialog.GetPath())
        dialog.Destroy()
        path = self.photoTxt.GetValue()
        self.photoTxt.Destroy()
        
        bmp=wx.Image(path, wx.BITMAP_TYPE_ANY)
        # this is the wxPython drawing surface/canvas
        scale_bmp_width = float(bmp.GetWidth())
        scale_bmp_height = float(bmp.GetHeight())
        bmp_scale = bmp.Scale(scale_bmp_width / scale_bmp_height * 
                              screen_size[1] * .80,screen_size[1] * .80)
        bmp2 = wx.BitmapFromImage(bmp_scale)
        image_buffer = wx.EmptyBitmap(scale_bmp_width / scale_bmp_height * 
                                     screen_size[1] * .80,
                                     screen_size[1]*.80)
        dc2 = wx.BufferedDC(wx.MemoryDC(), image_buffer)
        dc2.DrawBitmap(bmp2, 0, 0, True)
        self.buffer = wx.EmptyBitmap(scale_bmp_width / scale_bmp_height * 
                                     screen_size[1] * .80,
                                     screen_size[1] * .80)
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.DrawBitmap(bmp2, 0, 0, True)
        unscaled_image = False
        self.Refresh()

    def unscaled_image_open(self, event):
        global scale_bmp_width
        global scale_bmp_height
        global unscaled_image
        global current_loc
        global image_buffer
        
        self.photoTxt = wx.TextCtrl(self, size=(200,-1))
        wildcard = "JPEG files (*.jpg)|*.jpg"
        dialog = wx.FileDialog(None, "Choose a file",
                               wildcard=wildcard,
                               style=wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.photoTxt.SetValue(dialog.GetPath())
        dialog.Destroy()
        path = self.photoTxt.GetValue()
        self.photoTxt.Destroy()
        
        bmp=wx.Image(path, wx.BITMAP_TYPE_ANY)
        scale_bmp_width = float(bmp.GetWidth())
        scale_bmp_height = float(bmp.GetHeight())
        bmp2 = wx.BitmapFromImage(bmp)
        image_buffer = wx.EmptyBitmap(scale_bmp_width, scale_bmp_height)
        dc2 = wx.BufferedDC(wx.MemoryDC(), image_buffer)
        dc2.DrawBitmap(bmp2, 0, 0, True)
        self.buffer = wx.EmptyBitmap(scale_bmp_width,scale_bmp_height)
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.DrawBitmap(bmp2, 0, 0, True)

        #upper left coordinates of picture
        current_loc = [0,0]
        unscaled_image = True
        self.Refresh()
        
    def draw_rect(self, event):
        global cell_record
        global cell_record_scale
        global cell_counter
        
        self.points.append(event.GetPosition())
        x1, y1 = self.points[0]
        if len(self.points) == 1:
            dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
            dc.SetPen(wx.Pen(pen_color, rect_line_width, wx.SOLID))
            dc.DrawLine(x1, y1, (x1 + 1), (y1 + 1))
            self.Update()
        if len(self.points) == 2:
            dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
            dc.SetPen(wx.Pen(pen_color, rect_line_width, wx.SOLID))
            x1, y1 = self.points[0]
            x2, y2 = self.points[1]
            dc.DrawLine(x1, y1, x1, y2)
            dc.DrawLine(x1, y2, x2, y2)
            dc.DrawLine(x2, y2, x2, y1)
            dc.DrawLine(x2, y1, x1, y1)
            self.Update()
            celladd = [x1, y1, x2, y2, cell_type]
            if not cell_record:
                cell_record = []
            cell_record.append(celladd)
            
            # return coords to original image scale for output if image has 
            # been rescaled
            if unscaled_image:
                x1_scaled = x1 + current_loc[0]
                y1_scaled = y1 + current_loc[1]
                x2_scaled = x2 + current_loc[0]
                y2_scaled = y2 + current_loc[1]
                
            if not unscaled_image:
                x1_scaled = int(x1 * scale_bmp_width / 
                              (scale_bmp_width / scale_bmp_height * 
                               screen_size[1] * .80))
                y1_scaled = int(y1 * scale_bmp_height /(screen_size[1] * .80))
                x2_scaled = int(x2 * scale_bmp_width /(scale_bmp_width / 
                                                    scale_bmp_height * 
                                                    screen_size[1] * .80))
                y2_scaled = int(y2 * scale_bmp_height /(screen_size[1]*.80))
    
            cell_record_scale.append([x1_scaled, y1_scaled, x2_scaled, 
                                      y2_scaled, cell_type])
            print cell_record_scale
            cell_counter += 1
            self.points = []

    def erase_rect(self, event):
        global cell_record
        global cell_counter
        global cell_record_scale

        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc2 = wx.BufferedDC(wx.MemoryDC(), image_buffer)
        
        cutrow = len(cell_record_scale) - 1

        if unscaled_image:
            x1 = cell_record_scale[cutrow][0] - current_loc[0]
            y1 = cell_record_scale[cutrow][1] - current_loc[1]
            x2 = cell_record_scale[cutrow][2] - current_loc[0]
            y2 = cell_record_scale[cutrow][3] - current_loc[1]
            
            #replace left side
            dc.Blit(x1 - 1 - (rect_line_width / 2), 
                    y1 - 1 - (rect_line_width / 2), (rect_line_width + 2), 
                    (y2 - y1) + 2 + rect_line_width, dc2, 
                    x1 - 1 - (rect_line_width / 2) + current_loc[0], 
                    y1 - 1 - rect_line_width / 2 + current_loc[1],
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
            #replace top side
            dc.Blit(x1 - 1 - (rect_line_width / 2), 
                    y1 - 1 - (rect_line_width / 2), 
                    (x2 - x1) + 2 + rect_line_width, (rect_line_width + 2),
                    dc2, x1 - 1 - (rect_line_width / 2) + current_loc[0], 
                    y1 - 1 - (rect_line_width / 2) + current_loc[1],
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
            #replace right side
            dc.Blit(x2 - 1 - (rect_line_width / 2), 
                    y1 - 1 - (rect_line_width / 2), (rect_line_width + 2), 
                    (y2 - y1) + 2 + rect_line_width, dc2, 
                    x2 - 1 - (rect_line_width / 2) + current_loc[0], 
                    y1 - 1 - (rect_line_width / 2) + current_loc[1],
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
            #replace bottom side
            dc.Blit(x1 - 1 - (rect_line_width / 2), 
                    y2 - 1 - (rect_line_width / 2),
                    (x2 - x1) + 2 + rect_line_width, (rect_line_width + 2),
                    dc2, x1 - 1 - (rect_line_width / 2) + current_loc[0], 
                    y2 - 1 - (rect_line_width / 2) + current_loc[1],
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
            
        if not unscaled_image:
            x1 = cell_record[cutrow][0]
            y1 = cell_record[cutrow][1]
            x2 = cell_record[cutrow][2]
            y2 = cell_record[cutrow][3]
            
            #replace left side
            dc.Blit(x1 - 1 - (rect_line_width / 2), 
                    y1 - 1 - (rect_line_width / 2), (rect_line_width + 2), 
                    (y2 - y1) + 2 + rect_line_width, dc2, 
                    x1 - 1 - (rect_line_width / 2), 
                    y1 - 1 - (rect_line_width / 2),
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
            #replace top side
            dc.Blit(x1 - 1 - (rect_line_width / 2), 
                    y1 - 1 - (rect_line_width / 2), 
                    (x2 - x1) + 2 + rect_line_width, 
                    (rect_line_width + 2), dc2, 
                    x1 - 1 - (rect_line_width / 2), 
                    y1 - 1 - (rect_line_width / 2),
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
            #replace right side
            dc.Blit(x2 - 1 - (rect_line_width / 2), 
                    y1 - 1 - (rect_line_width / 2), (rect_line_width + 2), 
                    (y2 - y1) + 2 + rect_line_width, dc2, 
                    x2 - 1 - (rect_line_width / 2), 
                    y1 - 1 - (rect_line_width / 2),
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
            #replace bottom side
            dc.Blit(x1 - 1 - (rect_line_width / 2), 
                    y2 - 1 - (rect_line_width / 2), 
                    (x2 - x1) + 2 + rect_line_width, (rect_line_width + 2),
                    dc2, x1 - 1 - (rect_line_width / 2), 
                    y2 - 1 - (rect_line_width / 2),
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
             
        self.Update()     
        cell_record = cell_record[:-1]
        cell_record_scale = cell_record_scale[:-1]
        cell_counter -= 1

    def draw_dot(self, event):
        global cell_record_pt
        global cell_record_pt_scale
        global cell_counter
        
        self.points.append(event.GetPosition())
        x1, y1 = self.points[0]
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.SetPen(wx.Pen(pen_color, cross_width, wx.SOLID))
        dc.DrawLine(x1 - (cross_length / 2), y1, x1 + (cross_length / 2), y1)
        dc.DrawLine(x1, y1 - (cross_length / 2), x1, y1 + (cross_length / 2))
        self.Update()
        celladddot = [x1, y1, cell_type]
        cell_record_pt.append(celladddot)            
        # Return coords to original image scale for output 
        # if image has been rescaled.
        if unscaled_image:
            x1_scaled = x1 + current_loc[0]
            y1_scaled = y1 + current_loc[1]
        if not unscaled_image:
            x1_scaled = int(x1 * scale_bmp_width / 
                          (scale_bmp_width / 
                           scale_bmp_height * screen_size[1] * .80))
            y1_scaled = int(y1 * scale_bmp_height / (screen_size[1]*.80))

        cell_record_pt_scale.append([x1_scaled, y1_scaled, cell_type])
        print cell_record_pt_scale
        cell_counter += 1
        self.points = []

    def erase_dot(self, event):
        global cell_record_pt
        global cell_record_pt_scale
        global cell_counter

        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc2 = wx.BufferedDC(wx.MemoryDC(), image_buffer)
        
        cutrow = len(cell_record_pt_scale) - 1
        if unscaled_image and cell_record_pt_scale:
            x1 = cell_record_pt_scale[cutrow][0] - current_loc[0]
            y1 = cell_record_pt_scale[cutrow][1] - current_loc[1]
            # replace horizontal line
            dc.Blit(x1 - 1 - (cross_length / 2), y1 - 1 - (cross_width / 2), 
                    (cross_length + 2), (cross_width + 2),
                    dc2, x1 - 1 - (cross_length / 2) + current_loc[0],
                    y1 - 1 - (cross_width / 2) + current_loc[1],
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
            # replace vertical line
            dc.Blit(x1 - 1 - (cross_width / 2), y1 - 1 - (cross_length / 2), 
                    (cross_width + 2), (cross_length + 2),
                    dc2, x1 - 1 - (cross_width / 2) + current_loc[0], 
                    y1 - 1 - (cross_length / 2) + current_loc[1],
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
            
        if not unscaled_image and cell_record_pt_scale:
            x1 = cell_record_pt[cutrow][0]
            y1 = cell_record_pt[cutrow][1]
            # replace horizontal line
            dc.Blit(x1 - 1 - (cross_length / 2), y1 - 1 - (cross_width / 2),
                    (cross_length + 2), (cross_width + 2),
                    dc2, x1 - (cross_length / 2), y1 - 1 - (cross_width / 2),
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)
            # replace vertical line
            dc.Blit(x1 - 1 - (cross_width / 2), y1 - 1 - (cross_length / 2), 
                    (cross_width + 2), (cross_length + 2),
                    dc2, x1 - 1 - (cross_width / 2), 
                    y1 - 1 - (cross_length / 2),
                    rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)

        self.Update()
        if cell_record_pt and cell_record_pt_scale:     
            cell_record_pt = cell_record_pt[:-1]
            cell_record_pt_scale = cell_record_pt_scale[:-1]
            cell_counter -= 1

    def MouseMove(self, event):
        global self_loc
        
        self_loc = []
        self_loc.append(event.GetPosition())
        self.Bind(wx.EVT_LEFT_UP, self.MouseStopRedraw)

    def MouseStopRedraw(self, event):
        # Note that this is only implemented for unscaled images!  
        # Scaled images fit on a single screen and don't require movement.
        global self_loc
        global current_loc
        global cell_record_scale
        global cell_record_pt_scale
        global pen_color

        # import current image (dc), full image stored in memory (dc2)
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.Clear()
        dc2 = wx.BufferedDC(wx.MemoryDC(), image_buffer)

        # get location of movement
        self_loc.append(event.GetPosition())
        x1,y1 = self_loc[0]
        x2,y2 = self_loc[1]
        self_loc = []
        current_loc[0] = current_loc[0] + (x1 - x2)
        current_loc[1] = current_loc[1] + (y1 - y2)

        # redraw the correct image
        dc.Blit(0, 0, 1600, 1200, dc2, current_loc[0], current_loc[1],
                rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)

        # move rectangle objects
        if len(cell_record_scale) > 0:
            length = len(cell_record_scale) - 1
            retrace = 0
            while retrace <= length:
                x1 = cell_record_scale[retrace][0] - current_loc[0]
                y1 = cell_record_scale[retrace][1] - current_loc[1]
                x2 = cell_record_scale[retrace][2] - current_loc[0]
                y2 = cell_record_scale[retrace][3] - current_loc[1]
                cell_type = cell_record_scale[retrace][4]
                if cell_type == 0:
                    pen_color = pen_color_0
                if cell_type == 1:
                    pen_color = pen_color_1
                if cell_type == 2:
                    pen_color = pen_color_2
                if cell_type == 3:
                    pen_color = pen_color_3
                dc.SetPen(wx.Pen(pen_color, rect_line_width, wx.SOLID))
                dc.DrawLine(x1, y1, x1, y2)
                dc.DrawLine(x1, y2, x2, y2)
                dc.DrawLine(x2, y2, x2, y1)
                dc.DrawLine(x2, y1, x1, y1)
                retrace += 1
        
        # move dot objects
        if len(cell_record_pt_scale) > 0:
            length = len(cell_record_pt_scale) - 1
            retrace = 0
            while retrace <= length:
                x1 = cell_record_pt_scale[retrace][0] - current_loc[0]
                y1 = cell_record_pt_scale[retrace][1] - current_loc[1]
                cell_type = cell_record_pt_scale[retrace][2]
                if cell_type == 0:
                    pen_color = pen_color_0
                if cell_type == 1:
                    pen_color = pen_color_1
                if cell_type == 2:
                    pen_color = pen_color_2
                if cell_type == 3:
                    pen_color = pen_color_3
                dc.SetPen(wx.Pen(pen_color, cross_width, wx.SOLID))
                dc.DrawLine(x1- (cross_length / 2), y1, 
                            x1 + (cross_length / 2), y1)
                dc.DrawLine(x1, y1 - (cross_length / 2), x1, 
                            y1 + (cross_length / 2))
                retrace += 1
                
        self.Update()

        self.Bind(wx.EVT_LEFT_DOWN, self.MouseMove)

    def OnKeyDown(self, event):
        global pen_color
        global cell_type
        code = event.GetKeyCode()
        if code == 49:
            pen_color = ("BLUE")
            cell_type = 1
        if code == 50:
            pen_color = ("GREEN")
            cell_type = 2
        if code == 51:
            pen_color = ("PURPLE")
            cell_type = 3
        else:
            pass
        
    def neuron_button(self, event):
        global pen_color
        global cell_type
        pen_color = ("BLUE")
        cell_type = 1

    def glia_button(self, event):
        global pen_color
        global cell_type
        pen_color = ("GREEN")
        cell_type = 2

    def bv_button(self, event):
        global pen_color
        global cell_type
        pen_color = ("PURPLE")
        cell_type = 3

    def save_txt_all(self, event):
        global cell_record
        global cell_record_scale
        global cell_counter
        
        self.saveTxt = wx.TextCtrl(self, size=(200,-1))
        dialog = wx.FileDialog(None, "Enter", style=wx.SAVE)
        if dialog.ShowModal() == wx.ID_OK:
            self.saveTxt.SetValue(dialog.GetPath())
        dialog.Destroy()
        path = self.saveTxt.GetValue()
        self.saveTxt.Destroy()

        # Export rectangle tracing data. 
        if cell_record_scale:
            output_writer = csv.writer(open(path, 'wb'), delimiter='\t', 
                                       quotechar='|', 
                                       quoting=csv.QUOTE_MINIMAL)
            output_writer.writerow(["x1", "y1", "x2", "y2", "cell type"])
            for row in cell_record_scale:
                output_writer.writerow(row)
                
        # Export dot tracing data.
        if cell_record_pt_scale:
            output_writer.writerow(["x1", "y1", "cell type"])
            for row in cell_record_pt_scale:
                output_writer.writerow(row)
                
    def save_txt_cell_type(self, save_cell_type=0):
        global cell_record
        
        self.saveTxt = wx.TextCtrl(self, size=(200, -1))
        dialog = wx.FileDialog(None, "Enter", style=wx.FD_SAVE)
        if dialog.ShowModal() == wx.ID_OK:
            self.saveTxt.SetValue(dialog.GetPath())
        dialog.Destroy()
        path = self.saveTxt.GetValue()
        self.saveTxt.Destroy()

        # export rectangle tracings
        if cell_record_scale:
            output_writer = csv.writer(open(path, 'wb'), delimiter='\t', 
                                       quotechar='|',
                                       quoting=csv.QUOTE_MINIMAL)
            output_writer.writerow(["x1", "y1", "x2", "y2"])
            for row in cell_record_scale:
                if row[4] == save_cell_type:
                    output_writer.writerow(row)
                    
        # export dot tracings
        if cell_record_pt_scale:
            output_writer.writerow(["x1", "y1", "cell type"])
            for row in cell_record_pt_scale:
                if row[2] == save_cell_type:
                    output_writer.writerow(row)
    
    def save_neuron(self, event):
        self.save_txt_cell_type(save_cell_type=1)
        
    def save_glia(self, event):
        self.save_txt_cell_type(save_cell_type=2)  
          
    def save_bv(self, event):
        self.save_txt_cell_type(save_cell_type=3)                

    def import_txt(self, event):
        global cell_record_scale
        global cell_record_pt_scale
        global cell_record

        # UNFINISHED need to clear image of current points
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc2 = wx.BufferedDC(wx.MemoryDC(), image_buffer)
        
        self.loadTxt = wx.TextCtrl(self, size=(200,-1))
        dialog = wx.FileDialog(None, "Enter", style=wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.loadTxt.SetValue(dialog.GetPath())
        dialog.Destroy()
        path = self.loadTxt.GetValue()
        self.loadTxt.Destroy()
        raw_read = csv.reader(open(path, 'rb'), delimiter='\t', 
                              quotechar='|',
                              quoting=csv.QUOTE_MINIMAL)
        cell_record, cell_record_scale = [], []
        cell_record_pt, cell_record_pt_scale = [], []
        for row in raw_read:
            for index, coord in enumerate(row):
                try:
                    row[index] = int(coord)
                except:
                    pass
            if row[0] != 'x1':
                if len(row) == 5:
                    cell_record_scale.append(row)
                if len(row) == 3:
                    cell_record_pt_scale.append(row)

        # redraw a clean image
        dc.Blit(0, 0, 1600, 1200, dc2, current_loc[0], current_loc[1],
                rop=wx.COPY, useMask=False, xsrcMask=-1, ysrcMask=-1)

        # draw rectangle objects
        if cell_record_scale:
            cellnumber = len(cell_record_scale)
            drawcounter = 0
            
            if unscaled_image:
                cell_record = cell_record_scale
                while drawcounter < cellnumber:
                    x1 = cell_record_scale[drawcounter][0] - current_loc[0]
                    y1 = cell_record_scale[drawcounter][1] - current_loc[1]
                    x2 = cell_record_scale[drawcounter][2] - current_loc[0]
                    y2 = cell_record_scale[drawcounter][3] - current_loc[1]
                    cell_type = cell_record_scale[drawcounter][4]
                    if cell_type == 0:
                        pen_color = pen_color_0
                    if cell_type == 1:
                        pen_color = pen_color_1
                    if cell_type == 2:
                        pen_color = pen_color_2
                    if cell_type == 3:
                        pen_color = pen_color_3
                    dc.SetPen(wx.Pen(pen_color, rect_line_width, wx.SOLID))
                    dc.DrawLine(x1, y1, x1, y2)
                    dc.DrawLine(x1, y2, x2, y2)
                    dc.DrawLine(x2, y2, x2, y1)
                    dc.DrawLine(x2, y1, x1, y1)
                    drawcounter += 1
                    
            if not unscaled_image:                 
                while drawcounter < cellnumber:
                    # convert cell_record_scaled to cell_record 
                    x1 = cell_record_scale[drawcounter][0]
                    y1 = cell_record_scale[drawcounter][1]
                    x2 = cell_record_scale[drawcounter][2]
                    y2 = cell_record_scale[drawcounter][3]
                    cell_type = cell_record_scale[drawcounter][4]
                    x1_scaled_down = int(x1 / (scale_bmp_width / 
                                             (scale_bmp_width / 
                                              scale_bmp_height *
                                               screen_size[1] * .80)))
                    y1_scaled_down = int(y1 / (scale_bmp_height / 
                                             (screen_size[1] * .80)))
                    x2_scaled_down = int(x2 / (scale_bmp_width / 
                                             (scale_bmp_width / 
                                              scale_bmp_height * 
                                              screen_size[1] * .80)))
                    y2_scaled_down = int(y2 / (scale_bmp_height / 
                                             (screen_size[1] * .80)))
                    cell_record.append([x1_scaled_down, y1_scaled_down,
                                               x2_scaled_down, y2_scaled_down, 
                                               cell_type]) 
                    
                    #draw rescaled cell_record
                    if cell_type == 0:
                        pen_color = pen_color_0
                    if cell_type == 1:
                        pen_color = pen_color_1
                    if cell_type == 2:
                        pen_color = pen_color_2
                    if cell_type == 3:
                        pen_color = pen_color_3
                    dc.SetPen(wx.Pen(pen_color, rect_line_width, wx.SOLID))
                    dc.DrawLine(x1_scaled_down, y1_scaled_down, 
                                x1_scaled_down, y2_scaled_down)
                    dc.DrawLine(x1_scaled_down, y2_scaled_down, 
                                x2_scaled_down, y2_scaled_down)
                    dc.DrawLine(x2_scaled_down, y2_scaled_down, 
                                x2_scaled_down, y1_scaled_down)
                    dc.DrawLine(x2_scaled_down, y1_scaled_down, 
                                x1_scaled_down, y1_scaled_down)
                    drawcounter += 1
           
        # Draw dot objects
        if cell_record_pt_scale:
            cellnumber = len(cell_record_pt_scale)
            drawcounter = 0
    
            if unscaled_image:
                cell_record_pt = cell_record_pt_scale
                while drawcounter < cellnumber:
                    x1 = cell_record_pt_scale[drawcounter][0] - current_loc[0]
                    y1 = cell_record_pt_scale[drawcounter][1] - current_loc[1]
                    cell_type = cell_record_pt_scale[drawcounter][2]
                    if cell_type == 0:
                        pen_color = pen_color_0
                    if cell_type == 1:
                        pen_color = pen_color_1
                    if cell_type == 2:
                        pen_color = pen_color_2
                    if cell_type == 3:
                        pen_color = pen_color_3
                    dc.SetPen(wx.Pen(pen_color, 1, wx.SOLID))
                    dc.DrawLine(x1 - 5, y1, x1 + 5, y1)
                    dc.DrawLine(x1, y1 - 5, x1, y1 + 5)
                    drawcounter += 1
                    
            if not unscaled_image:
                while drawcounter < cellnumber:
                    # Convert cellscaled to cell record 
                    x1 = cell_record_pt_scale[drawcounter][0]
                    y1 = cell_record_pt_scale[drawcounter][1]
                    cell_type = cell_record_pt_scale[drawcounter][2]
                    x1_scaled_down = int(x1 / (scale_bmp_width / 
                                            (scale_bmp_width / 
                                             scale_bmp_height * 
                                             screen_size[1] * .80)))
                    y1_scaled_down = int(y1 / (scale_bmp_height / 
                                             (screen_size[1] * .80)))
                    cell_record_pt.append([x1_scaled_down, y1_scaled_down, 
                                                  cell_type]) 
                    
                    # Draw rescaled cell record
                    if cell_type == 0:
                        pen_color = pen_color_0
                    if cell_type == 1:
                        pen_color = pen_color_1
                    if cell_type == 2:
                        pen_color = pen_color_2
                    if cell_type == 3:
                        pen_color = pen_color_3
                    dc.SetPen(wx.Pen(pen_color, 1, wx.SOLID))
                    dc.DrawLine(x1_scaled_down - 5, y1_scaled_down, 
                                x1_scaled_down + 5, y1_scaled_down)
                    dc.DrawLine(x1_scaled_down, y1_scaled_down - 5, 
                                x1_scaled_down, y1_scaled_down + 5)
                    drawcounter += 1

        self.Update() 
                   
    def rect_switch(self, event):
        global draw_type
        self.Bind(wx.EVT_LEFT_DOWN, self.draw_rect)
        self.Bind(wx.EVT_RIGHT_DOWN, self.erase_rect)
        draw_type = 1
        
    def dot_switch(self, event):
        global draw_type
        self.Bind(wx.EVT_LEFT_DOWN, self.draw_dot)
        self.Bind(wx.EVT_RIGHT_DOWN, self.erase_dot)
        draw_type = 2

    def image_move_on(self, event):
        global unscaled_image
        if unscaled_image:
            self.Bind(wx.EVT_LEFT_DOWN, self.MouseMove)

    def image_move_off(self, event):
        global draw_type
        if draw_type == 1:
            self.Bind(wx.EVT_LEFT_DOWN, self.draw_rect)
        if draw_type == 2:
            self.Bind(wx.EVT_LEFT_DOWN, self.draw_dot)
        self.Bind(wx.EVT_LEFT_UP, self.does_nothing)

    def rect_size_set(self, event):
        global rect_line_width

        inputcapture = wx.TextEntryDialog(None, 
                                          "Rectangle draw width in pixels", 
                                          "Set Rectangle Width",
                                          defaultValue=str(rect_line_width), 
                                          style=wx.OK | wx.CANCEL)
        inputcapture.Show()
        if inputcapture.ShowModal() == wx.ID_OK:
            rect_line_width = int(inputcapture.GetValue())
        else:
            pass
        
    def cross_wide_set(self, event):
        global cross_width

        inputcapture = wx.TextEntryDialog(None, 
                                          "Cross marker width in pixels", 
                                          "Set Marker Width",
                                          defaultValue=str(cross_width), 
                                          style=wx.OK | wx.CANCEL)
        inputcapture.Show()
        if inputcapture.ShowModal() == wx.ID_OK:
            cross_width = int(inputcapture.GetValue())
        else:
            pass

    def cross_long_set(self, event):
        global cross_length

        inputcapture = wx.TextEntryDialog(None, 
                                          "Cross marker length in pixels",
                                          "Set Marker Width", 
                                          defaultValue=str(cross_length),
                                          style=wx.OK | wx.CANCEL)
        inputcapture.Show()
        if inputcapture.ShowModal() == wx.ID_OK:
            cross_length = int(inputcapture.GetValue())
        else:
            pass
        
    def create_crosshair(self, event):
        self.SetCursor(wx.StockCursor(wx.CURSOR_CROSS))

    def does_nothing(self, event):
        pass

    def on_paint(self, event):
        wx.BufferedPaintDC(self, self.buffer)


app = wx.App()
screen_size = wx.GetDisplaySize()
width = screen_size[0]
height = screen_size[1]*.95
CellCounter(None, (width, height)).Show()
app.MainLoop()
