import os
import datetime
import exifread
import shutil
import concurrent.futures
from tqdm import tqdm

# specify the directory containing the images
dir_path = "/input/path"
out_path = "/output/path"


# create a dictionary to store the image files by date
image_dict = {}

def process_file(file_path):
    # read the file extension
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # check if the file is an image file
    if file_ext in ('.jpg', '.jpeg', '.png'):
        # read the EXIF metadata of the image to get the date taken
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f, details=False)
            date_taken = tags.get('EXIF DateTimeOriginal')
        
        # if the date taken is available
        if date_taken is not None:
            # convert the date taken to a datetime object
            date_taken_str = str(date_taken)
            date_taken_obj = datetime.datetime.strptime(date_taken_str, '%Y:%m:%d %H:%M:%S')
            
            # create a key for the image_dict based on the date taken
            date_key = date_taken_obj.strftime('%Y_%m_%d')
            
            # add the file to the dictionary
            if date_key in image_dict:
                image_dict[date_key].append(file_path)
            else:
                image_dict[date_key] = [file_path]

# get the list of files to process
file_list = os.listdir(dir_path)

# create a progress bar
progress_bar = tqdm(total=len(file_list), desc='Processing files')

# loop through all files in the directory
with concurrent.futures.ThreadPoolExecutor() as executor:
    for file_path in file_list:
        # get the full path of the file
        file_path = os.path.join(dir_path, file_path)
        
        # process the file using multiple threads
        executor.submit(process_file, file_path)
        
        # update the progress bar
        progress_bar.update(1)

# close the progress bar
progress_bar.close()

# create a progress bar for copying files
num_files = sum([len(file_list) for _, file_list in image_dict.items()])
progress_bar = tqdm(total=num_files, desc='Copying files')

# loop through the dictionary and copy the image files to their appropriate folders
for date_key, file_paths in image_dict.items():
    # create a folder for the images if it doesn't exist
    folder_path = os.path.join(out_path, date_key)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # copy the image files to the appropriate folder
    for file_path in file_paths:
        filename = os.path.basename(file_path)
        new_file_path = os.path.join(folder_path, filename)
        shutil.copy2(file_path, new_file_path)
        
        # update the progress bar
        progress_bar.update(1)

# close the progress bar
progress_bar.close()
