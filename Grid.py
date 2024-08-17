from tkinter import *
import math
from GlobalStates import GlobalStates
from Slice import SliceCard
import random
import string
from ImageRasterizer import ImageSlicer

class Cell():
    FILLED_COLOR_BG = "black" 
    EMPTY_COLOR_BG = "white"
    FILLED_COLOR_BORDER = "green" 
    EMPTY_COLOR_BORDER = "grey"
    INDICATOR_COLOR = "red"
    INDIC_BORDER_COLOR = "pink"

    def __init__(self, master, x, y, size):
        """ Constructor of the object called by Cell(...) """
        self.master = master
        self.abs = x
        self.ord = y
        self.size= size
        self.fill = 0
        self.mat1 = False
        self.markeder = False
        self.numrows = 0
        self.numcols=0
        self.filename = ''

    def _switch(self):
        """ Switch if the cell is filled or not. """
        if self.fill == 0:
            self.fill = 1
        elif self.fill == 1:
            self.fill = 2
        else:
            self.fill = 0
  
    def mark(self):
         self.markeder = not self.markeder

    def draw(self):
        """ order to the cell to draw its representation on the canvas """
        if self.master != None :
            if self.fill == 0:
                fill = Cell.EMPTY_COLOR_BG
                outline = Cell.EMPTY_COLOR_BORDER
            elif self.fill == 1:
                fill = Cell.FILLED_COLOR_BG
                outline = Cell.FILLED_COLOR_BORDER
            elif self.fill == 2:
                fill = Cell.INDICATOR_COLOR
                outline = Cell.INDIC_BORDER_COLOR

            xmin = self.abs * self.size
            xmax = xmin + self.size
            ymin = self.ord * self.size
            ymax = ymin + self.size

            self.master.create_rectangle(xmin, ymin, xmax, ymax, fill = fill, outline = outline)

