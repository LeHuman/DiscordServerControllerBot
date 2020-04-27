import gpiozero
import asyncio
from threading import Thread
import platform
from gpiozero import PWMOutputDevice as PWM
import subprocess
import time
import os
from dotenv import load_dotenv

load_dotenv()
CPU = os.getenv("SERVER_CPU")
SERVER_RAM = os.getenv("SERVER_RAM")
SERVER_GPU = os.getenv("SERVER_GPU")
SERVER_STORAGE = os.getenv("SERVER_STORAGE")
SERVER_OS = os.getenv("SERVER_OS")
SERVER_LOCAL_IP = os.getenv("SERVER_LOCAL_IP")
SERVER_TIMEOUT_POWER = int(os.getenv("SERVER_TIMEOUT_POWER")) * 60  # Max time to wait after pinging before deeming it unresponsive
SERVER_INTERVAL_CHECK = int(os.getenv("SERVER_INTERVAL_CHECK"))  # Time between pings in seconds
SERVER_WAIT_POWER = int(os.getenv("SERVER_WAIT_POWER")) * 60  # Minimum wait time until we attempt to ping the server
RPI_GPIO_POWER_PIN = int(os.getenv("RPI_GPIO_POWER_PIN"))  # GPIO pin of the RPi that connects to the pc header pin
RPI_GPIO_LENGTH = int(os.getenv("RPI_GPIO_LENGTH"))  # Length of pulse to send
RPI_GPIO_POWER = float(os.getenv("RPI_GPIO_POWER"))  # Power output of the GPIO pin
GPIO_SWITCH = PWM(RPI_GPIO_POWER_PIN)

specString = f"""
CPU:    {CPU}
Ram:    {SERVER_RAM}
Gpu:    {SERVER_GPU}
Stor:   {SERVER_STORAGE}
OS:     {SERVER_OS}"""

commandSent = False  # Whether we have already sent a command and are awaiting a response
monitering = False  # Whether we are already monitering
timeout = False  # Whether our command was unable to be verified
mismatch = False  # Whether our ping and physical connection don't agree TODO
currentState = False  # Expected state of the server True = on False = off


def ping(host=SERVER_LOCAL_IP):
    """
    Returns True if host (str) responds to a ping request.\n
    Default is SERVER_LOCAL_IP
    """

    # Option for the number of packets as a function of
    param = "-n" if platform.system().lower() == "windows" else "-c"

    # Building the command
    command = ["ping", param, "1", host]
    return subprocess.call(command) == 0


def splitThread(name=None):
    """
        Make a function with no arguments run on a seperate thread
    """

    def splitThreadName(func):
        def threaded():
            t = Thread(target=func, daemon=True, name=name)
            t.start()

        return threaded

    return splitThreadName


@splitThread(name="Moniter")
def __monitorState():
    """
        Moniters the server for a change in state indicating
        a command was sucessfully sent
    """
    global commandSent, timeout, monitering, currentState
    if monitering:
        print("We are already monitering")
        return
    if commandSent:
        print("Command was sent, monitering change in state")
        monitering = True
        start = int(time.time())

        time.sleep(SERVER_WAIT_POWER)
        while int(time.time()) - start < SERVER_TIMEOUT_POWER:
            print("Pinging server")
            if ping() != currentState:
                print("State has changed, modifying current values")
                commandSent = False
                currentState = not currentState
                monitering = False
                timeout = False
                return
            time.sleep(SERVER_INTERVAL_CHECK)
        print("Monitering has timed out, undoing command")
        monitering = False
        commandSent = False
        timeout = True
    else:
        print("No command was sent, we will not monitor")


@splitThread(name="TurnOn")
def _turnOn():
    print("Turning On!")
    __monitorState()
    GPIO_SWITCH.blink(RPI_GPIO_LENGTH, 0, 0, 0, 1, False)
    print("Done sending on command")


@splitThread(name="TurnOff")
def _turnOff():
    print("Turning Off!")
    __monitorState()
    GPIO_SWITCH.blink(RPI_GPIO_LENGTH, 0, 0, 0, 1, False)
    print("Done sending off command")


async def sendCommand(cmd):
    """
    Returns True if command sent (str on | off) was passed to the server
    """
    global commandSent
    cmd = str(cmd).lower()
    if not commandSent:
        if cmd == "on":
            commandSent = True
            _turnOn()
            print("Returning to caller")
            return True
        elif cmd == "off":
            commandSent = True
            _turnOff()
            print("Returning to caller")
            return True
        else:
            print("Invalid command")
    else:
        print("Server is in a mid-state and cannot be sent another command")
    print("Returning to caller")
    return False


async def status():
    """
        Returns a list containing all the global vars including a
        formatted str of these vars
    """
    currState = "on" if currentState else "off"
    nextState = "on" if not currentState else "off"
    awaiting = f"\nAwaiting response from server to turn {nextState}" if commandSent else "\nNo command has been sent"
    timedout = "\nlast command sent failed to get a response" if timeout else ""
    network = "\nThere may be a network issue" if mismatch else f"\nNo network issue detected"
    return {
        "string": f"Server is detected as {currState}{awaiting}{timedout}{network}",
        "commandSent": commandSent,
        "currentState": currentState,
        "timeout": timeout,
        "monitering": monitering,
        "mismatch": mismatch,
    }


async def canSend():
    """
        Returns True if a command can be sent
    """
    return not commandSent


async def getSpecs():
    """
        Returns a str listing the specs of the server
    """
    return specString


async def main():
    stat = await status()
    print(stat["string"])
    time.sleep(2)
    if await canSend():
        await sendCommand("on")
    stat = await status()
    print(stat["string"])
    if await canSend():
        await sendCommand("off")
    time.sleep(8)
    stat = await status()
    print(stat["string"])
    while monitering:
        _ = 1


asyncio.run(main())
