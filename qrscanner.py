import time
import cv2
import json
import os
from datetime import datetime

# Create folder if it doesn't exist
os.makedirs("qr_codes", exist_ok=True)

cap = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()
with open("warehouse.json", "r") as file:
    warehouse = json.load(file)   #json file --> python dict
if not os.path.exists("logs.json"):
    with open("logs.json", "w") as file:
        json.dump([], file)

scanned_data = set()
current_shelf = None  #starts empty until qr is scanned

while True:
    ret, frame = cap.read()
    if not ret:
        break

    data, bbox, _ = detector.detectAndDecode(frame)

    if data:

        if data not in scanned_data:    #problematic in future if we want to scan same item multiple times, but for now it works as a proof of concept  instead of duplicate detection we should think scan history

            filename = f"qr_codes/qr_{int(time.time())}.png"
            print("New QR detected:", data)

            try: 
                qr_type, qr_value = data.split(":")

                qr_type = qr_type.strip()
                qr_value = qr_value.strip()
            except ValueError:
                print("Invalid QR format. Expected 'TYPE:value'.")
                continue
            if qr_type == "SHELF":
                current_shelf = qr_value
                print(f"Shelf set to: {current_shelf}")
            
            elif qr_type == "ITEM":
                if current_shelf is None:
                    print("no shelf selected yet. scan a shelf qr first.")
                else:
                    print(f"item detected: {qr_value} on shelf {current_shelf}")

                    expected_item = warehouse.get(current_shelf)

                    if qr_value in expected_item:
                        status = "correct"
                        print("item is in the correct shelf.")
                    
                    else:
                        status = "misplaced"
                        print("item misplaced.")

                        found_shelf = None

                        for shelf, items in warehouse.items():
                            if qr_value in items:
                                found_shelf = shelf
                                break
                        if found_shelf:
                            print(f"item belongs to shelf {found_shelf}.")
                        else:
                            print("item not found in warehouse data.")
            else:
                print("Unknown QR type. Expected 'SHELF' or 'ITEM'.")

        log_entry = {
            "item": qr_value,
            "shelf": current_shelf,
            "status": status,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        with open("logs.json", "r") as file:   #load old loags
            logs = json.load(file)
        logs.append(log_entry)

        with open("logs.json", "w") as file:   #write back with new log
            json.dump(logs, file, indent=4) 
        print("log updated.")

            # Save image
            # cv2.imwrite(filename, frame)
    else:
        print("unknown qr type use SHELF: shelfname or ITEM: itemname")
        scanned_data.add(data)

        # else:
        #     print("Duplicate ignored:", data)

    cv2.imshow("QR Code Scanner", frame)

    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()