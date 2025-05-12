import os
import shutil


class LocalFileGetter:
    def get_object_to_file(self, object_key, local_file):
        shutil.copy2(source_file, destination_file)

    # --- Helper function to read object content from OSS ---
    def read_object_content(self, object_key, encoding='utf-8'):
        try:
            if encoding != '':
                with open(object_key, 'r', encoding=encoding) as f:
                    return f.read()
            else:
                with open(object_key, 'rb') as f:
                    return f.read()
        except FileNotFoundError:
            print(f"Error: File not found at {object_key}")
            raise 
        except Exception as e:
            print(f"An error occurred reading file {object_key}: {e}")
            raise 
    
    def iterate_object_at(self, prefix):
        try:
            with os.scandir(prefix) as entries:
                for entry in entries:
                    if entry.is_file(): 
                        yield File(entry.path) 
        except FileNotFoundError:
            print(f"Error: Directory not found: {prefix}")
        except NotADirectoryError:
            print(f"Error: Path is not a directory: {prefix}")

class File:
    def __init__(self, object_key):
        self.key = object_key
        
def initialize():
    return LocalFileGetter()