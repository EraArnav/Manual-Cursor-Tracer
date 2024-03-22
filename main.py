import cv2
import numpy as np
import htm
import time
import pyautogui
import ctypes
from tkinter import *
import tkinter.ttk as ttk
from tkinter import messagebox

# repo: https://github.com/EraPython/AI-virtual-mouse
# With 💗 from Arnav and Arjun


def create():
    smoothening = 3
    pyautogui.FAILSAFE = False
    scrh, scrw = ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1)

    plocx, plocy = 0, 0
    clocx, clocy = 0, 0

    print(f'height: {scrh}, width: {scrw}')
    # 1920, 1080

    wcam, hcam = 640, 480
    frameR = 100

    cap = cv2.VideoCapture(0)
    cap.set(3, wcam)
    cap.set(4, hcam)
    ptime = 0

    detector = htm.HandDetector(maxHands=1)

    while True:
        # TODO-1: Find hand landmarks
        success, img = cap.read()
        img = detector.findHands(img)
        lmlist, bbox = detector.findPosition(img)

        # TODO-2: Get the tip of the index and middle fingers
        if len(lmlist) != 0:
            # Index finger
            x1, y1 = lmlist[8][1:]
            # Middle fingers
            x2, y2 = lmlist[12][1:]

        # TODO-3: Check which fingers are up
            # Returns a 5-element boolean list where 1 stands for True and 0 for False
            fingers = detector.fingersUp()
            # print(fingers)

            cv2.rectangle(img, (frameR, frameR), (wcam - frameR, hcam - frameR), (255, 0, 255), 2)

        # TODO-4: Only index finger (moving mode)
            if fingers[1] == 1 and fingers[2] == 0:

                # TODO-5: convert coordinates
                x3 = np.interp(x1, (frameR, wcam - frameR), (0, ctypes.windll.user32.GetSystemMetrics(1)))
                y3 = np.interp(y1, (frameR, hcam - frameR), (0, ctypes.windll.user32.GetSystemMetrics(0)))

                # TODO-6: Smoothen values
                clocx = plocx + (x3 - plocx) / smoothening
                clocy = plocy + (y3 - plocy) / smoothening

                # TODO-7: Move cursor
                pyautogui.moveTo(scrw-clocx, clocy)
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                plocx, plocy = clocx, clocy

            # TODO-8: Both index and middle fingers are up - clicking mode
            if fingers[0] == 1 and fingers[4] == 1:
                length, img, _ = detector.findDistance(12, 16, img)
                if length < 58:
                    cv2.circle(img, (_[4], _[5]), 15, (0, 255, 0), cv2.FILLED)
                    pyautogui.rightClick()

            if fingers[2] == 1 and fingers[3] == 1:
                length, img, _ = detector.findDistance(12, 16, img)
                if length < 58:
                    cv2.circle(img, (_[4], _[5]), 15, (0, 255, 0), cv2.FILLED)
                    pyautogui.middleClick()

            if fingers[1] == 1 and fingers[2] == 1:
                # TODO-9: Find distance between fingers
                length, img, _ = detector.findDistance(8, 12, img)
                # TODO-10: Click if distance is short
                if length < 58:
                    cv2.circle(img, (_[4], _[5]), 15, (0, 255, 0), cv2.FILLED)
                    pyautogui.click()

        # TODO-11: Frame rate
        ctime = time.time()
        fps = 1 / (ctime - ptime)
        ptime = ctime
        cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

        # TODO-12: Display
        cv2.imshow('AI Virtual Mouse', img)
        (cv2.waitKey(1))


def runner():
    main = Tk()
    main.geometry('500x100')
    main.resizable(False, False)
    main.title('Restricted Access')

    def auth():
        main.destroy()
        root = Tk()
        root.title('Authorisation')
        root.config(padx=110, pady=100)
        root.geometry('600x300')
        root.resizable(False, False)

        username_lbl = Label(root, text='Enter your Username: ')
        username_lbl.grid(row=0, column=0)

        username_ent = ttk.Entry(root, width=30)
        username_ent.grid(row=0, column=1)
        username_ent.focus()

        password_lbl = Label(root, text='Enter your Password: ')
        password_lbl.grid(row=1, column=0)

        password_ent = ttk.Entry(root, width=30, show='*')
        password_ent.grid(row=1, column=1)

        def verification():
            if username_ent.get() == 'dummyUser' and password_ent.get() == 'betatester':
                messagebox.showinfo(title='Authorised Successfully', message="Please wait till the Engine initialises"
                                                                             " itself."
                                                                             "\nStill in Beta testing. You will have"
                                                                             " to manually terminate the program via "
                                                                             "the task manager (ctrl+shift+esc).")
                root.destroy()
                create()
            else:
                isok = messagebox.askokcancel(title='Failure', message='Wrong Username or Password.'
                                                                       '\nDo you want to retry?')
                if not isok:
                    root.destroy()

        auth_button = ttk.Button(root, text='Verify', command=verification)
        auth_button.grid(row=2, column=0, columnspan=2, sticky='we')

        root.mainloop()

    rootLabel = ttk.Label(main, text='Unauthorised Access. Do you wish to override the authorities?')
    rootLabel.pack(side=TOP)

    rootButton = ttk.Button(main, text='Override', command=auth)
    rootButton.pack(side=BOTTOM)

    main.mainloop()


if __name__ == '__main__':
    runner()
