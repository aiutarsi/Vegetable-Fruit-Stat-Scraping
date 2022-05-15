import shutil
import os

path = os.getcwd()
files = os.listdir(path)
files_file = [f for f in files if (os.path.isfile(os.path.join(path, f)))]

for f in files_file:
  zip_without_dot = os.path.splitext(f)[1][1:]
  if (zip_without_dot == 'zip'):
    shutil.unpack_archive(f, 'data')
    os.remove(f)

