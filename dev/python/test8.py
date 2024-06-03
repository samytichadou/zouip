
import os

path = r"/home/tonton/Documents/Notes"
path = path.lstrip(os.sep)  # Get rid of leading "/" if any
root = path[:path.index(os.sep)] if os.sep in path else path
print(root)

# traverse root directory, and list directories as dirs and files as files
# size = 0
# for root, dirs, files in os.walk(path):
#     R = root
#     for f in files:
#         print()
#         print(f)
#         print(root)
#         print(root.replace(R, ""))
# print(size)

root_dir = path
dir = os.path.basename(root_dir)
for root, dirs, files in os.walk(root_dir):
    for f in files:
        rel_dir = os.path.join(
            dir,
            os.path.relpath(root, root_dir)
        )
        print(f)
        print(rel_dir)
