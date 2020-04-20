from PIL import Image
import sys
filename = sys.argv[1]
im = Image.open(filename, "r")
pix_val = list(im.getdata())
print(pix_val)
