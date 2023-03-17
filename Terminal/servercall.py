import json
import time
import requests
import serial
import RPi.GPIO as GPIO

import base64
import io
from PIL import Image
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(24,GPIO.OUT)
GPIO.output(24,GPIO.HIGH)

import printer

serverip = "http://" + 'onprem-api.caproverinstance.local' + ":3030"
print("hi server",serverip)

class serverFunction:
    def __init__(self, **kwargs):
        super(serverFunction, self).__init__(**kwargs)
        try:
            self.serverip = serverip
            # print('try found the serverip')
        except:
            print('exception found the serverip')
            self.serverip = serverip

    def login_api(self, data):
        api_endpoint = str(self.serverip) + str("/authentication")
        r = requests.post(url=api_endpoint, data=data, timeout=1)
        response_json = r.json()
        #print("AUTH:%s" % response_json)
        return response_json

    def veh_entry_api(self, api_token, data):
        api_endpoint = str(self.serverip) + str("/entry-parking/")
        hed = {'Authorization': 'Bearer ' + str(api_token)}
        print(api_endpoint)
        r = requests.post(url=api_endpoint, headers=hed, data=data)
        response_json = r.json()
        #  print("veh Entered into server:%s" % response_json)
        return response_json

    def veh_exit_api(self, api_token, querystring):
        api_endpoint = str(self.serverip) + str("/exit-parking")
        hed = {'Authorization': 'Bearer ' + str(api_token)}
        data = ""
        r = requests.get(url=api_endpoint, headers=hed, data=data, params=querystring)
        response_json = r.json()
        # print("veh exit into server:%s" % response_json["parkingRecords"])
        return response_json

