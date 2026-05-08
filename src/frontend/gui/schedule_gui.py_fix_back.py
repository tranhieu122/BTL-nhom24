
import sys

path = r'C:\Users\thesh\Downloads\BTL-nhom24-main - Copy\BTL-nhom24-main\src\frontend\gui\schedule_gui.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if i >= 509: # line 510 onwards
        new_lines.append('    ' + line) # add back 4 spaces
    else:
        new_lines.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
