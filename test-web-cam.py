import cv2

cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("❌ Cannot access the webcam.")
else:
    ret, frame = cam.read()
    if ret:
        print("✅ Frame captured successfully.")
        cv2.imshow("Test", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print("❌ Failed to capture a frame.")

cam.release()
