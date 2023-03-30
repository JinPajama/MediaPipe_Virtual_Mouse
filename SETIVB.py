import subprocess
import keyboard

while True:
    # AIVM.py 실행
    subprocess.run(['python', 'AIVM.py'])
    # AIVB.py 실행
    subprocess.run(['python', 'AIVB.py'])
    # 키보드 이벤트 처리