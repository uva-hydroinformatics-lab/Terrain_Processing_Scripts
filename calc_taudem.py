# -*- coding: utf-8 -*-
"""
This program utilizes the TauDEM library to calculate TWI and its components, i.e.,
-Slope
-flow directions
-upstream contributing area
-Topographic wetness index.
These outputs are calcualted using the D8 flow direction method (used in ArcGIS)
as well as with the D-infinity flow direction method (developed by D. Tarbarton).
Batch files are called to execute these calculations, calculating on 8 processors
(can be changed in batch files).

Before processing,the user designated elevation file is projected to UTM (currently VA 17N). 

Download TauDEM: http://hydrology.usu.edu/taudem/taudem5/
Download gdal: https://github.com/creare-com/pydem/blob/master/INSTALL.md

Note 1: if downloading gdal with Conda, must manually add path environment varaible
Note 2: Batch files calling Dinf-specific commands must include file path to the
        Dinf executable, this was not necessary for D8-specific or general TauDEM
        executables.


Author: Gina O'Neil
"""

from osgeo import gdal, osr
import os
import subprocess
import sys


f_in = sys.argv[1] #input elevation file

def project_to_utm(filename):
    gdal_dset = gdal.Open(filename)
    prj = gdal_dset.GetProjection()
    prj_file = filename[:-4] + '_UTM.tif'
    print "Projection is: {} \n".format(prj)   
    print ("Projecting %s from WSG84 to NAD83 UTM ZONE 17N..................\n" %(filename))
    cmd = 'gdalwarp.exe %s %s -t_srs "+proj=utm +zone=17 +datum=NAD83" -tr 0.76200152 0.76200152' %(filename, prj_file)
    subprocess.call(cmd)
    return prj_file

def remove_pits(prj_file):
    fel_file = prj_file[:-4]+"fel.tif" #this is the default file name given to the TauDEM remvove pits output
    if os.path.exists(fel_file):
        print "Elevation file with pits removed already exists! \n"
        print "Filled elevation file: %s \n" %(fel_file)
        return fel_file
    else:
        print "Filled elevation file does not exist! \n"
        print "Removing pits................................................\n"
        subprocess.call("remove_pits_n8.bat %s" %(prj_file)) #args = [elev.tif]
        return fel_file

def D8_calcs(fel_file):        
    D8_fdr = '.\D8\\' + fel_file[:-4]+"D8_fdr.tif"
    D8_slp = '.\D8\\' + fel_file[:-4]+"D8_slp.tif"
    D8_uca = '.\D8\\' + fel_file[:-4]+"D8_uca.tif"
    D8_TWI = '.\D8\\' + fel_file[:-4]+"D8_twi.tif"
    
    print "Executing D8 calculations........................................\n"
    
    if not os.path.exists('D8'):
        os.mkdir('D8')
    
    if not os.path.exists(D8_fdr):
        print "Calculating D8 flow directions and slope.....................\n"
        subprocess.call("D8FlowDir_n8.bat %s %s %s" %(D8_fdr, D8_slp, fel_file))
    else:
        print "D8 flow directions and slope already exist! \n"
        
    if not os.path.exists(D8_uca):
        print "Calculating D8 upstream constributing area...................\n"
        subprocess.call("D:\PyDEM_testing\USGS_tiff\TauDEM\D8_UCA_n8.bat %s %s" %(D8_fdr, D8_uca))
    else:
        print "D8 upstream contributing area already exists! \n"
    
    if not os.path.exists(D8_TWI):
        print "Calculating TWI from D8 components...........................\n"
        subprocess.call("D:\PyDEM_testing\USGS_tiff\TauDEM\TWI_n8.bat %s %s %s" %(D8_slp, D8_uca, D8_TWI))
    else:
        print "TWI from D8 components already exists! \n"
    
    print "D8 calculations complete! \n"

def Dinf_calcs(fel_file):        
    Dinf_fdr = '.\Dinf\\' + fel_file[:-4]+"Dinf_fdr.tif"
    Dinf_slp = '.\Dinf\\' + fel_file[:-4]+"Dinf_slp.tif"
    Dinf_uca = '.\Dinf\\' + fel_file[:-4]+"Dinf_uca.tif"
    Dinf_TWI = '.\Dinf\\' + fel_file[:-4]+"Dinf_twi.tif"
    
    print "Executing Dinf calculations......................................\n"
    
    if not os.path.exists('Dinf'):
        os.mkdir('Dinf')
    
    if not os.path.exists(Dinf_fdr):
        print "Calculating Dinf flow directions and slope...................\n"
        subprocess.call("DinfFlowDir_n8.bat %s %s %s" %(Dinf_fdr, Dinf_slp, fel_file))
    else:
        print "Dinf flow directions and slope already exist! \n"
        
    if not os.path.exists(Dinf_uca):
        print "Calculating Dinf upstream constributing area.................\n"
        subprocess.call("D:\PyDEM_testing\USGS_tiff\TauDEM\Dinf_UCA_n8.bat %s %s" %(Dinf_fdr, Dinf_uca))
    else:
        print "D8 upstream contributing area already exists! \n"
    
    if not os.path.exists(Dinf_TWI):
        print "Calculating TWI from Dinf components.........................\n"
        subprocess.call("D:\PyDEM_testing\USGS_tiff\TauDEM\TWI_n8.bat %s %s %s" %(Dinf_slp, Dinf_uca, Dinf_TWI))
    else:
        print "TWI from Dinf components already exists! \n"
        
    print "Dinf calculations complete! \n"

def main():
    #check projection of elevation file
    filename_to_elevation_geotiff = project_to_utm(f_in)

    #remove pits from projcted elevation file
    fel_file = remove_pits(filename_to_elevation_geotiff)

    #execute D8 calcs
    D8_calcs(fel_file)
    
    #execute Dinf calcs
    Dinf_calcs(fel_file)


if __name__ == '__main__':
    main()
