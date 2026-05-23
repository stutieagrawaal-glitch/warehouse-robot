#these are the fake qr codes i am going to use for testing
import qrcode
import os

# Create folder if it doesn't exist
os.makedirs("qrcodes", exist_ok=True)

data = "SHELF: A1"
img = qrcode.make(data)
img.save("testing\shelf_a1.png")

data = "SHELF: B1"
img = qrcode.make(data)
img.save("testing\shelf_b1.png")

data2 = "ITEM: item101"
img2 = qrcode.make(data2)
img2.save("testing\item101.png")

data = "ITEM: item102"
img = qrcode.make(data)
img.save("testing\item102.png")

data = "ITEM: item202"
img = qrcode.make(data)
img.save("testing\item202.png")