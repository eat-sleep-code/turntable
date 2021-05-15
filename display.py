import board
import time
from digitalio import DigitalInOut, Direction
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

rgbDisplay = st7789.ST7789(
	spi=board.SPI(),
	height=240,
	width=240,
	y_offset=80,
	rotation=180,
	cs=DigitalInOut(board.CE0),
	dc=DigitalInOut(board.D25),
	rst=DigitalInOut(board.D24),
	baudrate=24000000,
) 
width = int(rgbDisplay.width)
height = int(rgbDisplay.height)
rotation = 180
rgbImage = Image.new('RGB', (width, height))
draw = ImageDraw.Draw(rgbImage)
fontSize = 24
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', fontSize)


class Backlight:
	
	def on():
		backlight = DigitalInOut(board.D26)
		backlight.switch_to_output()
		backlight.value = True


	def off():
		backlight = DigitalInOut(board.D26)
		backlight.switch_to_output()
		backlight.value = False


#// ===========================================================================


class Text:

	def clear():
		global rgbDisplay
		global rgbImage
		global draw
		global width
		global height
		global rotation
		draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
		rgbDisplay.image(rgbImage, rotation)


	def write(inputLines = [], x = 0, y = 0, textColor='#FFFFFF'):
		global rgbDisplay
		global rgbImage
		global draw
		global font
		global rotation

		time.sleep(0.1)
		Text.clear()
		
		for line in inputLines:
			draw.text((x, y), str(line), font=font, fill=textColor)
			y += font.getsize(str(line))[1]

		rgbDisplay.image(rgbImage, rotation)

