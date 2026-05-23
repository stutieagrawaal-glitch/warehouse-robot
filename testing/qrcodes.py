#these are the fake qr codes i am going to use for testing
import qrcode
import os

# Create folder if it doesn't exist
os.makedirs("qrcodes", exist_ok=True)
type = input("what type of qr code do you want to generate? (SHELF or ITEM): ").upper()
n = int(input("how many qr codes do you want to generate? "))
while True:
    for i in range(n):
        if type == "SHELF":
            row = chr(65 + i) #A, B, C, D, E
            col = (i % 10) + 1 #1, 2, 3, 4, 5
            data = f"SHELF: {row}{col}"
        elif type == "ITEM":
            data = f"ITEM: Item_{101+ i}"
        else:
            print("Invalid type. Please choose 'SHELF' or 'ITEM'.")
            break
        img = qrcode.make(data)
        img.save(f"qrcodes/{type}_{i+1}.png")
        print(f"Generated QR code: {data} saved as qrcodes/{type}_{i+1}.png")
    cont = input("Do you want to generate more QR codes? (yes/no): ").lower()
    if cont != "yes":
        break