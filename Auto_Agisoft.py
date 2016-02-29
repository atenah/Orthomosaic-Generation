# Author:      Athena
#
# Created:     07/08/2014



import os
import PhotoScan
import argparse


def AgisoftInvoke(photoPath,pszFile,exportPath,res):

    print("Script started")

    doc = PhotoScan.app.document

    #promting for path to photos
    path_photos = photoPath
    path_psz = pszFile
    path_export = exportPath
    resolution = res

    if not os.path.isdir(path_photos):
    	print("Script aborted")
    	return -1

    #creating new chunk
    chunk = PhotoScan.Chunk()
    chunk.label = "New Chunk"
    doc.chunks.add(chunk)

    #loading images
    image_list = os.listdir(path_photos)
    for photo in image_list:
    	if ("jpg" or "jpeg" or "tiff" or "tif") in photo.lower():
    		chunk.photos.add(path_photos + photo)

    #loading coordinates from EXIF and setting up the coordinate system
    chunk.ground_control.loadExif()
    chunk.ground_control
    crs = PhotoScan.CoordinateSystem()
    crs.init("EPSG::4326") #WGS84
    chunk.ground_control.crs = crs

    #align photos
    chunk.matchPhotos(accuracy = "high", preselection = "generic", filter_mask = False, point_limit = 40000)
    chunk.alignPhotos()

    #building dense cloud
    #chunk.buildDenseCloud(quality = "medium", filter = "aggressive", gpu_mask = 1, cpu_cores_inactive = 1) #gpu_mask for OpenCL processing

    #building mesh
    chunk.buildModel(surface = "height field", source = "sparse", interpolation = "enabled", faces = "high")

    #build texture
    #chunk.buildTexture(mapping = "generic", blending = "average", size=4098)



    doc.save(path_psz)
    PhotoScan.app.update()

    ###exporting DEM and Orthophoto

    #estimating effective ground resolution
    if chunk.ground_control.locations[chunk.cameras[0]].coord:  #first image coordinates, should be aligned
    	crd = chunk.ground_control.locations[chunk.cameras[0]].coord

    #longitude
    v1 = PhotoScan.Vector((crd[0], crd[1], 0))
    v2 = PhotoScan.Vector((crd[0] + 0.001, crd[1], 0))
    vm1 = chunk.crs.unproject(v1)
    vm2 = chunk.crs.unproject(v2)
    res_x = (vm2 - vm1).norm() * 1000

    #latitude
    v2 = PhotoScan.Vector( (crd[0], crd[1] + 0.001, 0))
    vm2 = chunk.crs.unproject(v2)
    res_y = (vm2 - vm1).norm() * 1000

    pixel_x = pixel_y = resolution  #export resolution (meters/pix)
    d_x = pixel_x / res_x
    d_y = pixel_y / res_y

    chunk.exportOrthophoto(path_export + "orthophoto.tif", format='tif', blending='average', color_correction = False, projection = chunk.crs, dx = d_x, dy = d_y)
    #chunk.exportDem(path_export + "\\dem_.tif", format='tif', projection = chunk.crs, dx = d_x, dy = d_y)

    print("Script finished")


# Command Line: Parse Arguments
parser = argparse.ArgumentParser(description='This is script runs a standard mosaic at a given resolution in Agisoft Photoscan using images in a given directory.')
parser.add_argument('-i','--input',help='Input Photos Path',required=True)
parser.add_argument('-p','--psz',help='psz file name',required=True)
parser.add_argument('-o','--output',help='Output Folder Path',required=True)
parser.add_argument('-r','--resolution',help='Output Ortho Resolution',required=True,type=float)
args = parser.parse_args()


# Call Agisoft invoke method with parsed arguements
print(args.resolution)

AgisoftInvoke(args.input,args.psz,args.output,args.resolution)
