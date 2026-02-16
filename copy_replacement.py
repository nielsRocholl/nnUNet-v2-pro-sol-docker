"""
When copying files from a compute node to a storage server on DIAG's cluster, using the
standard shutil copy() and copytree() functions leads to errors. These functions copy
files but also try to copy metadata such as permissions, and our storage servers do not
support that. This module defines replacement functions.
"""
import os
import re

nnunet_path = "/root/nnunet/nnunetv2"

# Get all python files
pythonfiles = [os.path.join(root, name)
             for root, dirs, files in os.walk(nnunet_path)
             for name in files
             if name.endswith(".py")]

for filename in pythonfiles:
    # print("checking", filename)
    with open(filename, "r") as file:
        lines = file.readlines()
        
    with open(filename, "w") as file:
        for line in lines:
            if re.search(r"shutil\.copy", line):
                print("replace", line)
                line = re.sub(r"shutil\.copy", "shutil_sol.copyfile", line)
                file.write(line)
                print("with", line)
            elif re.search(r"copy_file\(", line):
                # distutils used in plan_and_preprocess_api.py
                print("replace", line)
                line = re.sub(r"copy_file", "shutil_sol.distutils_copyfile", line)
                file.write(line)
                print("with", line)
            else:
                file.write(line)
                if re.search(r"import\s+shutil", line):
                    print("adding shutil_sol import")
                    # Ensure correct indentation level
                    indentation = len(line) - len(line.lstrip())
                    indent_str = line[:indentation]
                    file.write(f"{indent_str}import nnunetv2.utilities.shutil_sol as shutil_sol \n")
                elif re.search(r"from\s+distutils.file_util\s+import\s+copy_file", line):
                    print("adding distutils_copyfile import")
                    # Ensure correct indentation level
                    indentation = len(line) - len(line.lstrip())
                    indent_str = line[:indentation]
                    file.write(f"{indent_str}import nnunetv2.utilities.shutil_sol as shutil_sol \n")
