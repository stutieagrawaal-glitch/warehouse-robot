import time
import cv2
import json
import os
from datetime import datetime

# Create folder if it doesn't exist
os.makedirs("qr_codes", exist_ok=True)

cap = cv2.VideoCapture(0)
detector = cv2.QRCodeDetector()
scanned_data = set()
current_shelf = None  #starts empty until qr is scanned
status = None

with open("warehouse.json", "r") as file:
    warehouse = json.load(file)   #json file --> python dict

if not os.path.exists("inventory.json"):
    with open("inventory.json", "w") as file:
        json.dump({}, file)   #empty dict for inventory

if not os.path.exists("logs.json"):
    with open("logs.json", "w") as file:
        json.dump([], file)

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

                    expected_item = warehouse.get(current_shelf, [])

                    found_shelf = None    #contains where item should belong
                    for shelf, items in warehouse.items():
                        if qr_value in items:
                            found_shelf = shelf
                            break

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

                    with open("inventory.json", "r") as file:
                        inventory = json.load(file)   #load inventory data
    
                        inventory[qr_value] = {
                            "current_shelf": current_shelf,
                            "status": status,
                            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }

                    with open ("inventory.json", "w") as file:
                        json.dump(inventory, file, indent=4)   #write back inventory data
                    print("inventory updated.")

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
        time.sleep(2)

            # Save image
            # cv2.imwrite(filename, frame)


        # else:
        #     print("Duplicate ignored:", data)

    cv2.imshow("QR Code Scanner", frame)

    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

with open("inventory.json", "r") as file:
    inventory = json.load(file)

missing_items = []

for shelf, items in warehouse.items():
    for item in items:
        if item not in inventory or inventory[item]["status"] != "correct":
            missing_items.append({
                "item": item,
                "expected_shelf": shelf,
                "status": inventory.get(item, {}).get("status", "missing")
            })
print("\nMissing/Misplaced Items:")
for item in missing_items:
    print(f"Item: {item['item']}, Expected Shelf: {item['expected_shelf']}, Status: {item['status']}")