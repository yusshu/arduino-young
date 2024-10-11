# Copyright (c) Andre Roldan
# Licensed under the MIT license
import serial, math


#
# Function that communicates with the source through serial
# data. Sends a 't' number of signals we want to take and waits
# for the source to take them, then reads them from the serial
# port and returns the average.
#
def read_distance(src, t = 1):
    # Send number of signals we want to get
    src.write((str(t) + '\n').encode())
    src.flush()

    # Wait for the signals and take the average
    signals = []
    while t > 0:
        signals.append(int(src.readline()))
        t -= 1
    return int(sum(signals) / len(signals))


#
# Function that takes a table (dictionary) where the keys are the
# 'x' values and the values are the 'y' values, both must be numbers,
# and returns the slope and intercept (in that order, as a tuple),
# for the line with least squared errors
#
def least_squares(table):
    n = len(table)
    sxy = 0
    sx = 0
    sx2 = 0
    sy = 0
    for x, y in table.items():
        sxy += (x * y)
        sx += x
        sx2 += (x**2)
        sy += y
    a = ((n*sx2) - sx**2)
    b = ((sy*sx2) - (sx*sxy)) / a    # intercept
    m = ((n*sxy) - (sx*sy)) / a      # slope
    return (m, b)

def main():
    # Connect with the Arduino
    arduino = serial.Serial('COM4', 9600)

    # We define the weights we can use (in kilograms)
    # and the dimensions of the object we're using (in
    # meters)
    weight_to_deformation = dict()
    weights = [ 0.01, 0.06, 0.07, 0.12, 0.13, 0.18, 0.19 ]
    b = 0.0282
    h = 0.001
    L = 0.282
    g = 9.81 # the earth gravity acceleration

    # areal moment of inertia with respect to the horizontal axis of the element (in meters^4)
    J = (b * (h**3)) / (12)


    # Ask for how many weights are we going to use
    weight_count = int(input('Masas: '))

    # Determine the initial distance from the object to the
    # sensor so we check the differences later and convert the
    # distance from milimeters to meters
    initial = read_distance(arduino, 4) / 1000

    # Loop through the wanted weights and wait for the operator to
    # put them over the object to check the deformation
    for i in range(weight_count):
        weight = weights[i]
        input(f'\n** {i+1}. Coloque una masa total de {weight}kg y luego presione Enter para continuar **\n')
        weight_to_deformation[weight] = (read_distance(arduino, 50) / 1000) - initial

    arduino.close()

    # Compute the Young's Modulus
    B, A = least_squares(weight_to_deformation)
    Y = ((L**3) * g) / (3*J*B)
    print(f'\nEl Módulo de Young calculado es: {Y:.2e}')

    # Compute the variance
    sx = 0
    for x, y in weight_to_deformation.items():
        sx = sx + x

    n = len(weight_to_deformation)
    avg_x = sx / n
    sxx = 0
    syy = 0

    for x, y in weight_to_deformation.items():
        sxx += (x - avg_x)**2
        syy += (y - B*x - A)**2

    delta_b = math.sqrt((syy)/((n-2)*(n*sxx)))
    error_b = (delta_b / B) * 100
    print(f'(con un error del {error_b:.3}%)\n')


if __name__ == "__main__":
    main()
