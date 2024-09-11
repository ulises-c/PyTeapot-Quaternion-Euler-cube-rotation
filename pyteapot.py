"""
PyTeapot module for drawing rotating cube using OpenGL as per
quaternion or yaw, pitch, roll angles received over serial port.
"""

import pygame
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *


def main():
    video_flags = OPENGL | DOUBLEBUF
    pygame.init()
    screen = pygame.display.set_mode((640, 480), video_flags)
    pygame.display.set_caption("PyTeapot IMU orientation visualization")
    resizewin(640, 480)
    init()
    frames = 0
    ticks = pygame.time.get_ticks()
    while 1:
        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            break
        if(useQuat):
            [w, nx, ny, nz] = read_data()
            draw(w, nx, ny, nz)
        elif(useEuler):
            [yaw, pitch, roll] = read_data()
            draw(1, yaw, pitch, roll)     
        pygame.display.flip()
        frames += 1
    print("fps: %d" % ((frames*1000)/(pygame.time.get_ticks()-ticks)))
    if(useSerial):
        ser.close()


def resizewin(width, height):
    """
    For resizing window
    """
    if height == 0:
        height = 1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0*width/height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def init():
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)


def cleanSerialBegin():
    if(useQuat):
        try:
            line = ser.readline().decode('UTF-8').replace('\n', '')
            w = float(line.split('w')[1])
            nx = float(line.split('a')[1])
            ny = float(line.split('b')[1])
            nz = float(line.split('c')[1])
        except Exception:
            pass
    elif(useEuler):
        try:
            line = ser.readline().decode('UTF-8').replace('\n', '')
            yaw = float(line.split('y')[1])
            pitch = float(line.split('p')[1])
            roll = float(line.split('r')[1])
        except Exception:
            pass


def find_headers(csv_file):
    # Function to find headers containing the substrings based on the mode
    print(f"CSV file: `{csv_file}` | Mode: {"Quat" if useQuat else "Euler"}")
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames

    if(useQuat):
        substrings = ["Quat_W", "Quat_X", "Quat_Y", "Quat_Z"]
    elif(useEuler):
        substrings = ["Yaw", "Pitch", "Roll"]
    else:
        return []

    found_headers = []
    for substring in substrings:
        for header in headers:
            if substring in header:
                found_headers.append(header)
                break
    return found_headers