class CellGrid(Canvas):
    def __init__(self,master, rowNumber, columnNumber, cellSize , *args, **kwargs):
        Canvas.__init__(self, master, width = cellSize * columnNumber , height = cellSize * rowNumber, *args, **kwargs)
        numcols = columnNumber
        numrows = rowNumber
        self.numcols = numcols
        self.numrows = numrows

        self.cellSize = cellSize

        self.grid = []
        for row in range(rowNumber):

            line = []
            for column in range(columnNumber):
                line.append(Cell(self, column, row, cellSize))

            self.grid.append(line)

        #memorize the cells that have been modified to avoid many switching of state during mouse motion.
        self.switched = []

        #bind click action
        self.bind("<Button-1>", self.handleMouseClick)  
        #bind moving while clicking
        self.bind("<B1-Motion>", self.handleMouseMotion)
        #bind release button action - clear the memory of midified cells.
        self.bind("<ButtonRelease-1>", lambda event: self.switched.clear())

        self.draw()

        
        self.runtime_text = Text(master, height=6, width=50)
        self.runtime_text.pack( anchor='ne',padx =5, pady=2)
        # Function to append text to the runtime text box
        self.add_runtime_text("Program started")
        self.add_runtime_text("Set your desired scale on the slider and press 'Resize' \n This deletes everything so do this first \n import an image by pressing 'Insert Image once the filepath is inserted \n interact with the grid by pressing on the desired cells \n press slice to slice and dice the image")
            
            
                # Create a slider that goes from 1 to 5 with integer steps
        self.slider_value = IntVar(value=GlobalStates.get_scaler(GlobalStates))  
        self.slider = Scale(master, from_=1, to=5, orient=HORIZONTAL, variable=self.slider_value, tickinterval=1, resolution=1, command=self.update_slider)
        self.slider.pack(anchor='nw', padx=5, pady=0)

        self.text_display = Label(master,text="The Black squares correspond to the first Material (Q1)\n The Red squares correspond to the second Material (Q2) \n Enter a filepath and press -Insert Image- in order to overlay an image into the grid \n Press slice to generate a Gcode with the current time as filename in the folder ")
        self.text_display.pack(anchor='ne', padx=5, pady=0)

        # Add erase button
        self.erase_button = Button(master, text="Erase", command=lambda: [self.add_runtime_text("ERASING"), self.erase()])
        self.erase_button.pack(anchor="nw", padx=10, pady=4)

        self.abaqus_button = Button(master, text="Abaqus", command=self.run_abaqus)
        self.abaqus_button.pack(anchor="nw", padx=10, pady=4)
            
        # Add slice button
        self.slice_button = Button(master, text="Slice", command=lambda: [self.add_runtime_text("SLICING AND DICING"), SliceCard.slice(SliceCard,self,numrows,numcols)])
        self.slice_button.pack(anchor="nw", padx=10, pady=4)
            

        self.resize_button = Button(master, text="Resize", command=self.resize)
        self.resize_button.pack(anchor="nw", padx=10, pady=4)
        
        self.insert_image_button = Button(master, text="Insert Image", command=lambda: [self.updatefilename(),self.insert_image()])
        self.insert_image_button.pack(anchor="nw", padx=10, pady=4)

        self.filepath_label = Label(master, text="Filepath:")  
        self.filepath_label.pack(anchor='sw', padx=10, pady=2)

        self.filepath_entry = Entry(master, width=20)
        self.filepath_entry.pack(anchor='sw', padx=10, pady=2)

    def updatefilename(self):
        self.filename = self.filepath_entry.get()

    def insert_image(self):
        importgrid = ImageSlicer.mainimage(self.filename,self.numcols,self.numrows)
        if importgrid != NONE:
            print("payload secured")
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                if importgrid[i][j]:
                    self.grid[i][j].fill=1
                    self.grid[i][j].draw()
                
        
    def resize(self):
        packandreplace(self)

    def update_slider(self, value):
    # Code to be executed when the slider value is changed
        self.slider_value = value
        GlobalStates.set_scaler(GlobalStates, self.slider_value)
        #self.add_runtime_text(str(GlobalStates.get_scaler(GlobalStates)))

    def erase(self):
        for row in self.grid:
            for cell in row:
                cell.fill = 0
                cell.draw()
    def add_runtime_text(self, message):
            self.runtime_text.insert('end', message + '\n')
            self.runtime_text.see('end')  # Scroll to the end of the text box
             
    def draw(self):
        for row in self.grid:
            for cell in row:
                cell.draw()
   

        # Get row and column from click event
    def event_coords(self,event):
            row = int(event.y / self.cellSize)
            col = int(event.x / self.cellSize)
            return row, col

        # Function to actually draw the circle
        

    
    def _eventCoords(self, event):
        row = int(event.y / self.cellSize)
        column = int(event.x / self.cellSize)
        return row, column

    def handleMouseClick(self, event):
            row, column = self._eventCoords(event)
            cell = self.grid[row][column]
        
            cell = self.grid[row][column]
            cell._switch()
            cell.draw()
            self.switched.append(cell)
                #add the cell to the list of cell switched during the click
                

    def handleMouseMotion(self, event):
        row, column = self._eventCoords(event)
        cell = self.grid[row][column]
        if cell not in self.switched:
                cell._switch()
                cell.draw()
                self.switched.append(cell)
#notes for next time, nothing works and various issues, slicecard has no attribute slicetoggle so we need to change that
#if circletoggle is false, why cant we paint
#when it is on, why we not circling
#etc etc
#
#
#
if __name__ == "__main__" :
    from Grid import packandship

    packandship()

def packandship():
    GlobalStates.set_firsttime(GlobalStates, True)
    GlobalStates.set_scaler(GlobalStates, 1)
    scale=GlobalStates.get_scaler(GlobalStates)
    app = Tk()
    numrows = 40*scale
    numcols = 50*scale
    cellsizer = int( 10/scale)
    frame = Frame(app)
    frame.pack()
    
    GlobalStates.set_frame(GlobalStates,frame)
    
    grid = CellGrid(frame, numrows, numcols, cellsizer)
    grid.pack()
    GlobalStates.set_firsttime(GlobalStates, False)
    app.mainloop()


def packandreplace(grid):
    
    frame = GlobalStates.get_frame(GlobalStates)
    scale = int(GlobalStates.get_scaler(GlobalStates))
    numrows = 40*scale
    numcols = 50*scale
    cellsizer =int(10/scale)
    # Delete current grid
    grid.erase_button.destroy()
    grid.slice_button.destroy()
    grid.resize_button.destroy()
    grid.insert_image_button.destroy()
    grid.filepath_label.destroy()
    grid.filepath_entry.destroy()
    grid.runtime_text.destroy()
    grid.slider.destroy()
    grid.text_display.destroy()
    grid.destroy()
    
    # Create new grid in same window
    newgrid = CellGrid(frame, numrows,numcols, cellsizer)
    newgrid.pack()

