# TAKIM 3
# Mertcan TOMBAK - 170419036
# Batikan Cagri SAVCI - 170419014
# Emir Muhammet AYDEMIR - 171419008

# Asagidaki tum kutuphaneler onerilen Python 3.7 interpreter'i kullanilarak import edilmelidir.
# Ana kutuphaneler
import time, math, numpy as np
import cv2
import pyautogui
import autopy

# Fonksiyonel ve gerekli kutuphaneler
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from pynput.keyboard import Controller

# El izleme modulu
import HandTrackingModule as handtm

# Degiskenler
pTime = 0  # fps hesaplama
wCam = 640  # en
hCam = 480  # boy
keyboard = Controller()

# Kayit alma ve ekran boyutlari tanimlandi
capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
capture.set(3, wCam)
capture.set(4, hCam)

# El dedektoru nesnesi olusturuldu
detector = handtm.handDetector(maxHands=1, detectionCon=0.85, trackCon=0.8)

# Ses degisim islemleri icin cihaz ve arayuz tanimlandi
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volumeCast = cast(interface, POINTER(IAudioEndpointVolume))

# Ses degisim fonksiyonu icin cihaza uygun range bilgileri ayarlandi
volumeRange = volumeCast.GetVolumeRange()  # (-65.25, 0.0, 0.03125)
minVol = -60
maxVol = 0.0
hmin = 25
hmax = 150
volumeBar = 400
volumePercent = 0
volume = 0

# Ek birkac degisken ileri islemler icin baslatildi
color = (0, 215, 255)
tipIds = [4, 8, 12, 16, 20]
mode = ''
active = 0
pressFlag = False
pyautogui.FAILSAFE = False


# Mod bilgisini ekrana yazdirirken kullanilacak fonksiyon
def putText(mode, loc=(250, 450), color=(0, 255, 255)):
    cv2.putText(image, str(mode), loc, cv2.FONT_HERSHEY_COMPLEX_SMALL,
                3, color, 3)