class vehRecord:

    def __init__(self, **kwargs):
        super(vehRecord, self).__init__(**kwargs)

    def veh_enter(self, data_json):
        try:
            entry_record = self.start_api.veh_entry_api(self.api_token_jwt, data_json)
            print(entry_record)
            firebaseID = entry_record["parkingRecord"]["vrFirebaseId"]
            date_time_var = int(entry_record["parkingRecord"]["vrParkingStartTimeL"]) / 1000
            ticketdate = time.strftime('%Y-%m-%d', time.localtime(date_time_var))
            tickettime = time.strftime('%H:%M:%S', time.localtime(date_time_var))
            try:
                vrNumberPlate = entry_record["numplateImage"]                
                image = base64.b64decode(vrNumberPlate)
                vrNumberPlate = Image.open(io.BytesIO(image))
                # print(vrNumberPlate.size)
                vrNumberPlate = vrNumberPlate.resize((230,80),Image.ANTIALIAS)   
            except:
                pass
                Image_blank='iVBORw0KGgoAAAANSUhEUgAAAeIAAABHCAYAAADbT0RKAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsIAAA7CARUoSoAAAAEwSURBVHhe7dUxAQAgDMCwgX/PwIGHPslTCV3nGQAgsX8BgIARA0DIiAEgZMQAEDJiAAgZMQCEjBgAQkYMACEjBoCQEQNAyIgBIGTEABAyYgAIGTEAhIwYAEJGDAAhIwaAkBEDQMiIASBkxAAQMmIACBkxAISMGABCRgwAISMGgJARA0DIiAEgZMQAEDJiAAgZMQCEjBgAQkYMACEjBoCQEQNAyIgBIGTEABAyYgAIGTEAhIwYAEJGDAAhIwaAkBEDQMiIASBkxAAQMmIACBkxAISMGABCRgwAISMGgJARA0DIiAEgZMQAEDJiAAgZMQCEjBgAQkYMACEjBoCQEQNAyIgBIGTEABAyYgAIGTEAhIwYAEJGDAAhIwaAkBEDQMiIASBkxAAQMmIACBkxAGRmLpN8BIqdDaLIAAAAAElFTkSuQmCC'
                #Image_not_found='iVBORw0KGgoAAAANSUhEUgAAAeIAAABHCAIAAABULdMdAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAzQSURBVHhe7Z3rYeNGDIRdlwpSParmmnExl31QFB8YvJakmGS+f7F3gcEACzmXxPn5Swgh5MZwTRNCyK3hmiaEkFvDNU0IIbeGa5oQQm4N1zQhhNwarmlCCLk1XNOEEHJruKYJIeTWcE0TQsit4ZomhJBbwzVNCCG3hmuaEEJuDdc0IYTcmv/lmv59PX5+nn+mvzqB398/r9fzUfhZU7/0eD5ff35/p6Mf/jxP1fRfoPr6rL5Odi7pxhZnp7NEg07+q+hrumyIKH2j+C4+XvGOOyVlQrctnbtqUIa/jH4T5qE8h/dj6Jq2azrRF42T+mB+uBgxHLLqUvH7+vN4Sp+DWw52dyJi8hf6e4aT4TK2Qs0A7YIjzUGjmOpL+XR7f77ZbQiy+Wm6NFHr4QN9xP7+qs2PjG5j2qQIqMPD3IOwKo26oKe4H/oeXmYpi1x5J2jK2vqfzgyQLtjK7wu8idK9sS9Ko7XxVfx4LGf04KnHaJIy+Zr+nuZkx5gS+9GWAKt337RN33tjJDl2FK1kGuXtDyypDcIfesDpNT6q1NVqfsytUEOll01jFTqmCiI102qSOACaHuiJcKmMXJn43aM80LkdXivfUXznpZywCrENSsmrQd+/VFTvWnl1epU2bTJ6d6C/7cfitUIt9alOLkBVuG2ZhSoTglrTOXgU7b7I3WhInzQJhDWNPDCNhvu94vWuckwXRDahh2J1JLHemdzeVeUEnvGH1YNzPxWE2mFn9F6zx/iMs4JCeOVzVvxIldJXJOkLm9Mmp/q7ajBMfbaTCyKuyUwRjAvXjWJoDsSz4z9XS/8IEThgGq06FxjfHufx3H+iN/wN37OT6FclIrYlJHAVQb0ZGZcV88XBYgtIw4Sr8tYDv+glngKkKZTvTSdR0KjfRjiTdH/nm3LqC5xckK/izRTBuoASTbjyuUYxWFH53JwOrBjb1Iev6edTvl1wOfdOX8oabvgWMWI+nGxUPN5Hlnp3wI/panqDzCANMw4x1TVLieisU76sURDWkuCgYb/7hbTJIJ8rHk59iZMLwq7tcNqIEs0cNIqJikTPIxbsOH5Nw/Xq1Nmzl6PjDd8AAibjydGcD2DDO5YqZciP5mpO3JKmQfkkLphJqhT9kDyAfvXi/f11Q0jCb7s0BZDPGU9OfZGTC4amtNEjmBqvGcVCpiLZ94AJG05Y0zCAZz4WPRpv+JoBVXuAuHQfujj1esCPcnT71ZogU+iapqGERlo6uguWEhA7Il5u9TZCOZXQoVZnhFSJ1V1Or4UIqS9zckHGtTU9gimyHTt5FBupisZtWHHKmkYRbE+WLTq2Uq2bZqd2ZC3CNH3q/YAfRd7uq+Vr8Tq3LFTCHle0TPWi8n0QN6TdZ5Xk0oKA3zPlTtpkkA/E24nfp77OyQUZ19b0CKbKdqxHBYV2tED1oi+RgF4RuhVyf+acNQ1FGlF65ulIzh5ADyb/V1eFYEzgUK4Fb0pQVYbfj3py99XyxTF9labhHRoJauBc1Tz9uxKxDvm9whwRIwLIJ1tVD2+E/Hmuj37HyXHXegRzVtuxd1SUtZEdxYlkReiamU/ipDWNh0QL0+9Y1ps6BObISFbEPDgTGWV+/H7UIs/R0jQsQsMuV4CEegfafUR/Cke06Mj58wDyiZVv+yDwJSfHXesRTJlbCw4fxTfZiqAgvxUzp61prBL60m/MAcYbPtMi97woqn96UYRAiBRuP9Z9OJSmYRUaulERHanykFVwaKLloECBHrn9PgiQT1Lcj6pCvuXkuGs9gtmodmwVFaVuiPG0UZxJV3TADL45b01j12SZu+6k7dnSA72vQVneuMj9uLAYTj+mY+eIacHlhIC9DuVtwFDhyT4gEgpxVptBPkHwNIGakK85Oe5aj2DqbMfOG8UP6Yrgogj34Mw1regUQu2bk7ZnQ1exuIVk+QLDUYibH8Plx3wo6pKPFn4fGja6sj1eDwOvYJywtwd0yeX3gYB8W8GfY5qQrzk57lqPYOpsx84bxQ/piqBzATMmTl3TWOguVj/puhyssala9wJFdo0wnAPX7QEMP/qvFZi+FnbJSdMghUbiGmtnlLdxnLdYj9sYw+/DAfnm0usvjlj93ghNyNecHHetRzB1tmNSVCy4sA6rjOKHdEVYiN+MiXPXNFa6Maen9N0N1diDbFsBZTliwwcQ0pUAd13iHDVNAwgNjaks7tRz4G0c5y02yx0KhTjH2Wh/C5qQrzk57lqP4NueIOoBo/ghX9FxTTh5TWOpK3faIe8ujdTYsws3kCw7OLoZ0pUB+SFzjhrtbRgK5/ZWA8HbOM5bLMUd6oj5ixDrb0ET8jUnx13rEXzbE0ZVzfSM4od8Rcc14fQ1jQ2bT4K+5O2ZaYrkPiALza4d530Q3Y/+t8TTlwrnqGkatNDQnUq/WI8Al+Ftsytb4NT5jTlg/kKAfHPpmz/VSvbhbCfHXesRTJ3tWMqCSr+ojOKHfEVQgd+MifPXNO7zdLR/33/PXWMPgNpgyUJA78MPIIjLj1md26UQTYMeGvpaqVerROAVvBv29oBILr8PBOTbCC67+n1ME/I1J8dd6xFMne3YeaP4IV0RTu83Y+KCNQ0Ddod6McK1tD0TPSs+DV3UE8BrRr9x00T2Ipx+TGZ7XYrRNFih1Uofr1cRiLxSJyUC1OD3xen3YYB8QumeFn/LyXHXegRTZztmRYXiK/oozqQrgsnDPbhmTUPBRW9PJt1K29NBc+pAtxEGdgkz/ndk7VeIy9m9fvRzTpeCtNiO0Jb5yGFUY7gcJCDwQgbnLwzIJyl2tPhbTo671iOYjWrHHFGzoziTruiAGXxzzZrGQ9OQdQ81XE9ooRs5bj8cHa02tx/toMulMP7QegOgVehacLSPCINinOMszCdLrhOkC/mSk+Ou9QimzHbszFF8k60Ipk0M0EVrWtlM0KisPZWezT6ZsxLV4lHWSJXmv1RPolBFu1vmnqbBez/e8kLKmh0gtfkklxyjxA/IJ2vWWjzxHSfHs/YI5vl2zBs1NYoT2YpQzpj/ncvWNKwW3hhoeK/A5QcyU+0euOTeAqnSApeKPhCqfMetUqBpcPnagD1XNIA7IdUghl94JeD3IcQKxy2e+YqT4671x2Web4n8UZEu245kRaM7YsV1azrc8XTD+0WvH6Ba4758y5szVVrgUjkqh6qyc4PSaRrMBixJGDXmbUF2Klp3qkkDgHxANmzxkm84Kef0u9ZT2hrbubNHsQL6YuQetWHNhWtaDKyYlLPnfc/vB8qjh5BvOV9AqrSsHx+izuxpEYIBJN26T3KlTm/R9XDZcpgx/zRAPnfZEl9wcrSMviRsk1ue00exAArSc8s7ND06l67pfcWaRyl7/G3+gBL5Mm1wJU6VlvRjZpI7/uwj3jb2yi0RYq1O5eLdsOZxv6OAfEP9+oaToA6nbe7n29KEe7EXZ3oB6tFyi5shLvbDtWt6W7J6OGHPfCk426BiM4wo0dGNkdJ2OPItL7uOI1qYTISNw47+SD3xZBbuBadhYsjvBCBfTvySq52UCwlc9R+9YhTDcyD5XU6PtFFY00iWWU+TZxm3rEE/G7an8I7uavQC0dmKOQeSyuM7X0EaLYmL/26tEHVmTdOQC7Gq2RVi+nfqV1jF7q84/ghXJtWkAbL9dXC1k7J1ZtOnlL407fAVoxiag/VvbJhIj+CMsKbRuFj2OU3+VO2LtwP6uvQzaAys2RNJak3pjNL9UOcn0J2ClKv+jo/N74BoBI1ZMUtIBvm47H1egrXYWelw6hl3wvM3BuzvSMc+XOykXI3yKt4p1Xfz4cJRhLvh8Vpo3f3Glc7juTyUZrOm1z957UA2r3/tT5OGtU0Oq/YIc7JkZVBl83uHKl2FxyIjWavaiiM26bFzYtqdUjoti1BeluRY1ylcKjB6jHi/rsijF2ovxq6yN382h4YeiO73UGgRK1/G6z3XOglq2k5OnazpYNUyfVXhylHU+6LR3/4UZpi+ppUfJhH9uRsXgQX1lvgt+TNYo4axbqHNFKvas1mEGbdQ25noi4GnihV2S4KLv9UUlyH+rAJIv5C43+FCVsTzJT9lF1zj5IQ7mSfRdaOYe3ePwrPUcdx2npH+ESIZpH7ev55lY+93dv1a6WVr5vHd/HdQnlt6u7W/GxGc7bae8kT+o1zoZPuBGaV6HfhDZ5iRUbwSrmlCCLk1XNOEEHJruKYJIeTWcE0TQsit4ZomhJBbwzVNCCG3hmuaEEJuDdc0IYTcGq5pQgi5NVzThBBya7imCSHk1nBNE0LIreGaJoSQW8M1TQght4ZrmhBCbg3XNCGE3BquaUIIuTVc04QQcmu4pgkh5NZwTRNCyK3hmiaEkFvDNU0IIbeGa5oQQm7M37//AJC+qdWBdx1zAAAAAElFTkSuQmCC'
                image = base64.b64decode(Image_blank)
                vrNumberPlate = Image.open(io.BytesIO(image))
                vrNumberPlate = vrNumberPlate.resize((100,50),Image.ANTIALIAS)  
                print("Image nhi mila")

            vrNumberPlateDigits = entry_record["parkingRecord"]["vrNumberPlateDigits"]
            vrVehicleType = entry_record["parkingRecord"]["vrVehicleType"]
            vrTicketId = entry_record["parkingRecord"]["vrTicketId"]
            amtCharged = entry_record["parkingRecord"]["vrParkingPrepaidFare"]
            vrParkingStartTimeL = entry_record["parkingRecord"]["vrParkingStartTimeL"]
            vrEnteredByName = entry_record["parkingRecord"]["vrEnteredByName"]


            if len(entry_record["passRecord"]):
                if entry_record["passResult"]["passValid"]:       
                    print("Pass Record Found")
                    vehRecord.boom_led(self,"GREEN")

                elif entry_record["passResult"]["passValid"]==False and entry_record["passResult"]["passValidCode"]==2:
                    print("Vehicle Already In")
                    vehRecord.ticketPrint(self,firebaseID,vrVehicleType,vrParkingStartTimeL,vrNumberPlate,vrNumberPlateDigits,amtCharged,vrTicketId,"ticket",ticketdate,tickettime,vrEnteredByName)
                    vehRecord.boom_led(self,"ORANGE")
                # else:
                #     print("FASTAG")
                #     vehRecord.ticketPrint(self,firebaseID,vrVehicleType,vrParkingStartTimeL,vrNumberPlate,vrNumberPlateDigits,amtCharged,vrTicketId,"ticket",ticketdate,tickettime,vrEnteredByName)
                #     vehRecord.boom_led(self,"RED")

            elif entry_record["passResult"]["passValid"]==False and entry_record["passResult"]["passValidCode"]==7:
                if len(entry_record["parkingRecord"]["vrRfidTag"]):
                    print("INVALID Pass so collect Ticket")
                    vehRecord.ticketPrint(self,firebaseID,vrVehicleType,vrParkingStartTimeL,vrNumberPlate,vrNumberPlateDigits,amtCharged,vrTicketId,"ticket",ticketdate,tickettime,vrEnteredByName)
                    vehRecord.boom_led(self,"RED")
                else:
                    print("Normal Ticket")
                    vehRecord.ticketPrint(self,firebaseID,vrVehicleType,vrParkingStartTimeL,vrNumberPlate,vrNumberPlateDigits,amtCharged,vrTicketId,"ticket",ticketdate, tickettime,vrEnteredByName)
                    vehRecord.boom_led(self,"GREEN")
        except:
            pass
        print("TASK Completed")

    def ticketPrint(self, firebaseID, vrVehicleType, vrParkingStartTimeL, vrNumberPlate, vrNumberPlateDigits,
                    amtCharged, vrTicketId, vrRecordType, ticketdate, tickettime,vrEnteredByName):

        qr_code = str("gp:pt:" + firebaseID + ":" + str(vrVehicleType) + ":" + str(vrParkingStartTimeL) + ":" + " " + ":" + vrNumberPlateDigits + 
        ":" + str(amtCharged) + ":" + str(vrRecordType) + ":" + str(vrEnteredByName) +":" + str(vrTicketId))

        # print(qr_code)
        
        bznsName = "THE CAPITAL MALL"
        bznsAdd = "  Vasai"
        gstNo ="27AAHCP8201E1ZL"
        inDate = ticketdate
        inTime = tickettime
        lostTicketCharge = ""
        parkingChargesData = "Facility Charges : \nInaugural offers - Free Parking"
        printType =str(vrRecordType)
        qrData =qr_code
        ticketNo = str(vrTicketId)
        vehNo =vrNumberPlate
        vehType = str(vrVehicleType)

        print("ticket is printing")
        printer.printTicket(bznsName, bznsAdd, vehType, vehNo, inTime, inDate,qrData, parkingChargesData, lostTicketCharge, gstNo, ticketNo)

    def boom_led(self,led_data):
        GPIO.output(24,GPIO.LOW)
        print("Boom Barrier on")
        time.sleep(1)
        GPIO.output(24,GPIO.HIGH)
        print("Boom Barrier off")
        time.sleep(1)
        try:
            ser = serial.Serial(
            port='/dev/ttyS0',
            baudrate = 115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1)
            ser.write(led_data.encode('UTF-8'))
        except:
            pass
