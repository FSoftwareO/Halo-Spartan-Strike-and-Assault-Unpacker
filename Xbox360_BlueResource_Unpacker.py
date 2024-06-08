import os
# This script is for the Xbox 360 version
# makesure = 203000 leaving unused for now since I do not own the 360 version. this was used for a size comparison originally
ddsh = b'\x44\x44\x53\x20\x7C\x00\x00\x00' # dds checker but the xbox 360 version may not use dds files
fsb = b'\x46\x53\x42\x34\x01\x00\x00\x00' # fsb checker
sigcheck = b'\x12\x34\x56\x78' # BlueResource checker for the xbox 360 version
ext1 = ".dds" # for dds extension
ext2 = ".bin" # for bin extension
ext3 = ".fsb" # for fsb extension
extension = ".BlueResourceXbox360" # BlueResource container file extension
errorfile = "error.txt" # error file
skippedfile = "skipped.txt" # file to show files skipped that were considered invalid BlueResource files.
finish = "Task finished."
ERROR_SIG_MISMATCH = 1 # signature error
ERROR_NO_FILE = 2 # no dropped file error
ERROR_PERMISSION = 3 # file permission error
ERROR_UNKNOWN = 4 # other errors
ERROR_WRONG = 5 # for modified BlueResource files
def rem(file): # To remove the error file and skipped file when script is executed so that old error files are not kept
    if os.path.isfile(file):
        os.remove(file)
def helpu(file, err_code, sig=None, list_file=None, sigcheck=None): # Error handling
    if err_code == ERROR_SIG_MISMATCH:
        err_msg = f"The signature '{sig}' within the file '{list_file}' does not match the correct signature '{sigcheck}' that BlueResource files have."
    elif err_code == ERROR_NO_FILE:
        err_msg = "There isn't a BlueResourcePC_Windows file within the current directory."
    elif err_code == ERROR_PERMISSION:
        err_msg = f"Permission error occurred while accessing the file '{list_file}'. Please check your file permissions."
    elif err_code == ERROR_UNKNOWN:
        err_msg = "An unknown error occured."
    with open(file, "w") as w1:
        w1.write(err_msg)
    raise SystemExit(err_code)

def helpo(file, err_code, listed_file=None): # For error handling but without closing
    if err_code == ERROR_WRONG:
        err_msg = f"The file '{listed_file}' is not a valid BlueResource file and has been skipped. Has that file been altered?\n"
    with open(file, "a") as w1:
        w1.write(err_msg)
        return True
    return False

def arga(): # Unpacking
    try:
        files = os.listdir(os.getcwd()) # get files within current directory
        files_with = [file for file in files if file.endswith(extension)] # get files with the extension
        total_files = len(files_with)  # Count the number of files with the extension
        if total_files == 0: # if 0 files in directory with the required extension
            helpu(errorfile, ERROR_NO_FILE)
        print(f"There are {total_files} files with the .BlueResourcePC_Windows extension.")
    except FileNotFoundError: # if no files in directory
        helpu(errorfile, ERROR_NO_FILE)
    except Exception as e: # for any other errors
        helpu(errorfile, ERROR_UNKNOWN, str(e))
    for file in files_with:
        try:
            with open(file, "r+b") as f1: # The file
                sig = f1.read(4) # signature
                if sig != sigcheck: # if signature does not match
                    helpu(errorfile, ERROR_SIG_MISMATCH, sig=sig, list_file=file, sigcheck=sigcheck)
                e1 = 0 # incrementer for dds files
                e2 = 0 # incrementer for bin files
                e3 = 0 # incrementer for fsb files
                gname = os.path.splitext(os.path.basename(file))[0] # get the filename without extension for incrementing
                os.makedirs(gname, exist_ok = True) # create directory
                bin_folder = os.path.join(gname, "bin") # for bin folder
                dds_folder = os.path.join(gname, "DDS") # for dds folder
                fsb_folder = os.path.join(gname, "BlueResource_FSB") # folder for fsb files within the containers
                ugx_folder = os.path.join(gname, "UGX") # for ugx folder
                os.makedirs(bin_folder, exist_ok=True) # make bin folder
                os.makedirs(dds_folder, exist_ok=True) # make dds folder
                os.makedirs(fsb_folder, exist_ok=True) # make fsb folder
                lis = [] # list to store file sizes
                unk1 = f1.read(8) # unknown
                entrysecs = int.from_bytes(f1.read(4), "big") # amount of file entry sections across the entire container file, specified at offset 12 of each container file
                for j in range(0, entrysecs): # main loop to be used for file entry sections
                    che = f1.tell() # Check current file entry section offset
                    unk2 = f1.read(12) # unknown
                    entryamount = int.from_bytes(f1.read(4), "big") # total file entries within the current file entry section.
                    #print(f"File entry section {j} at offset {che} in the container file")
                    for i in range(0, entryamount): # for metadata within file entry section 1 onwards
                        unk3 = f1.read(12) # unknown
                        size = int.from_bytes(f1.read(4), "big") # file size for current file entry within the current file entry section
                        lis.append(size) # append size of the currently read file entry metadata
                    lis.reverse() # reverse list for file sizes.
                    for a in range(0, entryamount): # file data that begins after the final file entry. If the section had 15 file entries then file data 1 for file entry 1 begins after file entry 15.
                        data = f1.read(lis.pop()) # read by the popped amount from the first read file size in the list
                        if ddsh in data: # if the dds header was present
                            header_index = data.index(ddsh) # Find the index of the DDS header
                            data = data[header_index:] # Extract data starting from the DDS header  
                            e1 += 1 # increment by 1 for the filename using the dds extension
                            fname1 = gname + str(e1) + ext1 # combine the container's filename, file incrementer, and extension
                            with open(os.path.join(dds_folder, fname1), "wb") as f2: # write the incremented file to the folder
                                f2.write(data)  # Write data starting from the DDS header position
                        elif fsb in data: # if the fsb header was present
                            fsb_index = data.index(fsb)
                            data = data[fsb_index:]
                            e3 += 1
                            fname3 = gname + str(e3) + ext3
                            with open(os.path.join(fsb_folder, fname3), "wb") as f3: # write the incremented file to the folder
                                f3.write(data)  # Write data starting from the fsb header position
                        else: # if neither a dds or fsb header was present
                            e2 += 1 # increment by 1 for the filename using the bin extension
                            fname2 = gname + str(e2) + ext2 # combine the container's filename, file incrementer, and extension
                            with open(os.path.join(bin_folder, fname2), "wb") as f4: # write the incremented file to the folder
                                f4.write(data)
        except PermissionError: # if a permission error occurs with file handling
            helpu(errorfile, ERROR_PERMISSION, list_file=file)
        except Exception as w: # for any other errors
            helpu(errorfile, ERROR_UNKNOWN)
    input(finish)
if __name__ == "__main__":
    rem(errorfile)
    rem(skippedfile)
    arga()
