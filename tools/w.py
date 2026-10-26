"""Ввод в ВМ Win11-lab и снимки (основа — ~/op05-shots-work/vm.py)."""
import sys, time
from pathlib import Path
sys.path.insert(0, str(Path.home() / 'op05-shots-work'))
import vm
vm.VM = 'Win11-lab'
vm.OUT = Path(__file__).parent / 'win'
vm.KEYS.update({'win+r': 'e0 5b 13 93 e0 db', 'win+space': 'e0 5b 39 b9 e0 db', 'alt+shift': '38 2a aa b8',
  'win+left': 'e0 5b e0 4b e0 cb e0 db', 'win+right': 'e0 5b e0 4d e0 cd e0 db', 'ctrl+shift+esc': '1d 2a 01 81 aa 9d',
  'alt+tab': '38 0f 8f b8', 'tab': '0f 8f', 'shift+tab': '2a 0f 8f aa', 'down': 'e0 50 e0 d0', 'up': 'e0 48 e0 c8',
  'right': 'e0 4d e0 cd', 'left': 'e0 4b e0 cb', 'space': '39 b9', 'alt+f4': '38 3e be b8', 'ctrl+f': '1d 21 a1 9d',
  'ctrl+d': '1d 20 a0 9d', 'ctrl+h': '1d 23 a3 9d', 'f10': '44 c4', 'menu': 'e0 5d e0 dd', 'shift+f10': '2a 44 c4 aa',
  'win+up': 'e0 5b e0 48 e0 c8 e0 db', 'ctrl+a': '1d 1e 9e 9d', 'esc': '01 81', 'enter': '1c 9c'})
if __name__ == '__main__':
    a = sys.argv[1:]
    if a[0] == 'shot': vm.shot(a[1])
    elif a[0] == 'key':
        for k in a[1:]: vm.key(k); time.sleep(0.6)
    elif a[0] == 'cmd': vm.cmd(' '.join(a[1:]), pause=1.5)
    elif a[0] == 'text': vm.text(' '.join(a[1:]))
    elif a[0] == 'run': vm.run(a[1])
