import os
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
import astroalign as aa
import regions
from regions import Regions
from tqdm.auto import tqdm

def combine_darks(path):
    red_dark = np.empty(0)
    green_dark = np.empty(0)
    blue_dark = np.empty(0)
    for (p, d, files) in os.walk(path):
        for filename in files:
            if filename.startswith('dark') and filename.endswith('.fits'):
                data = np.asarray(fits.open(path + "/" + filename)[0].data)
                if 'R' in filename:
                    if red_dark.size < 1:
                        red_dark = data
                    else:
                        red_dark = (red_dark + data)/2
                elif 'G' in filename:
                    if green_dark.size < 1:
                        green_dark = data
                    else:
                        green_dark = (green_dark + data)/2
                elif 'B' in filename:
                    if blue_dark.size < 1:
                        blue_dark = data
                    else:
                        blue_dark = (blue_dark + data)/2
    fits.writeto(path + '/' + 'full_dark_R.fits', red_dark)
    fits.writeto(path + '/' + 'full_dark_G.fits', green_dark)
    fits.writeto(path + '/' + 'full_dark_B.fits', blue_dark)

def apply_dark(path):
    sky_data = np.asarray(fits.open("/home/ben/Desktop/personal_projects/astrophotography/night10282022/sky7997-B.fits")[0].data)
    dark_data = np.asarray(fits.open("/home/ben/Desktop/personal_projects/astrophotography/night10282022/full_dark_B.fits")[0].data)

    cal_data = sky_data - dark_data
    fits.writeto('/home/ben/Desktop/astrophotography/night10282022/test_cal.fits', cal_data)

def align(path):
    # Import images
    # img1 = np.asarray(fits.open("/home/ben/Desktop/personal_projects/astrophotography/night10282022/sky7997-B.fits")[0].data)
    # img2 = np.asarray(fits.open("/home/ben/Desktop/personal_projects/astrophotography/night10282022/sky8018-B.fits")[0].data)

    # Import images in color lists
    imgs_R = []
    imgs_G = []
    imgs_B = []
    for file in os.listdir(path):
        if "sky" in file and "fits" in file:
            if "R" in file:
                imgs_R.append(np.asarray(fits.open(path+file)[0].data))
            elif "G" in file:
                imgs_G.append(np.asarray(fits.open(path+file)[0].data))
            elif "B" in file:
                imgs_B.append(np.asarray(fits.open(path+file)[0].data))

    # Make foreground mask with first red image (the foreground should be the same in all)
    fg_regions = Regions.read(path+'foreground.reg', format='ds9')
    pix_mask_list = []
    for reg in fg_regions:
        pix_mask_list.append(reg.to_mask(mode='center'))
    fg_mask = np.zeros(imgs_R[0].shape)
    for mask in pix_mask_list:
        fg_mask += mask.to_image(imgs_R[0].shape)

    # Save foreground
    fg_img_R = np.multiply(imgs_R[0], fg_mask)
    fg_img_G = np.multiply(imgs_G[0], fg_mask)
    fg_img_B = np.multiply(imgs_B[0], fg_mask)

    # Flip mask
    fg_mask = 1 - fg_mask

    # Make transformation comparison images
    imgR_comp = np.multiply(imgs_R[0], fg_mask)
    imgR_comp = np.where(imgR_comp==0, np.nan, imgR_comp)
    imgG_comp = np.multiply(imgs_G[0], fg_mask)
    imgG_comp = np.where(imgG_comp==0, np.nan, imgG_comp)
    imgB_comp = np.multiply(imgs_B[0], fg_mask)
    imgB_comp = np.where(imgB_comp==0, np.nan, imgB_comp)

    # To all images . . . 
    # img1_sky = np.multiply(img1, fg_mask)
    # img2_sky = np.multiply(img2, fg_mask)
    pb1 = tqdm(range(len(imgs_R)), desc="Transforming images", leave=False)
    for itr in range(len(imgs_R)):
        # . . . apply mask
        imgs_R[itr] = np.multiply(imgs_R[itr], fg_mask)
        imgs_G[itr] = np.multiply(imgs_G[itr], fg_mask)
        imgs_B[itr] = np.multiply(imgs_B[itr], fg_mask)
        # . . . make zero values nan
        imgs_R[itr] = np.where(imgs_R[itr]==0, np.nan, imgs_R[itr])
        imgs_G[itr] = np.where(imgs_G[itr]==0, np.nan, imgs_G[itr])
        imgs_B[itr] = np.where(imgs_B[itr]==0, np.nan, imgs_B[itr])
        # . . . find transform to first image
        transfR, (source_list,target_list) = aa.find_transform(imgR_comp, imgs_R[itr])
        transfG, (source_list,target_list) = aa.find_transform(imgG_comp, imgs_G[itr])
        transfB, (source_list,target_list) = aa.find_transform(imgB_comp, imgs_B[itr])
        # . . . apply transform
        imgs_R[itr] = ( aa.apply_transform(transfR, imgR_comp, imgs_R[itr]))[0]
        imgs_G[itr] = ( aa.apply_transform(transfG, imgG_comp, imgs_G[itr]))[0]
        imgs_B[itr] = ( aa.apply_transform(transfB, imgB_comp, imgs_B[itr]))[0]
        # Update progress bar
        pb1.update(1)

    # Make nan values 0 for comparison images
    imgR_comp[np.isnan(imgR_comp)] = 0.0
    imgG_comp[np.isnan(imgG_comp)] = 0.0
    imgB_comp[np.isnan(imgB_comp)] = 0.0

    # Combine all the aligned images
    pb2 = tqdm(range(len(imgs_R)), desc="Combining images", leave=False)
    imgR_aligned = imgR_comp
    imgG_aligned = imgG_comp
    imgB_aligned = imgB_comp
    for imgR,imgG,imgB in zip(imgs_R,imgs_G,imgs_B):
        imgR[np.isnan(imgR)] = 0.0
        imgG[np.isnan(imgG)] = 0.0
        imgB[np.isnan(imgB)] = 0.0
        imgR_aligned += imgR
        imgG_aligned += imgG
        imgB_aligned += imgB
        pb2.update(2)
    imgR_aligned /= len(imgs_R)+1
    imgG_aligned /= len(imgs_G)+1
    imgB_aligned /= len(imgs_B)+1

    # Add foreground back in
    imgR_aligned += fg_img_R
    imgG_aligned += fg_img_G
    imgB_aligned += fg_img_B

    # Make 0 values nan
    # img1_sky = np.where(img1_sky==0, np.nan, img1_sky)
    # img2_sky = np.where(img2_sky==0, np.nan, img2_sky)
    
    # transf, (source_list, target_list) = aa.find_transform(img1_sky, img2_sky)

    # img1_sky[np.isnan(img1_sky)] = 0.0
    # img2_sky[np.isnan(img2_sky)] = 0.0
    # newimg = (aa.apply_transform(transf, img1_sky, img2_sky))[0]

    # combined = (1/2)*(newimg+img1_sky)

    fits.writeto('/home/ben/Desktop/testcombine_R.fits', imgR_aligned, overwrite=True)
    fits.writeto('/home/ben/Desktop/testcombine_G.fits', imgG_aligned, overwrite=True)
    fits.writeto('/home/ben/Desktop/testcombine_B.fits', imgB_aligned, overwrite=True)
