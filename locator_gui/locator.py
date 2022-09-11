import tkinter
import tkinter as tk
from tkinter import ttk,messagebox,Canvas
from tkinter import *
#from tkinter.ttk import *
from PIL import Image
from pystray import MenuItem, Menu, Icon
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import sys
import serial
import time
import re
import math

recieve_flag=0
mode = 0

lastTime=0.0
updateRecieveTime = 2
curAngle=0
_range = 0
_angle = 0
_lastAngle=0
font_format = 'Arial'
bg_format = "#282828"
bg2_format = "#232323"
fg_format = "#b3b3b3"
fg_green_format = "#008000"
max_range = 1000
maxSpeed = 0
curSpeed = 0.0
filVal = 0.0

def xc_get(fi,r):
    global R,graph_w_center
    fii = (math.pi/180)*fi
    x = R*r*math.cos(fii)
    _xc = graph_w_center + x
    return _xc

def yc_get(fi,r):
    global R,graph_h_center
    fii = (math.pi/180)*fi
    y = R*r*math.sin(fii)
    _yc = graph_h_center - y
    return _yc

def esc_click(event):
    global recieve_flag
    print("ESC event")
    print(mode)
    if mode==0:
        print("exit!")
        sys.exit()
    else:
        uart.write(b's')
        ACmenu()
        recieve_flag=0
        mode1StartStopButton['text']="Старт"
        mode3StartStopButton['text']="Старт"
        
def serial_ports():                                     #Функция сканирования COM-портов
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
#    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
#        ports = glob.glob('/dev/tty[A-Za-z]*')
#    elif sys.platform.startswith('darwin'):
#        ports = glob.glob('/dev/tty.*')
#    else:
#        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port,timeout=0.1, writeTimeout=0.1)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass

    return result

def connect_click():                #Обработчик нажатия кнопки "Подключиться/Отключиться"

    global recieve_flag
    if not uart.is_open:
        try:
            cur_com_port = comboComs.get()               #Мы вытаскиваем из combo-списка название нужного нам COM порта
            print("выбран:",cur_com_port)
            uart.port=cur_com_port                          #И заносим его в настройки uart
            uart.baudrate = 9600                            # Частота баудрейта. ДОЛЖНА СОВПАДАТЬ С БАУДРЕЙТОМ АРДУИНО
            uart.open()
            print("uart connect...")

            start_time =time.perf_counter()
            while 1:

                dtime = time.perf_counter() -start_time
                if dtime>3:
                    messagebox.showerror(title="Ошибка", message="COM-порт не отвечает")
                    uart.close()            
                    recieve_flag=0
                    break

                uartin = uart.readline()                    #Ждем отклика от ардуино в виде команды "VOLUME_CONTROL"
                answer = uartin.decode('utf-8')
                if answer== "LOCATOR+OK":
                    print("ARDUINO:",answer)
                    print("Подключено")
                    ACmenu()

                    break
        except Exception as err:
            print(err)
            messagebox.showerror(title="Ошибка", message=err)

    else:
        uart.close()            # Все это происходит в случае, если мы нажимаем "Отключиться"
        recieve_flag=0
        print("uart is close")
        #sys.exit()
        #connect_button.configure(text = 'Подключиться')
        #send_button.configure(state='disable',text="Отправка настроек и запуск регулятора")
        
