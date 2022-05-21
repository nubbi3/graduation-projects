from flask import Flask
import RPi.GPIO as GPIO
import gpiod
import time
import subprocess

def button(secs, line):
    with gpiod.Chip("gpiochip0") as chip:
        line = chip.get_line(line)
        line.request(consumer="powerd", type=gpiod.LINE_REQ_DIR_OUT)
        line.set_value(1)
        time.sleep(secs)
        line.set_value(0)

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/poweron1")
def poweron1():
    button(1, 15)
    return "<p>Power on machine-1!</p>"

@app.route("/poweroff1")
def poweroff1():
    button(4, 15)
    return "<p>Power off machine-1!</p>"""

@app.route("/reboot1")
def reboot1():
    button(4, 15)
    time.sleep(1)
    button(1, 15)
    return "Rebooted machine-1!"

@app.route("/poweron2")
def poweron2():
    button(1, 14)
    return "<p>Power on machine-2!</p>"

@app.route("/poweroff2")
def poweroff2():
    button(4, 14)
    return "<p>Power off machine-2!</p>"""

@app.route("/reboot2")
def reboot2():
    button(4, 14)
    time.sleep(1)
    button(1, 14)
    return "Rebooted machine-2!"

@app.route("/poweron3")
def poweron3():
    button(1, 18)
    return "<p>Power on machine-3!</p>"

@app.route("/poweroff3")
def poweroff3():
    button(4, 18)
    return "<p>Power off machine-3!</p>"""

@app.route("/reboot3")
def reboot3():
    button(4, 18)
    time.sleep(1)
    button(1, 18)
    return "Rebooted machine-3!"

if __name__ == '__main__':
    subprocess.check_output(["sudo systemctl restart docker"], shell=True)
    button(0, 14)
    button(0, 15)
    button(0, 18)
    app.run(host='0.0.0.0', port=8182)