def readCSV():
    try:
        with open(csv_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            last_row = None
            for row in csv_reader:
                last_row = row

            if last_row is None:
                raise ValueError("CSV file is empty")

            if(useQuat):
                w = last_row.get(headers[0]) if len(headers) > 0 else None
                x = last_row.get(headers[1]) if len(headers) > 1 else None
                y = last_row.get(headers[2]) if len(headers) > 2 else None
                z = last_row.get(headers[3]) if len(headers) > 3 else None
                # print(f"W:{w} | X(A):{x} | Y(B):{y} | Z(C):{z}")
                # print(last_row)
                # BUG: Currently getting math domain errors when converting Quaternion to Euler Angles
                if None in [w, x, y, z]:
                    raise ValueError("Required quaternion data not found in CSV")
                return f"w{w}wa{x}ab{y}bc{z}c"  # format for quaternion

            elif(useEuler):
                yaw = last_row.get(headers[0]) if len(headers) > 0 else None
                pitch = last_row.get(headers[1]) if len(headers) > 1 else None
                roll = last_row.get(headers[2]) if len(headers) > 2 else None
                if None in [yaw, pitch, roll]:
                    raise ValueError("Required Euler data not found in CSV")
                return f"y{yaw}yp{pitch}pr{roll}r"  # format for Euler

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def read_data():
    if(useSerial):
        ser.reset_input_buffer()
        cleanSerialBegin()
        line = ser.readline().decode('UTF-8').replace('\n', '')
    elif(useWifi):
        # Waiting for data from udp port 5005
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        line = data.decode('UTF-8').replace('\n', '')
    elif(useCSV):
        line = readCSV()
    print(line)

    """ String formats
    - Both quaternions and Euler angles
    w0.09wa-0.12ab-0.09bc0.98cy168.8099yp12.7914pr-11.8401r
    - Quaternions only
    w0.09wa-0.12ab-0.09bc0.98c
    - Euler angles only
    y168.8099yp12.7914pr-11.8401r
    """
    if(useQuat):
        w = float(line.split('w')[1])
        nx = float(line.split('a')[1])
        ny = float(line.split('b')[1])
        nz = float(line.split('c')[1])
        return [w, nx, ny, nz]
    elif(useEuler):
        yaw = float(line.split('y')[1])
        pitch = float(line.split('p')[1])
        roll = float(line.split('r')[1])
        return [yaw, pitch, roll]


def draw(w, nx, ny, nz):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0.0, -7.0)

    drawText((-2.6, 1.8, 2), "PyTeapot", 18)
    drawText((-2.6, 1.6, 2), "Module to visualize quaternion or Euler angles data", 16)
    drawText((-2.6, -2, 2), "Press Escape to exit.", 16)

    if(useQuat):
        [yaw, pitch , roll] = quat_to_ypr([w, nx, ny, nz])
        drawText((-2.6, -1.8, 2), "Yaw: %f, Pitch: %f, Roll: %f" %(yaw, pitch, roll), 16)
        glRotatef(2 * math.acos(w) * 180.00/math.pi, -1 * nx, nz, ny)
    elif(useEuler):
        yaw = nx
        pitch = ny
        roll = nz
        drawText((-2.6, -1.8, 2), "Yaw: %f, Pitch: %f, Roll: %f" %(yaw, pitch, roll), 16)
        glRotatef(-roll, 0.00, 0.00, 1.00)
        glRotatef(pitch, 1.00, 0.00, 0.00)
        glRotatef(yaw, 0.00, 1.00, 0.00)

    glBegin(GL_QUADS)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(1.0, 0.2, -1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(1.0, 0.2, 1.0)

    glColor3f(1.0, 0.5, 0.0)
    glVertex3f(1.0, -0.2, 1.0)
    glVertex3f(-1.0, -0.2, 1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(1.0, -0.2, -1.0)

    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, -0.2, 1.0)
    glVertex3f(1.0, -0.2, 1.0)

    glColor3f(1.0, 1.0, 0.0)
    glVertex3f(1.0, -0.2, -1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(1.0, 0.2, -1.0)

    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(-1.0, -0.2, 1.0)

    glColor3f(1.0, 0.0, 1.0)
    glVertex3f(1.0, 0.2, -1.0)
    glVertex3f(1.0, 0.2, 1.0)
    glVertex3f(1.0, -0.2, 1.0)
    glVertex3f(1.0, -0.2, -1.0)
    glEnd()


def drawText(position, textString, size):
    font = pygame.font.SysFont("Courier", size, True)
    textSurface = font.render(textString, True, (255, 255, 255, 255), (0, 0, 0, 255))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glRasterPos3d(*position)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

def quat_to_ypr(q):
    yaw   = math.atan2(2.0 * (q[1] * q[2] + q[0] * q[3]), q[0] * q[0] + q[1] * q[1] - q[2] * q[2] - q[3] * q[3])
    pitch = -math.asin(2.0 * (q[1] * q[3] - q[0] * q[2]))
    roll  = math.atan2(2.0 * (q[0] * q[1] + q[2] * q[3]), q[0] * q[0] - q[1] * q[1] - q[2] * q[2] + q[3] * q[3])
    pitch *= 180.0 / math.pi
    yaw   *= 180.0 / math.pi
    yaw   -= -9.58  # Declination at Santa Clara, California, USA is - 9 degress 58 min
    roll  *= 180.0 / math.pi
    return [yaw, pitch, roll]


# Data transmission
useSerial = False  # set true for using serial for data transmission
useWifi = False    # set true for reading via wifi for data transmission
useCSV = True      # set true for reading a CSV file for data transmission

# Data format
useQuat = True     # set true for using quaternions (w, x, y, z)
useEuler = False   # set true for using Euler angles (yaw, pitch, roll)

if(useSerial):
    import serial
    ser = serial.Serial('/dev/ttyUSB0', 38400)
elif(useWifi):
    import socket
    UDP_IP = "0.0.0.0"
    UDP_PORT = 5005
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
elif(useCSV):
    import csv
    csv_file = "test_data.csv"
    headers = find_headers(csv_file)
    pass
else:
    print("\nError, data transmission type missing.\nSelect the data transmission type [serial, csv, wifi].\nExiting program.")
    quit()


if __name__ == '__main__':
    main()
