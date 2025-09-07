import subprocess
import fs

sass = [
    r"C:\bin\sass.bat",
    r"C:\Bin\lib\dart-sass\sass.bat",
]
exe = None
for file in sass:
    if fs.file_exists(file):
        exe = file

# subprocess.run([exe, '--watch', '--style=compressed', 'sass:../static/maven'])
# subprocess.run([exe, '--watch', 'sass:../static/maven'])
subprocess.run([exe, 'sass/maven-midnight.scss', '../static/maven/maven-midnight.css'])
print("Done.")
