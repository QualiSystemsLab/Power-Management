from zipfile import ZipFile
import os

root_dir = 'src'

scripts = os.listdir(root_dir)
for script in scripts:
    zipfile = os.path.join('dist', script + '.zip')
    with ZipFile(zipfile, 'w') as build:
        back = os.getcwd()
        os.chdir(os.path.join(root_dir, script))
        for root, dirs, files in os.walk(".", topdown=False):
            for name in files:
                if name == 'quali_config.json':
                    continue
                build.write(os.path.join(root, name))
        build.close()
        os.chdir(back)

pass
