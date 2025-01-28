import requests
import xml.etree.ElementTree as ET
import adafruit_display_text.label
import board
import displayio
import framebufferio
import rgbmatrix
import terminalio
import time

def fetch_and_sort_predictions(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch data: {response.status_code}")
        return None

    root = ET.fromstring(response.text)
    all_predictions = []

    for predictions in root.findall('predictions'):
        route_title = predictions.get('routeTitle')
        for direction in predictions.findall('direction'):
            for prediction in direction.findall('prediction'):
                minutes = int(prediction.get('minutes'))
                all_predictions.append({'route': route_title, 'minutes': minutes})

    all_predictions.sort(key=lambda x: x['minutes'])
    result = [{'route': pred['route'].split('-')[0], 'minutes': pred['minutes']} for pred in all_predictions[:3]]
    return result

def get_color(minutes):
    if minutes < 5:
        return 0xFF0000
    elif 5 <= minutes < 7:
        return 0x00FF00
    else:
        return 0xFFFF00
# use this to find your stop id https://www.ttc.ca/routes-and-schedules
url = "https://retro.umoiq.com/service/publicXMLFeed?command=predictions&a=ttc&stopId=2251"

matrix = rgbmatrix.RGBMatrix(
    width=64, height=32, bit_depth=1,
    rgb_pins=[board.D6, board.D5, board.D9, board.D11, board.D10, board.D12],
    addr_pins=[board.A5, board.A4, board.A3, board.A2],
    clock_pin=board.D13, latch_pin=board.D0, output_enable_pin=board.D1)

display = framebufferio.FramebufferDisplay(matrix, auto_refresh=False)
font = terminalio.FONT

while True:
    data = fetch_and_sort_predictions(url)
    g = displayio.Group()
    print(data)

    for i, item in enumerate(data[:3]):
        route_text = f"{item['route']}: {'now' if item['minutes'] == 0 else f'{item['minutes']} min'}"
        color = get_color(item['minutes'])

        label = adafruit_display_text.label.Label(
            font,
            color=color,
            text=route_text
        )
        label.x = 5
        label.y = i * 10 + 5
        g.append(label)

    display.root_group = g
    display.refresh()

    for seconds_left in range(20, 0, -1):
        time.sleep(1)

    print("\nRefreshing now...")
