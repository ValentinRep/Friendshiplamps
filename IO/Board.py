import datetime
##Zu testzwecken nur mit Konsolen ausgaben und "zufallswerten"
class Board:

    def __init__(self):
        self.isEnabled = False;

    def enableLamp(self):
        self.isEnabled = True
        print("Lampe wird aktiviert")


    def disableLamp(self):
        self.isEnabled = False
        print("Lampe wird deaktiviert")


    def buttonPressed(self):
        time = round(datetime.datetime.now().timestamp())
        if (time % 5) == 0:
            return True
        return False
