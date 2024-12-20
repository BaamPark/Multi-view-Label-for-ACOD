from ultralytics import YOLO
import cv2

def run_yolo(source):
    model = YOLO("yolov8s-world.pt")
    model.set_classes(["person"])
    results = model.predict(source)
    # results = model(source)
    frame = results[0].orig_img
    bbox_list = []

    clsnum_to_name = {0:'person'}#{0:'ga', 1:'gi', 2:'h', 3:'rc', 4: 'ma', 5:'mi', 6:'nc'}
    for result in results:
        for box in result.boxes:
            print("person", box.xyxy[0].tolist())
            bbox = [int(x) for x in box.xyxy[0].tolist()]
            x1, y1, x2, y2 = bbox
            top_left = (x1, y1)
            bottom_right = (x2, y2)

            # cv2.rectangle(frame, top_left, bottom_right, color=(0, 255, 0), thickness=2)
                
                #for mot format
            bb_left = x1
            bb_top = y1
            bb_width = x2 - x1
            bb_height = y2 - y1

            bbox_list.append([bb_left, bb_top, bb_width, bb_height, clsnum_to_name[int(box.cls.item())]])

    return frame, bbox_list

    # cv2.imshow('Image', frame)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

#source="videos/input segments/1.23 Simulation trimed.mp4" classes=0 save=True

# run_yolo("samples/2.24.23 sim without bed-trauma 1 above bed_above_17.png")