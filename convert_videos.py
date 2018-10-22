#!/usr/bin/env python3
__author__ = "piquesel"


import argparse
import logging
import os
import subprocess
import sys
import time

from pathlib import Path
from shutil import rmtree

LOG_FILENAME = 'convert_videos.log'
logging.basicConfig(filename=LOG_FILENAME,
                    level=logging.DEBUG)
ffmpeg = "/Users/brouchouse/bin/ffmpeg"
exclude_files = ["LG Smart TV", "$RECYCLE.BIN"]
# source_directory = "/Volumes/Videos"
source_directory = "/Users/brouchouse/Desktop/videos"
output_dir = "/Users/brouchouse/Videos"


def get_arguments():
    parser = argparse.ArgumentParser("Use the following arguments:")
    parser.add_argument("-dr", "--dryrun", help="Simulate a dry run.",
                        action="store_true", required=False)
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    return parser.parse_args()


def save_file(file_name, data):
    with open(file_name, "a") as f_output:
        for item in data:
            f_output.write(item[0] + item[1] + "\n")


def absolute_file_paths(directory):
    if not os.path.exists(directory):
        sys.exit("The directory {} doesn't exist".format(directory))
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


def check_extension(file):
    if not file.lower().endswith(('.avi', '.mov')):
        with open("exclude_files.txt", "a") as f_exclude:
            f_exclude.write(file)
            return False
    return True


def main():
    try:
        os.remove("exclude_files.txt")
        os.remove("files_to_convert.txt")
        os.remove("raw_files_to_convert.txt")
        rmtree(output_dir)
    except OSError:
        pass

    # Get arguments passed
    args = get_arguments()

    raw_files_to_convert = []
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Fetch files to copy
    my_files = absolute_file_paths(source_directory)
    for f in my_files:
        if check_extension(f) is True:
            with open("raw_files_to_convert.txt", "a") as f_output:
                f_output.write(f+"\n")
            directory = os.path.dirname(f)
            filename = os.path.basename(f)
            raw_files_to_convert.append((directory, filename))
    files_to_convert = [item for item in raw_files_to_convert
                        if item[0].split('/')[3] not in exclude_files]
    save_file("files_to_convert.txt", files_to_convert)

    print("Number of raw files to convert: {}".
          format(len(raw_files_to_convert)))
    print("Number of files to convert: {}".
          format(len(files_to_convert)))

    total_time = 0

    for (d, f) in files_to_convert:
        orig_file = d + "/" + f
        dest_dir = output_dir + d[len(source_directory):]
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        if f.endswith(".mov") or f.endswith(".MOV"):
            new_file = Path(f).stem + ".mpeg"
        elif f.endswith(".avi"):
            new_file = Path(f).stem + ".mpeg"
        else:
            logging.debug('Unknown extension')
        new_file = dest_dir + "/" + new_file
        if args.dryrun:
            result = subprocess.call(["touch", new_file])
        else:
            start_time = time.time()
            result = subprocess.call([ffmpeg, "-i", orig_file,
                                      "-c:v", "libx264", "-crf", "20",
                                      "-strict", "-2",
                                      new_file])
            delta_time = time.time() - start_time
            total_time += delta_time
            elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.time() -
                                                                 start_time))
            logging.debug("Time to convert {} = {}".format(orig_file,
                                                           elapsed_time))
            if result == 0:
                logging.debug("[+] {} converted successfully.".
                              format(orig_file))
            else:
                logging.debug("[-] {} conversion failed.")

            final_time = time.strftime("%H:%M:%S", time.gmtime(total_time))
            logging.debug("Total time to convert files = {}".
                          format(final_time))


if __name__ == '__main__':
    main()
