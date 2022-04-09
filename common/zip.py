import shutil

class Zip:
    def __init__(self,zipfile_path,folder_path):
        shutil.make_archive(zipfile_path, 'zip', folder_path)

if __name__ == '__main__':
    zipobj = Zip('test','../common')