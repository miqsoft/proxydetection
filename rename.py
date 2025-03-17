import os

def rename_tlscrypt(path):
    # First, rename directories from deepest level to top to avoid path issues
    for root, dirs, files in os.walk(path, topdown=False):
        # Rename files
        for filename in files:
            if "_tlscrypt" in filename:
                old_file = os.path.join(root, filename)
                new_file = os.path.join(root, filename.replace("_tlscrypt", ""))
                print(f"Renaming file: {old_file} -> {new_file}")
                os.rename(old_file, new_file)
        
        # Rename directories
        for dirname in dirs:
            if "_tlscrypt" in dirname:
                old_dir = os.path.join(root, dirname)
                new_dir = os.path.join(root, dirname.replace("_tlscrypt", ""))
                print(f"Renaming directory: {old_dir} -> {new_dir}")
                os.rename(old_dir, new_dir)

if __name__ == "__main__":
    # Change this to the path where you want to perform renaming
    target_path = "./"  # Current directory
    rename_tlscrypt(target_path)
