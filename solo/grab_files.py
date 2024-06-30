import os
import argparse
import sys
import hashlib
import time
import datetime
import random
import shutil


def generate_random_number():
    return random.randint(1000, 9999)  # Change the range as needed


def create_directory(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)


def human_readable_size(size_in_bytes):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(size_in_bytes) < 1024.0:
            return f"{size_in_bytes:.1f} {unit}B"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.1f} YiB"  # Supports all currently known binary prefixes

def move_file(source_path, destination_path):
    print(f"[*] Task: move {source_path}, to {destination_path}")

    try:
        #shutil.move(source_path, destination_path)
        os.rename(source_path, destination_path)
        print(f"[+] File moved successfully to '{destination_path}'.")
    except FileExistsError as e:
        print(f"[+] File moved successfully to '{destination_path}' name was changed.")
        base_name, extension = os.path.splitext(destination_path)
        random_suffix = generate_random_number()
        new_destination_path = f"{base_name}_{random_suffix}{extension}"
        move_file(source_path, new_destination_path)
        #shutil.move(source_path, new_destination_path)
    except FileNotFoundError as e:
        print(f"[-] Source file '{source_path}' does not exist.")
    except Exception as e:
        print(e)

def copy_file(source_path, destination_path):
    print(f"[*] Task: copy {source_path}, to {destination_path}")

    try:
        shutil.copy(source_path, destination_path)
        print(f"[+] File coped successfully to '{destination_path}'.")
    except FileExistsError as e:
        print(f"[+] File coped successfully to '{destination_path}' name was changed.")
        base_name, extension = os.path.splitext(destination_path)
        random_suffix = generate_random_number()
        new_destination_path = f"{base_name}_{random_suffix}{extension}"
        copy_file(source_path, new_destination_path)
        #shutil.move(source_path, new_destination_path)
    except FileNotFoundError as e:
        print(f"[-] Source file '{source_path}' does not exist.")
    except Exception as e:
        print(e)


def listAll(path, script_dir, move_files):
    for root, dirs, files in os.walk(path):
        for filename in files:
            filepath = os.path.join(root, filename)
            info = os.stat(filepath)

            formatted_creation_time = time.ctime(info.st_ctime)
            formatted_modification_time = time.ctime(info.st_mtime)
            formatted_access_time = time.ctime(info.st_atime)

            fc = datetime.datetime.strptime(formatted_creation_time, "%a %b %d %H:%M:%S %Y")
            fm = datetime.datetime.strptime(formatted_modification_time, "%a %b %d %H:%M:%S %Y")
            fa = datetime.datetime.strptime(formatted_access_time, "%a %b %d %H:%M:%S %Y")

            Tfc = str(fc).split(" ")
            Tfm = str(fm).split(" ")
            Tfa = str(fa).split(" ")

            dirfc = Tfc[0].replace("-","")
            dirfm = Tfm[0].replace("-","")
            dirfa = Tfa[0].replace("-","")
            
            md5_hash = ''
            sha1_hash = ''

            with open(filepath, 'rb') as file:
                data = file.read()
                md5_hash = hashlib.md5(data).hexdigest()
                sha1_hash = hashlib.sha1(data).hexdigest()
                #print(f"MD5: {md5_hash}")
                #print(f"SHA-1: {sha1_hash}\n")
            
            print(f"[*] File: {path}\{filename}, Size: {human_readable_size(info.st_size)}, CTIME: {fc}, MTIME: {fm}, ATIME: {fa}, Permissions (octal): {oct(info.st_mode & 0o777)}, Owner: {info.st_uid}, Group: {info.st_gid}, md5sum: {md5_hash}, sha1_hash: {sha1_hash}")

            create_dir = f"{script_dir}\{dirfm}"
            create_directory(create_dir)
            #print(f"[*] {create_dir}")
            source = filepath
            dest = f"{create_dir}\{filename}"

            if(move_files):
                move_file(source, dest)
            else:
                copy_file(source, dest)


if __name__ == '__main__':
    script_path = os.path.abspath(__file__)
    script_directory = os.path.dirname(script_path)
    script_dir = f"{script_directory}\work"
    print(f"[*] Current script path: {script_directory}")
    print(f"[*] Current workspace path: {script_dir}")
            
    parser = argparse.ArgumentParser(
        conflict_handler='resolve', 
        description='Check files MM wersja 0.1b',
        formatter_class=argparse.RawTextHelpFormatter
        )    

    parser.add_argument('-dc', '--dir-check', action='store', dest='dir_to_check', type=str, 
                        help='Path to directory with data.')
    
    parser.add_argument('-m', '--move-files', action='store', dest='move_files', type=bool, default=False,
                        help='Move files')

    args = parser.parse_args()

    if ('dir_to_check' not in args or not args.dir_to_check):
        parser.print_help()
        sys.exit(1)
    else:
        dir_to_check = args.dir_to_check
        move_files = args.move_files

        listAll(dir_to_check, script_dir, move_files)
