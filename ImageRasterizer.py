

class ImageSlicer:
    def __init__(self, grid, numrows, numcols,file):
        self.grid = grid
        self.numrows = numrows
        self.numcols = numcols
        self.file = file

    def mainimage(file,numcols,numrows):
        
    
        from PIL import Image as PILImage
        from GlobalStates import GlobalStates


        image = PILImage.open(file)
        width, height = image.size
        width = int(width) 
        height = int(height)
        print(str(width) + "width and " + str(height) + "height""\n")
        cols=int(numcols)
        rows=int(numrows)
        numberofyes = 0
        grid = [[False for i in range(cols)] for j in range(rows)]
        for i in range(0, height-int(height/rows), int(height/rows)):
                for j in range(0, width - int(width/cols), int(width/cols)):
                    slice = image.crop((j, i, j + cols, i + rows))
                     #slice = image.crop(j, i, j + int(width/cols), i + int(width/rows))
                # print(slice.getpixel((slice.width // 2, slice.height // 2)))
                    if slice.getpixel((slice.width // 2, slice.height // 2))[0:2] < (160, 160):

                            grid[int(i/(height/rows))][int(j/(width/cols))] = True
                            numberofyes = numberofyes + 1
                            
                    else:
                        grid[int(i/(height/rows))][int(j/(width/cols))] = False

        print("numberofyes=" + str(numberofyes)+"\n" )
        #print("first five elements: "+str(grid[1][1]) + str(grid[2][1]) + str(grid[3][1])+ str (grid[4][1]) + str(grid[5][1])+"\n")


        return grid
    



