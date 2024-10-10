import os
import sys
import shutil
import re
import time

##Create log file and go from there ? 
def seperate_create_master_odd_even_files(supplied_folder_name):
    ''' go through the supplied images folder , the files should be of the format 00000.jpg 00001.jpg etc,
    and create and off directories like odd_supplied_folder_name_master , even_supplied_folder_name_master and copy the images based on wethere they are odd or even '''

    # check if the supplied folder exists
    if not os.path.exists(supplied_folder_name):
        print("The supplied folder does not exist")
        return
    
    files = os.listdir(supplied_folder_name)
    
    odd_dir = os.path.join(supplied_folder_name + "_odd_master")
    if not os.path.exists(odd_dir):
        os.makedirs(odd_dir)
    even_dir = os.path.join(supplied_folder_name + "_even_master")
    if not os.path.exists(even_dir):
        os.makedirs(even_dir)

    pattern = re.compile(r'^\d{5}\.jpg$')
    even_counter = 0
    odd_counter = 0 

    for file in files:
        if pattern.match(file):
            print("Processing file: ", file)
            # get the number from the file name
            number = int(file.split(".")[0])
            if number % 2 == 0:
                new_file_name = f"{even_counter:05d}.jpg"
                shutil.copy(os.path.join(supplied_folder_name, file), os.path.join(even_dir, new_file_name))
                even_counter += 1
            else:
                new_file_name = f"{odd_counter:05d}.jpg"
                shutil.copy(os.path.join(supplied_folder_name, file), os.path.join(odd_dir, new_file_name))
                odd_counter += 1

def create_odd_even_colmap_training(even_number,central_log_file):
    ## colmap is run only from the even numbered images and odd numbered images are copied over 
    odd_number = 98-even_number
    colmap_dir = "colmap_even_master_number" + str(even_number)
    colmap_final_dir = "colmap_odd+even_master_number" + str(even_number) + "_" + str(odd_number)
    central_log_file.write("Processing even images : " + str(even_number) + " and odd images : " + str(odd_number) + "\n")
    if not os.path.exists(colmap_dir):
        os.makedirs(colmap_dir)
        if not os.path.exists(os.path.join(colmap_dir, "input")):
            os.makedirs(os.path.join(colmap_dir, "input"))
    if not os.path.exists(colmap_final_dir):
        os.makedirs(colmap_final_dir)
        if not os.path.exists(os.path.join(colmap_final_dir, "input")):
            os.makedirs(os.path.join(colmap_final_dir, "input"))
    for i in range(0, even_number):
        shutil.copy(os.path.join("coffee_images_even_master", f"{i:05d}.jpg"), os.path.join(colmap_dir, f"input/{i:05d}.jpg"))

    for i in range(0, odd_number):
        k = 98 - i
        shutil.copy(os.path.join("coffee_images_odd_master", f"{i:05d}.jpg"), os.path.join(colmap_final_dir, f"input/{k:05d}.jpg"))
    for i in range(0,even_number):
        shutil.copy(os.path.join("coffee_images_even_master", f"{i:05d}.jpg"), os.path.join(colmap_final_dir, f"input/{i:05d}.jpg"))

    
    ## run colmap point cloud generation on the even images
    print("Running colmap point cloud generation on the even images")
    colmap_command_even = "python convert.py -s " + colmap_dir
    colmap_command_even_start_time = time.time()
    os.system(colmap_command_even)
    colmap_command_even_stop_time = time.time()
    colmap_command_even_time = colmap_command_even_stop_time - colmap_command_even_start_time
    central_log_file.write("Colmap command even time : " + str(colmap_command_even_time) + "\n")

    ## run colmap point cloud generation on the combined odd and even images
    print("Running colmap point cloud generation on the combined odd and even images")
    colmap_command_combined = "python convert.py -s " + colmap_final_dir
    colmap_command_combined_start_time = time.time()
    os.system(colmap_command_combined)
    colmap_command_combined_stop_time = time.time()
    colmap_command_combined_time = colmap_command_combined_stop_time - colmap_command_combined_start_time
    central_log_file.write("Colmap command combined time : " + str(colmap_command_combined_time) + "\n")
    

    ##copy point3d.bin file from the even run to the combined run
    remove_command = "rm " + os.path.join(colmap_final_dir, "sparse/0/points3D.bin")
    copy_command = "cp " + os.path.join(colmap_dir, "sparse/0/points3D.bin") + " " + os.path.join(colmap_final_dir, "sparse/0/points3D.bin")
    os.system(remove_command)
    os.system(copy_command)

    ##run gsplat training on the combined run 
    print("Running gsplat training on the combined run")
    output_folder = "output" + str(even_number) + "_" + str(odd_number)
    training_command = "python3 train.py  -s " + colmap_final_dir + " -m " + output_folder
    training_command_start_time = time.time()
    os.system(training_command)
    training_command_stop_time = time.time()
    training_command_time = training_command_stop_time - training_command_start_time
    central_log_file.write("Training command time : " + str(training_command_time) + "\n")
    central_log_file.write("-------------------------------------------------------------------------------------\n")
    central_log_file.write("\n\n\n\n\n")


if __name__ == "__main__":
    seperate_create_master_odd_even_files("coffee_images")
    central_log_file_txt = "log_file.txt"
    central_log_file = open(central_log_file_txt, "a")

    for i in range(0, 99):
        k = 98 - i
        create_odd_even_colmap_training(k,central_log_file)
    
    central_log_file.close()
    # create_odd_even_colmap_training(98)