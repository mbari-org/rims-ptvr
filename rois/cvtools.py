# -*- coding: utf-8 -*-
"""
cvtools - image processing tools for plankton images

"""
import time
import json
import csv
import os
import sys
import glob
import datetime
import pickle
import random, string
from math import pi
import cv2
from skimage import morphology, measure, exposure, restoration
from skimage import transform
from skimage import util
from skimage import color
from skimage.feature import canny
from skimage.filters import threshold_otsu, scharr, gaussian
from skimage.draw import ellipse_perimeter
import numpy as np
from scipy import ndimage

PROC_VERSION = 101
EDGE_THRESH = 2.0
DECONV = True
DECONV_ITER = 9
DECONV_METHOD = 'LR'
DECONV_MASK_WEIGHT = 0.5
ESTIMATE_SHARPNESS = True 
SMALL_FLOAT_VAL = 0.0001
BW_BLUR_RADIUS = 3
BAYER_PATTERN = cv2.COLOR_BAYER_RG2RGB

# make a Gaussian kernel
def make_gaussian(size, fwhm = 3, center=None):
    """ Make a square gaussian kernel.
    size is the length of a side of the square
    fwhm is full-width-half-maximum, which
    can be thought of as an effective radius.
    """

    x = np.arange(0, size, 1, float)
    y = x[:,np.newaxis]

    if center is None:
        x0 = y0 = size // 2
    else:
        x0 = center[0]
        y0 = center[1]

    output = np.exp(-4*np.log(2) * ((x-x0)**2 + (y-y0)**2) / fwhm**2)
    output = output/np.sum(output)

    return output

# Encode Bayer pattern string into CV2 bayer pattren code
def get_bayer_pattern(proc_settings):
    if proc_settings['bayer_pattern'] == 'RG':
        bayer_pattern = cv2.COLOR_BAYER_RG2RGB
    elif proc_settings['bayer_pattern'] == 'BG':
        bayer_pattern = cv2.COLOR_BAYER_BG2RGB
    elif proc_settings['bayer_pattern'] == 'GR':
        bayer_pattern = cv2.COLOR_BAYER_GR2RGB
    else:
        bayer_pattern = cv2.COLOR_BAYER_GB2RGB
        
    return bayer_pattern

# import raw image
def import_image(abs_path, filename, proc_settings):
    
    if proc_settings['is_raw']:
        bayer_pattern = get_bayer_pattern(proc_settings)

    # Load and convert image as needed
    img_c = cv2.imread(os.path.join(abs_path,filename),cv2.IMREAD_UNCHANGED)
    if proc_settings['is_raw']:
        img_c = cv2.cvtColor(img_c,bayer_pattern)

    return img_c

# convert image to 8 bit with or without autoscaling
def convert_to_8bit(img, proc_settings):

    # Convert to 8 bit and autoscale
    if proc_settings['autoscale']:

        result = np.float32(img)-np.min(img)
        if np.max(img) != 0:
            result = result/np.max(img)

        img_8bit = np.uint8(255*result)
    else:
        img_8bit = np.unit8(img)

    return img_8bit

