import subprocess
import sys

m = 'town01'
intersection = 87
view_im = False

command = ['poetry', 'run', 'scenic']
command.extend(['-b'])
command.extend(['--zoom', '0'])
# command.extend(['-v', str(verbosity)])
command.extend(['-p', 'outputWS', 'fse'])
command.extend(['-p', 'outputDir', 'figs'])

command.extend(['-p', 'vis-figs', 'src'])
command.extend(['-p', 'intersectiontesting', f'{intersection}'])

command.extend(['-p', 'viewImgs', str(view_im)])

command.extend(['-p', 'map', f'maps/{m}.xodr'])
command.append(f'fse/config/dummy1.scenic')
p = subprocess.Popen(command, stderr=sys.stderr, stdout=sys.stdout)

p.wait()
print()