# Programin calisacagi ana dongu
while True:
    # O an kaydedilen goruntuden bir imaj aliniyor ve onun uzerinde calisiliyor
    # Bu islem milisaniyeler icerisinde gerceklesiyor
    success, image = capture.read()
    image = detector.findHands(image)

    # Hand tracking modulu yardimi ile goruntudeki el-parmaklar algilaniyor
    # Parmaklar landmark (isaret noktalari) ile belirtiliyor
    lmList = detector.findPosition(image, draw=False)

    # Parmaklarin acik kapali durumunun tutuldugu dizi
    fingers = []

    # Landmark noktalari arasindaki iliskiler incelenerek parmaklarin acik/kapali
    # durumlari ilgili diziye ekleniyor.
    if len(lmList) != 0:
        # Basparmak icin acik/kapali tespiti
        # NOT: Iki el icin ters yonlerde oldugundan ayri olarak ele alindi
        if lmList[tipIds[0]][1] > lmList[tipIds[0 - 1]][1]:
            if lmList[tipIds[0]][1] >= lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        elif lmList[tipIds[0]][1] < lmList[tipIds[0 - 1]][1]:
            if lmList[tipIds[0]][1] <= lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        # Diger dort parmak icin acik/kapali tespiti
        for id in range(1, 5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        # Kullanicinin ne yapmak istedigi fonksiyon seciliyor
        # Not: Modlar arasi gecis yaparken onceki moddan cikmak icin oncelikle "Free" moda gecis yapilmalidir.

        # Free mod icin 1-1-1-1-1 yani tum parmaklar acik olmalidir.
        if (fingers == [1, 1, 1, 1, 1]) & (active == 0):
            mode = 'Free'

        # Yukari Scroll mod icin 0-1-0-0-0 yani sadece isaret parmagi acik olmalidir.
        # Asagi Scroll mod icin 0-1-1-0-0 yani isaret ve orta parmak acik olmalidir.
        elif (fingers == [0, 1, 1, 0, 0] or fingers == [0, 1, 0, 0, 0]) & (active == 0):
            mode = 'Scroll'
            active = 1

        # Ses ayarlama modu icin 1-1-0-0-0 yani basparmak ve isaret parmagi acik olmalidir.
        elif (fingers == [1, 1, 0, 0, 0]) & (active == 0):
            mode = 'Volume'
            active = 1

        # Oyun modu icin 0-0-0-0-0 yani tum parmaklar kapali olmalidir.
        elif (fingers == [0, 0, 0, 0, 0]) & (active == 0):
            mode = 'Game'
            active = 1

        # Uygulamayi kapatmak icin 0-0-0-0-1 yani sadece serce parmak acilmalidir.
        elif (fingers == [0, 0, 0, 0, 1]) & (active == 0):
            mode = 'Break'

    # Scroll modu icin islemler
    if mode == 'Scroll':
        putText(mode)
        cv2.rectangle(image, (200, 410), (245, 460), (255, 255, 255), cv2.FILLED)
        if len(lmList) != 0:
            if fingers == [0, 1, 0, 0, 0]:
                putText(mode='Up', loc=(200, 455), color=(0, 255, 0))
                pyautogui.scroll(200)
            if fingers == [0, 1, 1, 0, 0]:
                putText(mode='Down', loc=(200, 455), color=(0, 0, 255))
                pyautogui.scroll(-200)
            elif fingers == [1, 1, 1, 1, 1]:
                active = 0
                mode = 'Free'
    # Volume modu icin islemler
    if mode == 'Volume':
        putText(mode)
        if len(lmList) != 0:
            if fingers == [1, 1, 1, 1, 1]:
                active = 0
                mode = 'Free'
                print(mode)
            else:
                x1, y1 = lmList[tipIds[0]][1], lmList[tipIds[0]][2]
                x2, y2 = lmList[tipIds[1]][1], lmList[tipIds[1]][2]
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                cv2.circle(image, (x1, y1), 10, color, cv2.FILLED)
                cv2.circle(image, (x2, y2), 10, color, cv2.FILLED)
                cv2.line(image, (x1, y1), (x2, y2), color, 3)
                cv2.circle(image, (cx, cy), 8, color, cv2.FILLED)
                length = math.hypot(x2 - x1, y2 - y1)

                volume = np.interp(length, [hmin, hmax], [minVol, maxVol])
                volumeBar = np.interp(volume, [minVol, maxVol], [400, 150])
                volumePercent = np.interp(volume, [minVol, maxVol], [0, 100])
                print(volume)
                volN = int(volume)
                if volN % 4 != 0:
                    volN = volN - volN % 4
                    if volN >= 0:
                        volN = 0
                    elif volN <= -64:
                        volN = -64
                    elif volume >= -11:
                        volN = volume
                volumeCast.SetMasterVolumeLevel(volume, None)
                if length < 50:
                    cv2.circle(image, (cx, cy), 11, (0, 0, 255), cv2.FILLED)
                cv2.rectangle(image, (30, 150), (55, 400), (209, 206, 0), 3)
                cv2.rectangle(image, (30, int(volumeBar)), (55, 400), (215, 255, 127), cv2.FILLED)
                cv2.putText(image, f'{int(volumePercent)}%', (25, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (209, 206, 0), 3)
    # Gaming modu icin islemler
    if mode == 'Game':
        putText(mode)
        cv2.rectangle(image, (110, 20), (620, 350), (255, 255, 255), 3)
        if fingers[1:] == [1, 1, 1, 1]:
            active = 0
            mode = 'Free'
            print(mode)
        else:
            if len(lmList) != 0:
                lmX, lmY = lmList[tipIds[1]][1], lmList[tipIds[1]][2]
                width, height = autopy.screen.size()
                x = int(np.interp(lmX, [110, 620], [0, width - 1]))
                y = int(np.interp(lmY, [20, 350], [0, height - 1]))
                cv2.circle(image, (lmList[tipIds[1]][1], lmList[tipIds[1]][2]), 7, (255, 255, 255), cv2.FILLED)
                cv2.circle(image, (lmList[tipIds[0]][1], lmList[tipIds[0]][2]), 10, (0, 255, 0), cv2.FILLED)
                if x % 2 != 0:
                    x = x - x % 2
                if y % 2 != 0:
                    y = y - y % 2
                print("Position: " + str(x) + " , " + str(y))
                autopy.mouse.move(x, y)
                if fingers[0] == 1:
                    cv2.circle(image, (lmList[tipIds[0]][1], lmList[tipIds[0]][2]), 10, (0, 0, 255), cv2.FILLED)
                    pressFlag = True
                if fingers[0] == 0:
                    if pressFlag:
                        print('t')
                        keyboard.press("t")
                        keyboard.release("t")
                        pressFlag = False
    # Programin ve capture islemlerinin sonlandirilmasi
    if mode == 'Break':
        print("Shutdown")
        time.sleep(1)
        capture.release()
        cv2.destroyAllWindows()
        break
    cTime = time.time()
    fps = 1/((cTime + 0.01) - pTime)
    pTime = cTime

    # FPS gostergesi ve capture penceresi
    cv2.putText(image, f'FPS:{int(fps)}', (480, 50), cv2.FONT_ITALIC, 1, (255, 0, 0), 2)
    cv2.imshow('Hand Gesture Project', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
