#Imports
from skimage.io import imread,imsave
from skimage import draw
import glob
import matplotlib.pyplot as plt
import numpy as np
import SimpleITK as sitk
import os


Image_Size=128  #Parameter (currently only works on single channel square images)
Circle_Radius=50

#Make TempStorage Folder for Image Processing
os.makedirs('./TempStorage', exist_ok=True)

#Make Output Folder
os.makedirs('./CircleOutputs', exist_ok=True)

#Create Circle Mask for Target Registration
black=np.zeros((Image_Size,Image_Size))
coords = draw.circle(Image_Size/2, Image_Size/2,Circle_Radius) 
black[coords]=1
imsave('./TempStorage/CircleMask.png',black.astype('uint8'))


#Glob Files
files=sorted(glob.glob('./InputImages/*')) #Must be Segmented Single Cells on Black Background

    
#Initialize Registration Method
selx = sitk.ElastixImageFilter()
selx.SetParameterMap(selx.GetDefaultParameterMap('nonrigid'))
    
#For each file loop
for n,file in enumerate(files):
    name=file.split('/')[-1]
    
    #Read Image and create current shape mask
    img=imread(file)
    mask=img>0
    
    #Save Image and Mask so they can be properly read in using SimpleITK
    imsave('./TempStorage/CellImage.png',img.astype('uint8'))
    imsave('./TempStorage/CellMask.png',mask.astype('uint8'))

    #Read In Using Proper Method
    movingImage = sitk.ReadImage('./TempStorage/CellMask.png')
    movingLabel = sitk.ReadImage('./TempStorage/CellImage.png')

    
    #Create Deformation Field necessary to register shape of mask to target circle
    selx.SetMovingImage(movingImage)
    fixedImage = sitk.ReadImage('./Test/CircleMask.png')
    selx.SetFixedImage(fixedImage)
    selx.Execute()

    # Transform Image using the deformation field from above
    resultImage = sitk.Transformix(movingLabel, selx.GetTransformParameterMap())
    
    #Process Outputs (Maybe changed depending on needs)
    RegisteredImage=np.reshape(resultImage,(Image_Size,Image_Size))
    RegisteredImage[RegisteredImage<0]=0
    imsave('./CircleOutputs/'+name,RegisteredImage.astype('uint8'))
    
    #Show Progress
    if n%10000==0:
        print(n)
        
print('Done')
