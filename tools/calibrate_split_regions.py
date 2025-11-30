# tools/calibrate_split_regions.py
"""
Interactive tool to find home and away score regions
"""

import cv2


def mouse_callback(event, x, y, flags, param):
    """Handle mouse events"""
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Click at: x={x}, y={y}")


def calibrate_regions(video_path):
    """Interactively find score regions"""

    # Load first frame
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Could not read video")
        return

    print("\nInstructions:")
    print("1. Click top-left of HOME score")
    print("2. Click bottom-right of HOME score")
    print("3. Click top-left of AWAY score")
    print("4. Click bottom-right of AWAY score")
    print("\nPress 'q' to quit")

    cv2.namedWindow('Calibrate')
    cv2.setMouseCallback('Calibrate', mouse_callback)

    while True:
        cv2.imshow('Calibrate', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    calibrate_regions("../data/entire_rotation.jpg")