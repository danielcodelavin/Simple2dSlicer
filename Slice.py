import random
import string
from GlobalStates import GlobalStates
import time
class SliceCard:
    def __init__(self, grid, numrows, numcols): 
        self.grid = grid
        self.numrows = numrows
        self.numcols = numcols
        self.globalextrusion = 0
        self.globalextruder = 0
        self.file = None
        self.scaler=0
        self.mat = 1
    

      #  self.currenttail = 0
    def generate(self,start, end, column):
           #generate needs 3 parts, the head, the body and the legs
           # the head should be the "speedup" and should begin 2 rows or "y" above startblock and end at startblock
           #the body is from startblock to endblock and needs the ""additive"" Q1 variable which comes from endblock-startblock
            #the tail is to two rows below endblock
         self.head(self,start,column)
         self.body(self,start,end)
         self.tail(self,end)
         
        
    def head(self,start,column):
          begin = (start/self.scaler)-2
          open(self.file, 'a').write("G01 Y" +str(begin)+" X"+ str(column/self.scaler) +" \n")
          open(self.file, 'a').write("G01 Y" +str(start/self.scaler) +" \n")
    
    def body(self,start,end):
          amount=(end-start +1)/self.scaler
          if self.mat ==1:
            self.globalextrusion = self.globalextrusion + amount
            open(self.file, 'a').write("G01 Y" + str(end/self.scaler) +" Q"+ str(self.mat) + "=" + str(self.globalextrusion) +"\n")
          else:
            self.globalextruder = self.globalextruder + amount
            open(self.file, 'a').write("G01 Y" + str(end/self.scaler) +" Q"+ str(self.mat) + "=" + str(self.globalextruder) +"\n")

    def tail(self,end):
          tailerow = (end/self.scaler)+2
          open(self.file, 'a').write("G01 Y" +str(tailerow) +"\n \n")





    def slice(self,grid,numrows,numcols):
        self.scaler = int(GlobalStates.get_scaler(GlobalStates))
        endblack = 0
        self.globalextrusion = 0
        self.globalextruder = 0
        t = time.localtime(time.time())
        namestring = str(t.tm_year) +'_'+ str(t.tm_mon) +'_'+ str(t.tm_mday) +'_'+ str(t.tm_hour) +'_'+ str(t.tm_min) +'_'+ str(t.tm_sec)
        fileraw = ''.join(namestring)  # Create random string of length 15
        file = fileraw + ".nc"
        self.file = file
        open(self.file, 'w').write("")
        with open(self.file, 'a') as f:
                        f.write("\nR21=2000 (Ventilöffnungszeit in ms)\n")
                        f.write("R22=1000 (Druckhöhe in mbar)\n\n")
                        f.write("R30=-30\t( -- X-Offset Druckkopf rechts, PH1 -- )\n")
                        f.write("R31=-40\t( -- Y-Offset Druckkopf rechts, PH1 -- )\n")
                        f.write("R32=0.0\t\t( -- Z-Offset Druckkopf rechts, PH1 -- )\n")
                        f.write("#set paramZeroShift( G54; R30; R31; R32)#\n\n")
                        f.write("G54 (Aufruf Offset)\n\n\n\n")
        
        for column in range(numcols):
            for row in range(numrows):
                cell = grid.grid[row][column]
                if cell.fill ==1 or cell.fill == 2: # find beginning of black section
                    self.mat = cell.fill
                    startblack = row
                    checkbox = grid.grid[startblack-1][column]
                    if checkbox.fill != self.mat:
                        for brow in range(startblack + 1, numrows):
                            dell = grid.grid[brow][column]
                            if dell.fill != self.mat:
                                endblack = brow-1  # find end of black section
                                print("found the top and bottom of the line, resuming with mat " + str(self.mat) )
                                self.generate(self, startblack, endblack, column)
                                break  # break out of the innermost loop only




