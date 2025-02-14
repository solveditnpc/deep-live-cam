import os
import time
import csv
import subprocess
import ffmpeg

framerate: float 
input_video:str  
output_folder:str  
image_folder: str
output_video: str

def command_prompt():
    source_image_path1 = input("Enter source image path: ")
    target_frame_directory1 = input("Enter target folder path: ")
    result_directory1 = input("Enter result folder path: ")
    n = int(input("Enter the total number of image's,you'd like to edit: "))
    s = int(input("Enter the image in the folder to start editing from: "))
    
    source_image_path = source_image_path1.replace("\\", "/").replace('"', '')
    target_frame_directory = target_frame_directory1.replace("\\", "/").replace('"', '')
    result_directory = result_directory1.replace("\\", "/").replace('"', '')
    
    command_template = 'python run.py --execution-provider cuda -s "{}" -t "{}/{}" -o "{}/{}" --nsfw-filter --keep-audio --keep-frames --frame-processor face_swapper face_enhancer'

    frame_timeout = 60
 
    missing_csv_path1 = os.path.join(result_directory, "missing.csv")
    missing_csv_path = missing_csv_path1.replace("\\","/").replace('"','')

   
    with open(missing_csv_path, mode='a', newline='') as missing_file:
        csv_writer = csv.writer(missing_file)
        csv_writer.writerow(["Missing Output Files", "Reason"])

        for i in range(s, n + 1):
            image_count = f"{i:04d}"
            image_number = f"{image_count}.png"
            try:
               
                command = command_template.format(source_image_path, target_frame_directory, image_number, result_directory, image_number)
                print(command)
              
                process = subprocess.Popen(command, shell=True)

                start_time = time.time()
                while process.poll() is None:
                    if time.time() - start_time > frame_timeout:
                        process.terminate() 
                        print(f"Frame {i} exceeded the timeout ({frame_timeout} seconds). Skipping to the next frame.")
                        break
                    time.sleep(1)  
                
                output_file = os.path.join(result_directory, f"{i:04d}.png")
                if os.path.exists(output_file):
                    print(f"Frame {i} processed successfully.")
                else:
                   
                    csv_writer.writerow([output_file, "Image processing issue"])
                    print(f"Frame {i} failed; missing output file. Reason: Face is not visible.")

            except AttributeError:
               
                reason = "check_and_ignore_nsfw failed to ignore,try cropping the face and attaching after swapping:("
                csv_writer.writerow([f"{i:04d}.png", reason])
                print(f"Frame {i} failed; {reason}.")
                continue


def video_to_frames(input_video, output_folder, f):
    try:
        (
            ffmpeg
            .input(input_video)
            .output(f'{output_folder}/%04d.png', vf=f'fps={f}')
            .run()
        )
        print(f"Frames extracted successfully to {output_folder}.")
        return "Success"  
    except ffmpeg.Error as e:
        print(f"An error occurred: {e}")
        return "Error" 


def create_video_from_image(image_folder, output_video, framerate):
    try:
        (
            ffmpeg
            .input(f'{image_folder}/%04d.png', framerate=framerate)
            .output(output_video, vcodec='libx264', pix_fmt='yuv420p')
            .run()
        )
        print("Video created successfully.")
    except ffmpeg.Error as e:
        print(f"An error occurred: {e.stderr.decode('utf8')}")

def main():
    n = int(input("enter 1: for converting a video to frames \n2: for editing the images in a folder \n3: for combining edited frames into a video\n"))
    if n == 1:
        input_video1 = input("Enter the path to the video file: ")
        output_folder1 = input("Enter the path to the output folder that you've created: ")
        f = float(input("Enter the fps of this video: "))

        input_video = input_video1.replace("\\", "/").replace('"','')
        output_folder = output_folder1.replace("\\", "/").replace('"','')
        video_to_frames(input_video, output_folder,f)
    elif n == 2:
        command_prompt()
    elif n == 3:
        image_folder1 = input("Enter the path to the images folder: ")
        output_video1 = input("Enter the path where you want to store your output video along with it's name: ")
        framerate = float(input("Enter the fps you want your video to have: "))
        image_folder = image_folder1.replace("\\", "/").replace('"','')
        output_video = output_video1.replace("\\", "/").replace('"','')
        create_video_from_image(image_folder, output_video, framerate)
    else:
        print("Enter a valid choice")
        exit

main()