def ACmenu():

    global mode
    mode=0
    frame_connect.place_forget()
    frame_mode1.place_forget()
    frame_mode2.place_forget()
    frame_mode3.place_forget()
    mode1graph.place_forget()
    app.attributes('-fullscreen', True)
    print("ACmenu")

    #app.geometry('{}x{}+{}+{}'.format(1200,1000,0,0))
    #labelTop.destroy()
    #settingsLabel.destroy()
    #comboComs.destroy()
    #connect_button.destroy()

    frame_menu.place(x=0,y=0,w=centerX*2,h=centerY*2)
    modeLabel.place(x=centerX-1000//2,y=300,w=1000,h=100)
    mode1.place(x=centerX-600//2,y=400,w=600,h=100)
    mode2.place(x=centerX-600//2,y=500,w=600,h=100)
    mode3.place(x=centerX-600//2,y=600,w=600,h=100)
    modeSelectButton.place(x=centerX-600//2,y=750,w=600,h=100)
    modeMyInfo.place(x=centerX*2-500,y=35,h=70,w=500)
    app.after(500, lambda: modeMyInfo.place_forget())
    
def modeSelect():
    mode = curMode.get()
    if mode==1:
        _mode1()
    elif mode==2:
        _mode2()
    elif mode==3:
        _mode3()
        
def _mode1():
    print("mode1")
    global mode,max_range
    mode=1
    frame_menu.place_forget()


    frame_mode1.place(x=0,y=0,w=centerX*2,h=centerY*2)

    a = 100
    mode1ScaleMinFi_Label.place(x=0,y=centerY*2-265+a)
    mode1ScaleMinFi.place(x=0,y=centerY*2-230+a,w=centerX,h=80)

    mode1ScaleMaxFi_Label.place(x=centerX,y=centerY*2-265+a)
    mode1ScaleMaxFi.place(x=centerX,y=centerY*2-230+a,w=centerX,h=80)

    mode1DeltaFi_Label.place(x=0,y=centerY*2-149+a,w=centerX/2,h=50)
    mode1Deltafi1.place(x=centerX/2,y= centerY*2 -149+a,w=centerX/4,h=50)
    mode1Deltafi2.place(x=3*centerX/4,y= centerY*2 -149+a,w=centerX/4,h=50)
    mode1Deltafi3.place(x=4*centerX/4,y= centerY*2 -149+a,w=centerX/4,h=50)
    mode1Deltafi5.place(x=5*centerX/4,y= centerY*2 -149+a,w=centerX/4,h=50)
    mode1Deltafi10.place(x=6*centerX/4,y= centerY*2 -149+a,w=centerX/4,h=50)
    mode1StartStopButton.place(x=7*centerX/4,y= centerY*2 -149+a,w=centerX/4,h=50)
    maxRentry.place(x=graph_w-DArc-DArcStep*1 +20,y=graph_h_center+5)

    frame_mode1graph.place(x=0,y=0,w=centerX*2,h=centerY*2-160)
    mode1graph.place(x=0,y=0,w=centerX*2,h=centerY*2-160)
    mode1Label.place(x=2,y=2,w=350,h=70)
    mode1CurRangeLabel.place(x=centerX*2-200+18,y=2,w=100,h=30)
    mode1CurRange.place(x=centerX*2-120+18,y=2,w=100,h=30)
    mode1CurAngleLabel.place(x=centerX*2-200+18,y=30,w=100,h=30)
    mode1CurAngle.place(x=centerX*2-120+18,y=30,w=100,h=30)
    for i in range(1,6):
        create_line_radar(30*i)

    for i in range(0,20):
        if i%2 ==0:
            wid=3
        else:
            wid=1
        mode1graph.create_arc(DArc+DArcStep*i,DArcStep*i,graph_w-DArc-DArcStep*i,(graph_h-50)*2-DArcStep*i, start=0,extent=180, outline=fg_green_format, width=wid)
    mode1ScaleMinFi_update(int(mode1ScaleMinFi.get()))
    mode1ScaleMaxFi_update(int(mode1ScaleMaxFi.get()))
    
def mode1connect():
    global  recieve_flag,max_range
    minFi = mode1ScaleMinFi.get()
    maxFi = mode1ScaleMaxFi.get()
    deltaFi = curDeltaFi.get()
    max_range = int(maxRentry.get())

    if max_range<50:
        messagebox.showerror(title="Ошибка", message="Rmax должен быть не меньше")
        return 0

    mode1graph.delete('maxrange')
    for i in range(1,10):
        mode1graph.create_text(graph_w-DArc-DArcStep*i*2,graph_h_center+18, text=int(max_range-(max_range*i)/10),justify=CENTER,fill='red',font=(font_format,15,'bold'),tag='maxrange')
    for i in range(0,10):
        mode1graph.create_text(DArc+DArcStep*i*2,graph_h_center+18, text=int(max_range-(max_range*i)/10),justify=CENTER,fill='red',font=(font_format,15,'bold'),tag='maxrange')


    if minFi>maxFi:
        messagebox.showerror(title="Ошибка", message="Минимальный угол развертки должен быть меньше максимального")
        return 0

    if recieve_flag==0:

        print("connect mode1")
        recieve_flag=1

        data1 = bytes(str(minFi),'utf-8')       #Кодируем их для отправки по uart
        data2 = bytes(str(maxFi),'utf-8')
        data3 = bytes(str(deltaFi),'utf-8')

        uart.write(b'$')                            #Отправляем пакет данных в виде $1 data1 data2 data3;
        uart.write(b'1')
        uart.write(b' ')
        uart.write(data1)
        uart.write(b' ')
        uart.write(data2)
        uart.write(b' ')
        uart.write(data3)
        uart.write(b';')

        for i in range(0,180):
            mode1graph.delete('a'+str(i))

        start_time =time.perf_counter()
        while 1:

            dtime = time.perf_counter() -start_time
            if dtime>3:
                messagebox.showerror(title="Ошибка", message="COM-порт не отвечает")
                recieve_flag=0
                return 0
            uartin = uart.readline()                    #Ждем отклика от ардуино в виде команды "VOLUME_CONTROL"
            answer = uartin.decode('utf-8')
            if answer== "LOCATOR+SET+OK":
                print("ARDUINO:",answer)
                print("Запуск режима локатора")
                break
        mode1StartStopButton['text']="Стоп"
        app.after(updateRecieveTime+10, lambda: mode1_recieve())
    else:
        print("disconnect mode1")

        recieve_flag=0
        uart.write(b's')
        mode1StartStopButton['text']="Старт"
        
def mode1_recieve():
    global recieve_flag,lastTime,_range,_angle,max_range,_lastAngle
    times = time.time()

    while recieve_flag==1:
        if times-lastTime>(updateRecieveTime/1000):     # Алгоритм таймера, как в коде ардуино
            uart_message = uart.read_until(';')             # Считываем uart сообщения раз в updateRecieveTime/1000 секунд
            str_message = str(uart_message)

            try:

                data  = re.findall(r'\d+',(str_message.partition(';')[0]))
                _range = int(data[0])
                _angle = int(data[1])

            except:
                print("err")


            print("range:",_range," angle:",_angle)
            mode1RadarLine_update(_angle)
            mode1CurAngle['text']=str(_angle)+' °'
            mode1CurRange['text']=str(_range)+' мм'
                    # Повторно вызываем volume_recieve() через updateRecieveTime. нужна эта функция,чтобы само окно не зависало на момент приема данных


            x = xc_get(180-int(_angle),_range/max_range)
            y = yc_get(180-int(_angle),_range/max_range)
            mode1graph.delete('a'+str(_angle))
            mode1graph.create_oval(x, y, x, y, width = 6,outline='lightgreen',tag='a'+str(_angle))

            lastTime=times
            _lastAngle=_angle
            app.after(updateRecieveTime, lambda: mode1_recieve())
            return
        
def _mode2():
    print("mode2")
    global mode
    mode=2
    frame_menu.place_forget()
    frame_mode2.place(x=0,y=0,w=centerX*2,h=centerY*2)
    mode2Label.place(x=centerX-1000//2,y=00,w=1000,h=100)
    mode2CurRangeLabel.place(x=centerX-600//2-200,y=300)
    mode2CurRange.place(x=(centerX-600//2)+400,y=292)
    mode2CurAngleLabel.place(x=centerX-600//2-200,y=500)
    mode2CurAngle.place(x=(centerX-600//2)+400,y=492)

    mode2ScaleLabel.place(x=centerX-1000//2,y=800-50)
    mode2ScaleAngle.place(x=centerX-1000//2,y=800)
    measureButton.place(x=centerX-600//2,y=800+100,w=600,h=100)

    curAngleLabel = tk.Label(app,text="Текущий угол оси дальномера: ", font=(font_format, 25, 'bold'),bg=bg_format,fg=fg_format)
    #curAngleLabel.grid(row=1,column=1,columnspan=2)

    curRangeLabel = tk.Label(app,text="Расстояние до объекта: ", font=(font_format, 25, 'bold'),bg=bg_format,fg=fg_format)
    #curRangeLabel.grid(row=2,column=1,columnspan=2)
    
def mode2measure():
    curAngle = mode2ScaleAngle.get()
    mode2CurAngle['text'] = str(curAngle)+' °'
    data1 = bytes(str(curAngle),'utf-8')

    uart.write(b'$')                            #Отправляем пакет данных в виде $data1 data2 data3;
    uart.write(b'2')
    uart.write(b' ')
    uart.write(data1)
    uart.write(b';')
    while 1:
        uartin = uart.readline()               # После этого ждем команды-отклика от ардуино "SETTINGS OK"
        answer = uartin.decode('utf-8')
        if answer=="LOCATOR+SET+OK":
            print("Locator+set+ok")
            break
    time.sleep(0.3)
    while 1:
        uartin = uart.readline()
        answer = uartin.decode('utf-8')
        if answer:
            print('Answer=',answer)
            break
    answerStr  = re.findall(r'\d+', str(answer))      #Пробуем вытащить из сообщения int
    if int(answerStr[0])>8000:
        answerStr[0]='???'
    mode2CurRange['text']= answerStr[0]+ " мм"

def _mode3():
    print("mode3")
    global mode
    mode=3
    frame_menu.place_forget()
    frame_mode3.place(x=0,y=0,w=centerX*2,h=centerY*2)
    mode3Label.place(x=centerX-1000//2,y=00,w=1000,h=100)
    mode3CurSpeedLabel.place(x=centerX-600//2-200,y=300)
    mode3CurSpeed.place(x=(centerX-600//2)+400,y=292)
    mode3CurAngleLabel.place(x=centerX-600//2-200,y=500)
    mode3CurAngle.place(x=(centerX-600//2)+400,y=492)
    mode3ScaleLabel.place(x=centerX-1000//2,y=800-50)
    mode3ScaleAngle.place(x=centerX-1000//2,y=800)
    mode3StartStopButton.place(x=centerX-600//2,y=800+100,w=600,h=100)
    mode3Speedometr.place(x=centerX*(2-0.25),y=window_height-window_height*0.1,w=window_width/10,h=window_height*4)
    mode3Speedometr['value']=0

    mode3graph.place(x=centerX*(2-0.21),y=window_height-window_height*0.3,w=window_width/4,h=window_height*4.5)
    global maxSentry
    maxSentry = Entry(mode3graph, width=2,bg=bg_format,fg='red',font=(font_format,15,'bold'),selectforeground=bg_format)
    maxSentry.insert(0,"2")
    maxSentry.place(x=window_width/10,y=(window_height-window_height*0.87))

    mode1graph.delete('maxspeed')
    for i in range(0,51):
        a = 1
        if(i%5==0):
            a=3
        else:
            a=1
        mode3graph.create_line(0,i*(window_height/12.5)+(window_height-window_height*0.8), window_width/15,i*(window_height/12.5)+(window_height-window_height*0.8),fill='red',width=a)

def mode3connect():
    global  recieve_flag,max_range,maxSpeed
    maxSpeed = int(maxSentry.get())
    mode3graph.delete('maxspeed')
    for i in range(1,11):
        dS = maxSpeed*(1-i/10)
        mode3graph.create_text(window_width/7,
                               i*(window_height/2.5)+(window_height-window_height*0.8)
                               ,text=str(round(dS, 1)),
                               justify=CENTER,
                               fill='red',
                               font=(font_format,15,'bold'),
                               tag='maxspeed')

    if recieve_flag==0:

        print("connect mode3")
        recieve_flag=1

        curAngle = int(mode3ScaleAngle.get())
        mode3CurAngle['text']= str(curAngle) +' °'

        data1 = bytes(str(curAngle),'utf-8')       #Кодируем их для отправки по uart

        uart.write(b'$')                            #Отправляем пакет данных в виде $1 data1 data2 data3;
        uart.write(b'3')
        uart.write(b' ')
        uart.write(data1)
        uart.write(b';')

        start_time =time.perf_counter()
        while 1:

            dtime = time.perf_counter() -start_time
            if dtime>3:
                messagebox.showerror(title="Ошибка", message="COM-порт не отвечает")
                recieve_flag=0
                return 0
            uartin = uart.readline()                    #Ждем отклика от ардуино в виде команды "VOLUME_CONTROL"
            answer = uartin.decode('utf-8')
            if answer== "LOCATOR+SET+OK":
                print("ARDUINO:",answer)
                print("Запуск режима измерения скорости")
                break
        mode3StartStopButton['text']="Стоп"
        app.after(updateRecieveTime+1, lambda: mode3_recieve())
    else:
        print("disconnect mode1")
        mode3Speedometr['value']=0
        recieve_flag=0
        uart.write(b's')
        mode3StartStopButton['text']="Старт"
        
def mode3_recieve():
    global recieve_flag,lastTime,maxSpeed,curSpeed
    times = time.time()
    while recieve_flag==1:
        if times-lastTime>(updateRecieveTime/1000):     # Алгоритм таймера, как в коде ардуино
            uart_message = uart.readline()                # Считываем uart сообщения раз в updateRecieveTime/1000 секунд
            #print(uart_message)
            try:
                data = re.findall(r'\d+',str(uart_message))
                curSpeed = int(data[1])/1000  #                        !!!!ЖЕНЯ, ТУТ БЫЛО 1000
                if curSpeed>5:
                    curSpeed=0
                #curSpeed = 1.158
                if int(data[0])==0:
                    curSpeed=curSpeed*(-1)
                    
            except:
                0
            #print('speed=',curSpeed)
            fCurSpeed= speedFilter(curSpeed)
            mode3Speedometr['value']=int(math.fabs(fCurSpeed*100/maxSpeed))
            mode3CurSpeed['text']=str(curSpeed)+' м/c'
            app.after(updateRecieveTime, lambda: mode3_recieve())        # Повторно вызываем volume_recieve() через updateRecieveTime. нужна эта функция,чтобы само окно не зависало на момент приема данных


            x = xc_get(180-int(_angle),_range/max_range)
            y = yc_get(180-int(_angle),_range/max_range)
            mode1graph.delete('a'+str(_angle))
            mode1graph.create_oval(x, y, x, y, width = 6,outline='lightgreen',tag='a'+str(_angle))

            lastTime=times
            break

def speedFilter(newVal):
    global filVal
    if newVal<filVal:
        filVal = filVal + (newVal-filVal)*0.05
    else:
        filVal = filVal + (newVal-filVal)*1
    return filVal

def create_line_radar(ugol):
    xc = xc_get(ugol,1)
    yc = yc_get(ugol,1)
    mode1graph.create_line(graph_w_center,graph_h_center,xc,yc,width=2,fill=fg_green_format)
    
def mode1ScaleMinFi_update(ugol):
    xc = xc_get(180-int(ugol),1)
    yc = yc_get(180-int(ugol),1)
    mode1graph.delete('minFiLine')
    mode1graph.create_line(graph_w_center,graph_h_center,xc,yc,width=3,fill='red',tag='minFiLine')
    
def mode1ScaleMaxFi_update(ugol):
    xc = xc_get(180-int(ugol),1)
    yc = yc_get(int(ugol),1)
    mode1graph.delete('maxFiLine')
    mode1graph.create_line(graph_w_center,graph_h_center,xc,yc,width=3,fill='red',tag='maxFiLine')
    
def mode1RadarLine_update(ugol):
    xc = xc_get(180-int(ugol),1)
    yc = yc_get(180-int(ugol),1)
    mode1graph.delete('radarLine')
    mode1graph.create_line(graph_w_center,graph_h_center,xc,yc,width=3,fill='lightgreen',tag='radarLine')

#____Создание_окна_______
com_ports = serial_ports()              # вытаскиваем в переменную все работающие ком порты
uart = serial.Serial(timeout=.01)        # создаем объект serial для uart соединения с ардуино

app = tk.Tk()
app["bg"] = bg_format
app.title("Локатор")
app.iconbitmap('bonch.ico')

curMode = tk.IntVar()
curMode.set(0)
curDeltaFi = tk.IntVar()
curDeltaFi.set(1)

window_width  = 300         #ширина окна
window_height = 200         #высота окна
w = app.winfo_screenwidth()  # Вычисление центра экрана для окна
w = w//2 - window_width//2
h = app.winfo_screenheight()
h = h//2 - window_height//2
centerX = app.winfo_screenwidth()//2
centerY = app.winfo_screenheight()//2

app.geometry('{}x{}+{}+{}'.format(window_width,window_height,w,h))
app.resizable(False, False)

#______________________________________________________________________________ОКНО ПОДКЛЮЧЕНИЯ УСТРОЙСТВА_____________________________________________________________________________________________________
frame_connect = Frame(app,bg=bg_format)
settingsLabel = tk.Label(frame_connect,text="Подключение устройства",font=(font_format,16,'bold'),fg='red',bg=bg_format)
labelTop = tk.Label(frame_connect,text = "Выберите COM-порт:",font=(font_format, 10, 'bold'),bg = bg_format,fg = fg_format)
connect_button = tk.Button(frame_connect,text="Подключиться", padx="20", pady="8", font=(font_format, 10, 'bold'),fg= 'red', command=connect_click, bg = bg_format)

#______________________________________________________________________________________ОКНО ВЫБОРА РЕЖИМА РАБОТЫ УСТРОЙСТВА______________________________________________________________________________________
frame_menu = Frame(app, bg=bg_format) # root можно не указывать
modeLabel = tk.Label(frame_menu,text="Выбор режима работы локатора:",font=(font_format,30,'bold'),fg='red',bg=bg_format)

mode1 = tk.Radiobutton(frame_menu,text="Режим радара ",font=(font_format,25,'bold'), value=1, variable=curMode, padx=100, pady=10,bg=bg_format,fg = fg_format,indicatoron = 0,selectcolor=fg_green_format,width=24)
mode2 = tk.Radiobutton(frame_menu,text="Режим одиночных измерений ",font=(font_format,25,'bold'), value=2, variable=curMode, padx=100, pady=10,bg=bg_format,fg = fg_format,indicatoron = 0,selectcolor=fg_green_format,width=24)
mode3 = tk.Radiobutton(frame_menu,text="Режим измерения скорости",font=(font_format,25,'bold'), value=3, variable=curMode, padx=100, pady=10,bg=bg_format,fg = fg_format,indicatoron = 0,selectcolor=fg_green_format,width=24)
modeSelectButton = tk.Button(frame_menu,text="Далее",padx=100, pady=10, font=(font_format, 25 , 'bold'),fg='red', command=modeSelect, bg = bg_format,width=24,relief = GROOVE)

modeMyInfo = tk.Label(frame_menu,text="Разработано студентом РТ-82\nЧервинко Е.И., кафедра РОС, 2022",font=(font_format,20),fg='black',bg=fg_format,justify=LEFT)

#______________________________________________________________________________ОКНО РЕЖИМА ЛОКАТОРА №1______________________________________________________________________________________________
frame_mode1 = Frame(app, bg=bg_format) # root можно не указывать

mode1ScaleMinFi_Label = tk.Label(frame_mode1,text="Минимальный угол развертки локатора φmin:",font=(font_format,20),bg=bg_format,fg='red')
mode1ScaleMinFi = tk.Scale(
    frame_mode1, orient="horizontal", resolution=1, from_=0, to=180, length = 1000,
    sliderlength=50,relief = "sunken",tickinterval=10,bg=bg_format,fg='red',
    font=(font_format,15,'bold'),command = mode1ScaleMinFi_update)
mode1ScaleMinFi.set(0)

mode1ScaleMaxFi_Label = tk.Label(frame_mode1,text="Максимальный угол развертки локатора φmax:",font=(font_format,20),bg=bg_format,fg='red')
mode1ScaleMaxFi = tk.Scale(
    frame_mode1, orient="horizontal", resolution=1, from_=0, to=180, length = 1000,
    sliderlength=50,relief = "sunken",tickinterval=10,bg=bg_format,fg='red',
    font=(font_format,15,'bold'),command = mode1ScaleMaxFi_update)
mode1ScaleMaxFi.set(180)

mode1DeltaFi_Label = tk.Label(frame_mode1,text="Шаг измерений Δφ:",font=(font_format,25),bg=fg_format,fg='black')
mode1Deltafi1 = tk.Radiobutton(frame_mode1,text="1",font=(font_format,15,'bold'), value=1, variable=curDeltaFi, pady=0,bg=fg_format,fg = 'black',indicatoron = 0,selectcolor=fg_green_format,width=24)
mode1Deltafi2 = tk.Radiobutton(frame_mode1,text="2",font=(font_format,15,'bold'), value=2, variable=curDeltaFi, pady=0,bg=fg_format,fg = 'black',indicatoron = 0,selectcolor=fg_green_format,width=24)
mode1Deltafi3 = tk.Radiobutton(frame_mode1,text="3",font=(font_format,15,'bold'), value=3, variable=curDeltaFi, pady=0,bg=fg_format,fg = 'black',indicatoron = 0,selectcolor=fg_green_format,width=24)
mode1Deltafi5 = tk.Radiobutton(frame_mode1,text="5",font=(font_format,15,'bold'), value=5, variable=curDeltaFi, pady=0,bg=fg_format,fg = 'black',indicatoron = 0,selectcolor=fg_green_format,width=24)
mode1Deltafi10 = tk.Radiobutton(frame_mode1,text="10",font=(font_format,15,'bold'), value=10, variable=curDeltaFi, pady=0,bg=fg_format,fg = 'black',indicatoron = 0,selectcolor=fg_green_format,width=24)

mode1StartStopButton = tk.Button(frame_mode1,text="Старт", padx=0, pady=10, font=(font_format, 20, 'bold'),fg= 'red', command=mode1connect, bg = bg_format,width=40,height=10)

graph_w = centerX*2
graph_h = centerY*2-160

R = graph_h-50
DArc = graph_w - (R)*2
DArc = DArc/2
DArcStep = (R)/20
graph_w_center = centerX
graph_h_center = graph_h-50
frame_mode1graph = Frame(frame_mode1,bg=bg_format)
mode1graph = Canvas(frame_mode1graph, width=graph_w, height=graph_h, bg=bg_format)
mode1Label  = tk.Label(mode1graph,text="Режим локатора", font=(font_format, 30, 'bold'),bg=bg_format,fg='red')
mode1CurRangeLabel = tk.Label(mode1graph,text="R(φ):",font=(font_format,15),bg=bg_format,fg=fg_green_format,justify=RIGHT)
mode1CurAngleLabel = tk.Label(mode1graph,text="φ:",font=(font_format,15),bg=bg_format,fg=fg_green_format,justify=RIGHT)
mode1CurRange   = tk.Label(mode1graph,text="0 мм",font=(font_format,15,'bold'),bg=bg_format,fg='red',justify=LEFT)
mode1CurAngle   = tk.Label(mode1graph,text="0 °",font=(font_format,15,'bold'),bg=bg_format,fg='red',justify=LEFT)
maxRentry = Entry(mode1graph, width=4,bg=bg_format,fg='red',font=(font_format,15,'bold'),selectforeground=bg_format)
maxRentry.insert(0,"1000")

#______________________________________________________________________________ОКНО РЕЖИМА ОДИНОЧНЫХ ИЗМЕРЕНИЙ_№2______________________________________________________________________________________________
frame_mode2 = Frame(app, bg=bg_format) # root можно не указывать
mode2Label  = tk.Label(frame_mode2,text="Режим одиночных измерений", font=(font_format, 50, 'bold'),bg=bg_format,fg='red')
mode2CurRangeLabel = tk.Label(frame_mode2,text="Текущее расстояние до цели:",font=(font_format,30),bg=bg_format,fg=fg_green_format)
mode2CurAngleLabel = tk.Label(frame_mode2,text="Текущий угол оси локатора :",font=(font_format,30),bg=bg_format,fg=fg_green_format)
mode2CurRange   = tk.Label(frame_mode2,text="0 мм",font=(font_format,40,'bold'),bg=bg_format,fg='red')
mode2CurAngle   = tk.Label(frame_mode2,text="90°",font=(font_format,40,'bold'),bg=bg_format,fg='red')

mode2ScaleAngle = tk.Scale(frame_mode2, orient="horizontal", resolution=1, from_=0, to=180, length = 1000,sliderlength=50,relief = "sunken",tickinterval=10,bg=bg_format,fg='red',font=(font_format,15,'bold'))
mode2ScaleAngle.set(90)
mode2ScaleLabel = tk.Label(frame_mode2,text="Задание угла оси локатора:",font=(font_format,25),bg=bg_format,fg='red')

measureButton = tk.Button(frame_mode2,text="Измерение", padx=20, pady=8, font=(font_format, 30, 'bold'),fg= 'red', command=mode2measure, bg = bg_format,width=40,height=10)

#______________________________________________________________________________ОКНО РЕЖИМА ИЗМЕРИТЕЛЯ СКОРОСТИ №3______________________________________________________________________________________________
frame_mode3 = Frame(app, bg=bg_format)
mode3Label  = tk.Label(frame_mode3,text="Режим измерения скорости", font=(font_format, 50, 'bold'),bg=bg_format,fg='red')
mode3CurAngleLabel = tk.Label(frame_mode3,text="Текущий угол оси локатора :",font=(font_format,30),bg=bg_format,fg=fg_green_format)
mode3CurAngle   = tk.Label(frame_mode3,text="  ",font=(font_format,40,'bold'),bg=bg_format,fg='red')
mode3CurSpeedLabel = tk.Label(frame_mode3,text="Текущая скорость :",font=(font_format,30),bg=bg_format,fg=fg_green_format)
mode3CurSpeed   = tk.Label(frame_mode3,text="   ",font=(font_format,40,'bold'),bg=bg_format,fg='red')

mode3ScaleAngle = tk.Scale(frame_mode3, orient="horizontal", resolution=1, from_=0, to=180, length = 1000,sliderlength=50,relief = "sunken",tickinterval=10,bg=bg_format,fg='red',font=(font_format,15,'bold'))
mode3ScaleAngle.set(90)
mode3ScaleLabel = tk.Label(frame_mode3,text="Задание угла оси локатора:",font=(font_format,25),bg=bg_format,fg='red')
mode3StartStopButton = tk.Button(frame_mode3,text="Старт", padx=20, pady=8, font=(font_format, 30, 'bold'),fg= 'red', command=mode3connect, bg = bg_format,width=40,height=10)

mode3Speedometr = ttk.Progressbar(frame_mode3, orient="vertical", mode="determinate", maximum=100, value=0)

mode3graph = Canvas(frame_mode3, width=window_width/15, height=window_height*4.2, bg=bg_format,bd=0, highlightthickness=0, relief='ridge')

#Пакуем первое окно_________________________________________________________________________________________________________________________________
frame_connect.place(x=0,y=0,w=window_width,h=window_height)
settingsLabel.pack()
labelTop.pack()

if com_ports:
    comboComs = ttk.Combobox(frame_connect, values=com_ports)
    comboComs.pack()
    comboComs.current(0)
    print(comboComs.current(), comboComs.get())
else:
    labelComsError = tk.Label(frame_connect, text="COM-порты не найдены,\nпроверьте подключение устройства", fg="red",relief = "sunken",bg=bg_format)

    labelComsError.pack()
    connect_button.configure(state = 'disabled')
connect_button.pack(expand=1)

#_____________________________________________________________________________________________________________________________________________________
app.bind('<Escape>', esc_click)
app.mainloop()




