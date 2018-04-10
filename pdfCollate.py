''' 
pdfCollater.py
Code by Mikenna Everett
mikenna.everett@gmail.com
August 18, 2013

This program depends on the python module PyPDF2 version 1.7, available for download and installation at:
https://github.com/mstamy2/PyPDF2/

This program will collate a PDF file (or the PDF files in a directory) scanned using an auto-document feeder without cutting the binding of the original document. 


A potential 4-page PDF input document
    -----------------
    |   8   |   1   |   (Page 1)
    -----------------
    |   2   |   7   |   (Page 2)
    -----------------
    |   6   |   3   |   (Page 3)
    -----------------
    |   4   |   5   |   (Page 4)
    -----------------

Will be collated into the resulting document:
    ---------
    |   1   |   (Page 1)
    ---------
    |   2   |   (Page 2)
    ---------
    |   3   |   (Page 3)
    ---------
    |   4   |   (Page 4)
    ---------
    |   5   |   (Page 5)
    ---------
    |   6   |   (Page 6)
    ---------

To prepare a document for use:
-Remove the document's fasteners
-Open to its center page 
-Placed in the auto-document feeder (ADF).
-The resulting scan should begin with the first and last page of the original pamphlet, with each subsequent page in the document moving towards the middle pages of the original pamphlet.
-Crop as needed.
    

USAGE INSTRUCTIONS:
Run this program at a command line terminal. Navigate to the directory where pdfCollate.py is saved and run it with 1 argument:
"python pdfCollate.py [PATH]"

INPUT: a full path to a file/directory OR a filename/directory name in the same folder as pdfCollate.py.
OUTPUT: a file/directory of the properly collated document(s) by the same name as the original file/directory plus "-collated". NOTE: if a directory is specified, all contents of the directory are copied to the new directory.

Note: this program will not overwrite the original PDF files.

'''
from PyPDF2 import PdfFileReader, PdfFileWriter
import sys
import os
import shutil
 
def collatePDF(inFile, outFile):
    output = PdfFileWriter()
    pdfLeft = PdfFileReader(file( inFile, "rb"))
    pdfRight = PdfFileReader(file( inFile, "rb"))
    n = pdfLeft.getNumPages()
    frontPages = []
    backPages = []
    finalrot=0
    for i in range(n):
        # two copies of the same page to be split
        rightSide = pdfRight.getPage(i)
        leftSide = pdfLeft.getPage(i)
        
        upperRightx = leftSide.cropBox.getUpperRight_x() 
        upperRighty = leftSide.cropBox.getUpperRight_y()
        lowerLeftx = leftSide.cropBox.getLowerLeft_x()
        lowerLefty = leftSide.cropBox.getLowerLeft_y()

        width = leftSide.cropBox.getUpperRight_x() - leftSide.cropBox.getLowerLeft_x()
        height = leftSide.cropBox.getUpperRight_y() - leftSide.cropBox.getLowerLeft_y()
        rotation=leftSide.get('/Rotate')
        if (rotation==90 or rotation==270):
            leftSide.cropBox.upperRight = (width+leftSide.cropBox.lowerLeft[0],height/2+leftSide.cropBox.lowerLeft[1])
            rightSide.cropBox.lowerLeft = (leftSide.cropBox.lowerLeft[0],height/2+leftSide.cropBox.lowerLeft[1])
            rightSide.cropBox.upperRight = (width+leftSide.cropBox.lowerLeft[0], height+leftSide.cropBox.lowerLeft[1])
            
        elif(rotation ==0 or rotation==180): #width >= height
            leftSide.cropBox.upperRight = (width/2+leftSide.cropBox.lowerLeft[0],height+leftSide.cropBox.lowerLeft[1])
            rightSide.cropBox.lowerLeft = (width/2+leftSide.cropBox.lowerLeft[0],leftSide.cropBox.lowerLeft[1])
            rightSide.cropBox.upperRight = (width+leftSide.cropBox.lowerLeft[0],height+leftSide.cropBox.lowerLeft[1])
        else:
            print "Pages have no rotation, output may be incorrect"
            leftSide.cropBox.upperRight = (width/2+leftSide.cropBox.lowerLeft[0],height+leftSide.cropBox.lowerLeft[1])
            rightSide.cropBox.lowerLeft = (width/2+leftSide.cropBox.lowerLeft[0],leftSide.cropBox.lowerLeft[1])
            rightSide.cropBox.upperRight = (width+leftSide.cropBox.lowerLeft[0],height+leftSide.cropBox.lowerLeft[1])
        if(i==0):
            finalrot=rotation
        test = (i%2 == 0) != (rotation != finalrot) #If the page is even and rotated correctly, or odd and rotated incorrectly
        if (test):
            backPages.append(leftSide)
            frontPages.append(rightSide)
        else:                                       #The else case: odd and correct or even and incorrect
            frontPages.append(leftSide)
            backPages.append(rightSide)
                        
    backPages.reverse()
        
    for item in frontPages:
        output.addPage(item)
     
    for item in backPages:
        output.addPage(item)
     
    outputStream = file(outFile, "wb")
    output.write(outputStream)
    outputStream.close()

def main():
    
    if len(sys.argv) < 2:
        print "Invalid arguments"
        sys.exit()

    fileOrDir = sys.argv[1]

    if len(sys.argv) > 2:
        args = sys.argv[1:]
        fileOrDir = " ".join(args)

    curDirect = os.getcwd()

    if os.path.isdir(os.path.join(curDirect, fileOrDir)) or os.path.isfile(os.path.join(curDirect, fileOrDir)):
        fileOrDir = os.path.join(curDirect, fileOrDir)

    if os.path.isdir(fileOrDir):
        # user has specified a folder
        topDir = fileOrDir        
        path_out = topDir + "-collated"

        if not os.path.exists(path_out):
            os.makedirs(path_out)

        # walk through directory, collate all files
        for (path, dirs, files) in os.walk(topDir):
            # copy all directories, preserving hierarchy
            for d in dirs:
                newPath = path.replace(topDir,path_out)
                if not os.path.exists(newPath):
                    os.makedirs(newPath)
                if not os.path.exists(os.path.join(newPath,d)):
                    os.makedirs(os.path.join(newPath,d))
            for f in files:
                newPath = path.replace(topDir, path_out)
                print os.path.basename(path)
                print path
                if f.endswith(".pdf") and not f.startswith("._"):
                    collatePDF(os.path.join(path,f), os.path.join(newPath, f))
                else:
                    shutil.copyfile(os.path.join(path,f),os.path.join(newPath,f))

    elif os.path.isfile(fileOrDir):
        # user has specified a single file
        path_out = os.path.dirname(fileOrDir)

        if fileOrDir.endswith(".pdf"):
            f_out = fileOrDir[:-4] + "-collated.pdf"
        else:
            print "Error: non-PDF specified"
            sys.exit()
        collatePDF(os.path.join(curDirect,fileOrDir), os.path.join(path_out, f_out))

    else:
        print "Error: unable to locate file/directory"

main()










