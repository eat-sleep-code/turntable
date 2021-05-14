import board
import time
from digitalio import DigitalInOut, Direction
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

rgbDisplay = st7789.ST7789(
	spi=board.SPI(),
	cs=DigitalInOut(board.CE0),
	dc=DigitalInOut(board.D25),
	rst=None,
	baudrate=64000000,
	width=240,
	height=240,
	x_offset=10,
	y_offset=10
) 
width = int(rgbDisplay.width)
height = int(rgbDisplay.height)
rotation = 0
rgbImage = Image.new('RGB', (width, height))
draw = ImageDraw.Draw(rgbImage)
fontSize = 24
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', fontSize)


class Backlight:
	
	def on():
		print('DEBUG: Backlight ON...')
		backlight = DigitalInOut(board.D26)
		backlight.switch_to_output()
		backlight.value = True


	def off():
		print('DEBUG: Backlight OFF...')
		backlight = DigitalInOut(board.D26)
		backlight.switch_to_output()
		backlight.value = False


#// ===========================================================================


class Text:

	def clear():
		print('DEBUG: Clearing...')
		global rgbDisplay
		global rgbImage
		global draw
		global width
		global height
		global rotation
		draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
		rgbDisplay.image(rgbImage, rotation)


	def write(x = 0, y = 0, inputLines = [], textColor='#FFFFFF'):
		global rgbDisplay
		global rgbImage
		global draw
		global font

		Backlight.on()
		Text.clear()
		
		for line in inputLines:
			print('DEBUG: Writing... ' + str(line))
			draw.text((x, y), str(line), font=font, fill=textColor)
			y += font.getsize(str(line))[1]

		rgbDisplay.image(rgbImage, rotation)
		time.sleep(0.1)

