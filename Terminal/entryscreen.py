from servercall import serverFunction,vehRecord

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP) #11 pin number of rpi
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP) #13 pin number of rpi
import time
import json

jsonLocation = '/home/pi/Rustmjee Terminal Codes/data.json'


class entryHome():
    def __init__(self, **kwargs):
        super(entryHome, self).__init__(**kwargs)
        while True:
            with open(jsonLocation, 'r') as f:
                self.data = json.load(f)
            
            self.start_api = serverFunction()
            
            user_auth = {
                "strategy": "local",
                "loginId":str(self.data["userData"]["loginId"]),
                "password":str(self.data["userData"]["password"])
            }
            try:
                auth_response = self.start_api.login_api(user_auth)
            except:
                auth_response = {}
                print("entryserver down")

            if "authentication" in auth_response:
                self.data["userData"]["loginId"] = auth_response["user"]["loginId"]
                self.data["userData"]["userFirstName"] = auth_response["user"]["userFirstName"]
                self.data["accessToken"] = auth_response["accessToken"]

                with open(jsonLocation, "w+") as f:
                    json.dump(self.data, f, indent=4)

            with open(jsonLocation, 'r') as f:
                self.data = json.load(f)
            self.api_token_jwt = self.data["accessToken"]
        
            # print("WAITING for input")
            button_4w = GPIO.input(17)
            button_2w = GPIO.input(27)
            try:
                if button_4w == False:
                    self.veh_selected("4W")
                    print("4w pushed")
                if button_2w == False:
                    self.veh_selected("2W")
                    print("2w pushed!")
            except:
                print("pressed")

    def veh_selected(self, data):
        print('The button has been pressed :', data)
        enter_record = {
            "vehicleType": data,
            "uhfEpcId": "",
            "uhfTid": "",
            "uhfUserData": "",
            "anprData": "", 
            "rfid": "",
            "numberplate": "",
            "prepaidFare": 0,
            "laneNo" :"1",
            "vehicleImage": ""
        }
        enter_record = vehRecord.veh_enter(self, enter_record)

# if __name__ == '__main__':
#     a=entryHome()