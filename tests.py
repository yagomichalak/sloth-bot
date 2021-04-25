from treelib import Node, Tree
import os

tree = Tree()

ignore_files = ['venv', '__pycache__', '.git', '.gitignore']

tree.create_node('Root', 'root')

for file in os.listdir('./'):
    if file in ignore_files:
        continue

    if os.path.isdir(file):
        tree.create_node(file, file, parent='root')
        for subfile in (directory := os.listdir(f'./{file}')):
            if subfile in ignore_files:
                continue
            # print(f"{file} -> {subfile}")
            tree.create_node(subfile, subfile, parent=file)

    else:
        # print(f"{file}")
        tree.create_node(file, file, parent='root')


tree.show(line_type="ascii-em")