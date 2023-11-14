from starlette.responses import HTMLResponse
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import RPi.GPIO as GPIO
from datetime import datetime
from fastapi.templating import Jinja2Templates


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class Valve(BaseModel):
    gpio: int
    is_open: bool = False
    last_changed: datetime = datetime.now()
    
    def init(self):
        print(f"Initializing valve {self.gpio}")
        GPIO.setup(self.gpio, GPIO.OUT)
        return self
    
    def open(self):
        print(f"Opening valve {self.gpio}")
        GPIO.output(self.gpio, GPIO.HIGH)
        self.is_open = True
        self.last_changed = datetime.now()
        
    def close(self):
        print(f"Closing valve {self.gpio}")
        GPIO.output(self.gpio, GPIO.LOW)
        self.is_open = False
        self.last_changed = datetime.now()


class LED(BaseModel):
    gpio: int
    is_on: bool = False
    
    def init(self):
        print(f"Initializing LED {self.gpio}")
        GPIO.setup(self.gpio, GPIO.OUT)
        return self
    
    def on(self):
        print(f"Turning on LED {self.gpio}")
        GPIO.output(self.gpio, GPIO.HIGH)
        self.is_on = True
        
    def off(self):
        print(f"Turning off LED {self.gpio}")
        GPIO.output(self.gpio, GPIO.LOW)
        self.is_on = False
        
    
valve = Valve(gpio=17).init()
led1 = LED(gpio=22).init()
led2 = LED(gpio=27).init()

api = FastAPI()
api.mount("/static", StaticFiles(directory="static"), name="static")

@api.on_event("startup")
def startup():
    valve.close()
    led1.on()
    led2.off()

@api.on_event("shutdown")
def shutdown():
    valve.close()
    led1.off()
    led2.off()
    
@api.get("/valves/status")
def valve_status():
    return {"is_open": valve.is_open}

@api.get("/valves/open")
def open_valve():
    valve.open()
    led2.on()
    return generate_html_redirect_response()

@api.get("/valves/close")
def close_valve():
    valve.close()
    led2.off()
    return generate_html_redirect_response()

templates = Jinja2Templates(directory="templates")

@api.get("/")
def root(request: Request):
  return templates.TemplateResponse("index.html", {"request": request, "valve_state": valve})

def generate_html_root_response() -> HTMLResponse:
  state = "opened" if valve.is_open else "closed"
  state_color = "blue" if valve.is_open else "green"
  time_in_state = datetime.now() - valve.last_changed
  return HTMLResponse(content=html_content, status_code=200)

def generate_html_redirect_response() -> HTMLResponse:
    html_content = f"""
    <html>
      <head>
        <meta http-equiv="refresh" content="1; url='/api'" />
      </head>
      <body>
          <p>Processing...</p>
      </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)