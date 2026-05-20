import time
import cv2
import json
import os

# Create folder if it doesn't exist
os.makedirs("qr_codes", exist_ok=True)

cap = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()
with open("warehouse.json", "r") as file:
    warehouse = json.load(file)   #json file --> python dict

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
                print("Invalid QR format. Expected 'type:value'.")
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
                        print("item is in the correct shelf.")
                    
                    else:
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

            # Save image
            # cv2.imwrite(filename, frame)
            # scanned_data.add(data)

        else:
            print("Duplicate ignored:", data)

    cv2.imshow("QR Code Scanner", frame)

    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()