# extract simple features and create a binary representation of the image
# use the binary image to estimate morphological features and save out
# a number of intermediate images
def extract_features(img,
                     original,
                     proc_settings, 
                     save_to_disk=False,
                     abs_path='',
                     file_prefix=''):

    start_time = time.time()

    # Define an empty dictionary to hold all features
    output = {}
    
    # copy the image to save a raw color version
    output['rawcolor'] = np.copy(img)
    
    # compute features from gray image
    if proc_settings['channels'] == 3:
        gray = np.uint8(np.mean(img,2))
    else:
        gray = img
        print(img.shape)
        img = np.dstack((img, img, img))
        print(img.shape)
    
    # unpack settings
    low_threshold = proc_settings['edge_threshold_low']
    blur_rad = proc_settings['bw_blur_radius']

    # edge-based segmentation and region filling to define the object
    edges_mag = scharr(gray)
    edges_med = np.median(edges_mag)
    edges_thresh = low_threshold*edges_med
    edges = edges_mag >= edges_thresh
    edges = morphology.closing(edges,morphology.disk(blur_rad))
    filled_edges = ndimage.binary_fill_holes(edges)
    edges = morphology.erosion(filled_edges,morphology.disk(blur_rad))
    
    # define the binary image for further operations
    bw_img = edges

    # Compute morphological descriptors
    label_img = morphology.label(bw_img,connectivity=2,background=0)
    props = measure.regionprops(label_img,gray)

    valid_object = False
    
    data_img = img.copy()

    if len(props) > 0:
        # use only the features from the object with the largest area
        max_area = 0
        max_area_ind = 0
        for f in range(0,len(props)):
            if props[f].area > max_area:
                max_area = props[f].area
                max_area_ind = f

        ii = max_area_ind

        # Save only the BW image with the largets area
        bw_img = (label_img)== props[ii].label

        # Check for clipped image
        if np.max(bw_img) == 0:
            bw = bw_img
        else:
            bw = bw_img/np.max(bw_img)
            
        features = {}    
            
        clip_frac = float(np.sum(bw[:,1]) +
                np.sum(bw[:,-2]) +
                np.sum(bw[1,:]) +
                np.sum(bw[-2,:]))/(2*bw.shape[0]+2*bw.shape[1])


        # Save simple features of the object
        features['area'] = props[ii].area
        features['minor_axis_length'] = props[ii].axis_minor_length
        features['major_axis_length'] = props[ii].axis_major_length
        if props[ii].axis_major_length == 0:
            features['aspect_ratio'] = 1
        else:
            features['aspect_ratio'] = props[ii].axis_minor_length/props[ii].axis_major_length
        features['orientation'] = props[ii].orientation
        
        # draw an ellipse using the major and minor axis lengths
        cv2.ellipse(data_img,
            (int(props[ii].centroid[1]),int(props[ii].centroid[0])),
            (int(props[ii].axis_major_length/2),int(props[ii].axis_minor_length/2)),
            180 - 180/np.pi*props[ii].orientation,
            0,
            360,
            (0,255,0), 
            2
        )

        # save all features except for those with  pixel data
        output_dict = {}
        for prop in props[ii]:
            if prop == 'convex_image':
                continue
            if prop == 'filled_image':
                continue
            if prop == 'image':
                continue
            if prop == 'coords':
                continue
            output_dict[prop] = props[ii][prop]
       
        features = output_dict
        #print features
        features['clipped_fraction'] = clip_frac
        valid_object = True

    else:

        valid_object = False
        features = {}
        features['clipped_fraction'] = 1.0

        # Save simple features of the object
        features['area'] = 0.0
        features['minor_axis_length'] = 0.0
        features['major_axis_length'] = 0.0
        features['aspect_ratio'] = 1
        features['orientation'] = 0.0
 

 
    # sharpness analysis of the image using FFTs
    if proc_settings['estimate_sharpness']:
        if valid_object:

            gray_img = gray
        
            pad_size = 6
            # pad gray image to square shape for FFT
            for s in [6,7,8,9,10,11,12,13,14]:
                if np.max(gray_img.shape) <= 2**s:
                    pad_r = 2**s - gray_img.shape[0]
                    pad_c = 2**s - gray_img.shape[1]
                    real_img = np.pad(gray_img,[(0,pad_r),(0,pad_c)],mode='constant') # default is 0 for pad value
                #print "Pad size: " + str(2**s)
                    pad_size = 2**s
                    break
        
        
            # prefilter the image to remove some of the DC
            real_img = real_img.astype('float') - np.mean(img)
        
            # window the image to reduce ringing and energy leakage
            wind = make_gaussian(pad_size, pad_size/2, center=None)
        
            # estimate blur of the image using the method from Roberts et. al 2011
            the_fft = np.fft.fft2(real_img*wind)
            fft_mag = (np.abs(the_fft).astype('float'))
            fft_mag = np.fft.fftshift(fft_mag)
            fft_mag = gaussian(fft_mag,2)
        
            # find all frequencies with energy above 5% of the max in the spectrum
            mask = fft_mag > 0.02*np.max(fft_mag)
        
            rr = (mask.nonzero())[0]
            rr = rr.astype('float') - pad_size/2
            rr = 4*rr/pad_size
            cc = (mask.nonzero())[1]
            cc = cc.astype('float') - pad_size/2
            cc = 4*cc/pad_size

            #cv2.imwrite('fft_mask.tif',255*mask.astype('uint8'))
            #cv2.imwrite('fft_mag.tif',(255*fft_mag/np.max(fft_mag)).astype('uint8'))
        
            rad = np.sqrt(rr**2 + cc**2)

        else:

            rad = 0
    else:
    
        rad = 0

    # normalize the image as a float
    if np.max(img) == 0:
        img = np.float32(img)
    else:
        img = np.float32(img)/np.max(img)
        
    if proc_settings['deconv']:
    
        # Get the intesity image in HSV space for sharpening
        # ignore 0/0 errors here
        with np.errstate(divide='ignore'):
            hsv_img = color.rgb2hsv(img)
        v_img = hsv_img[:,:,2]
    
    
        # unsharp mask before masking with binary image
        if proc_settings['deconv_method'] == "um":

            old_mean = np.mean(v_img)
            blurd = gaussian(v_img,1.0)
            hpfilt = v_img - blurd*proc_settings['deconv_mask_weight']
            v_img = hpfilt/(1-proc_settings['deconv_mask_weight'])

            new_mean = np.mean(v_img)

            if (new_mean) != 0:
                v_img = v_img*old_mean/new_mean


            v_img[v_img > 1] = 1
            v_img = np.uint8(255*v_img)

        # mask the raw image with smoothed foreground mask
        blurd_bw_img = gaussian(bw_img,blur_rad)
        v_img = v_img*blurd_bw_img

        v_img[v_img == 0] = proc_settings['small_float_val']

        if proc_settings['deconv_method'] == "lr":
        
            # Make a guess of the PSF for sharpening
            # for now just use a static kernel size
            # @TODO : add these to settings
            psf = make_gaussian(5, 3, center=None)

            v_img = restoration.richardson_lucy(v_img, 
                                                psf, 
                                                proc_settings['deconv_iter'])

            v_img[v_img < 0] = 0

            if np.max(v_img) == 0:
                v_img = np.uint8(255*v_img)
            else:
                v_img = np.uint8(255*v_img/np.max(v_img))
        
        # restore the rbg image from hsv
        v_img[v_img == 0] = proc_settings['small_float_val']
        hsv_img[:,:,2] = v_img
        img = color.hsv2rgb(hsv_img)
    
    else:
    
        pass

        # mask the raw image with smoothed foreground mask
        #blurd_bw_img = gaussian(bw_img,blur_rad)
        #for ind in range(0,3):
        #    img[:,:,ind] = img[:,:,ind]*blurd_bw_img
               
    
    # Check for clipped image
    output['clipped_fraction'] = features['clipped_fraction']
    output['valid_object'] = valid_object
    output['features'] = features
    output['image'] = img
    output['binary'] = 255*bw_img
    output['data'] = data_img
    output['sharpness'] = 1024*np.max(rad)
    #output['proc_version'] = proc_settings['proc_version']

    
    # Save the binary image and also color image if requested
    if save_to_disk and valid_object:

        #try:

        # convert and save images

        # save features
        #with open(os.path.join(abs_path,file_prefix+"_features.csv"),'wb') as csv_file:
        #    writer = csv.writer(csv_file)
        #    writer.writerow(output['features'].keys())
        #    writer.writerow(output['features'].values())

        # Raw color (no background removal)
        #cv2.imwrite(os.path.join(abs_path,file_prefix+"_rawcolor.jpg"),output['rawcolor'])
        # Save the processed image and binary mask
        cv2.imwrite(os.path.join(abs_path,file_prefix+".jpg"),output['image'])
        cv2.imwrite(os.path.join(abs_path,file_prefix+"_binary.png"),output['binary'])
        cv2.imwrite(os.path.join(abs_path,file_prefix+"_rawcolor.png"),output['rawcolor'])
        cv2.imwrite(os.path.join(abs_path,file_prefix+"_rawcolor.jpg"),output['rawcolor'])
        cv2.imwrite(os.path.join(abs_path,file_prefix+"_ellipse.png"),output['data'])
        cv2.imwrite(os.path.join(abs_path,file_prefix+"_ellipse.jpg"),output['data'])
        cv2.imwrite(os.path.join(abs_path,file_prefix+"_edges.png"),255*edges_mag)
        cv2.imwrite(os.path.join(abs_path,file_prefix+"_edges.jpg"),255*edges_mag)
        if original.size:
            cv2.imwrite(os.path.join(abs_path,file_prefix+"_original.tif"),original)

        cmd = ('zip -mqj ' + os.path.join(abs_path,file_prefix+'.zip ') +
                os.path.join(abs_path,file_prefix+"_binary.png ") +
                os.path.join(abs_path,file_prefix+"_rawcolor.png ") +
                os.path.join(abs_path,file_prefix+"_rawcolor.jpg ") +
                os.path.join(abs_path,file_prefix+"_ellipse.png ") +
                os.path.join(abs_path,file_prefix+"_ellipse.jpg ") +
                os.path.join(abs_path,file_prefix+"_edges.png ") +
                os.path.join(abs_path,file_prefix+"_edges.jpg ") +
                os.path.join(abs_path,file_prefix+"_features.csv")
            )
        if original.size:
            cmd = cmd + " " + os.path.join(abs_path,file_prefix+"_original.tif")

        os.system(cmd)

    #print "proccessing time " + str(time.time()-start_time)

    return output
