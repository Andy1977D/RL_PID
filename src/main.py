# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 17:03:08 2024
Updated on 2025-05-14

@author: andy
"""

import numpy as np
import matplotlib.pyplot as plt


def system_reaction(pwm, pwm_f, voltage, mass, c_feder, speed, position, dt=0.01):
    """
    Calculates the system reaction of a heater system
    
    Arguments:
    temp_bef      -- temperature in step before
        
    Returns:
    temp_new      -- New temperature
    """
    # Variabel def
    fc = 0.25
    
    # main function
    
    pwm_f = pwm_f * (1-fc) + pwm * fc           # Tiefpass in der Ansteuerung
    force = - position * c_feder + (pwm_f-0.50) * voltage * 35 # Kraft
    speed += dt * force/mass                    # Beschleuningung --> Geschwindigkeit
    speed = speed * (1-dt*1.5)                    # Dämpfung
    position += dt * speed                      # Integral --> Position

    return speed, position, pwm_f


def system_temp_reaction(pwm, voltage, temp_bef, outside_temp, outside_wind, heat_capa, dt=0.01):
    """
    Calculates the system reaction of a heater system
    
    Arguments:
    temp_bef      -- temperature in step before
        
    Returns:
    temp_new      -- New temperature
    """
    powerin = voltage**2 * pwm
    powerout = (temp_bef-outside_temp)*(2+outside_wind)
    powerin = powerin-powerout
    #print(powerin)
    heatup = powerin*dt/max(heat_capa,0.01)
    temp_new = temp_bef+heatup
    
    return temp_new


# Variation parameters   : voltage, outisde_temp, outside_wind, temp_desired
# fixed parameters       : heat_capa, temp_bef, (sequence_length)
# optimization parameter : sequence of pwm


# X : 100 test case, 4 variation parameters
# Y : 100 test cases, time series of 200 values
nr_testcases = 36


X = np.zeros((nr_testcases,4))
Y = np.zeros((nr_testcases,500))
X1 = np.zeros((nr_testcases,500))


# X[:,0] = np.random.rand(100)*6+8        # voltage       - random between 8 and 14 V
# X[:,1] = np.random.rand(100)*40+10      # outside temp  - random between 10 and 50 °C
# X[:,2] = np.random.rand(100)*2+0        # outside wind  - random between 0 and 2 m/s
# X[:,3] = np.random.rand(100)*100+50     # desired temp  - random between 50 and 150 °C

# pol_p = 1.2
# pol_i = 0.65
# pol_d = 0.38
pol_p = 0.17
pol_i = 0.65
pol_d = 0.08
lastreward = 0

for i in range(1,2000):
 
    X[:,0] = np.random.rand(nr_testcases)*5+10        # voltage       - random between 8 and 14 V
    X[:,1] = np.random.rand(nr_testcases)*0.40+0.10      # mass       - random between 10 and 50 °C
    X[:,2] = np.random.rand(nr_testcases)*3+1        # c_feder    - random between 0 and 2 m/s
    X[:,3] = np.random.rand(nr_testcases)*10+20     # desired pos  - random between 50 and 150 °C
     
    
    dp = 0
    di = 0
    dd = 0
    eps = np.random.rand(1)
    if eps> 0.7:
        dp = 0.2*(np.random.rand(1)-0.5)
    else:
        if eps> 0.4:
            di = 0.2*(np.random.rand(1)-0.5)
        else:
            if eps > 0.1:
                dd = 0.1*(np.random.rand(1)-0.5)
        
    
    # initialisieren
    
    temp_bef = 20
    heat_capa = 5
       
    position = 0
    speed = 0
    pwm_f = 0
    pwm_i = 0
    loss = np.zeros((nr_testcases,1))
    
    for t in range(1,500):
        
        # settings holen
        
       voltage    =X[:,0]
       mass       =X[:,1]
       c_feder    =X[:,2]
       target_pos =X[:,3]
       
       # voltage=X[:,0]
       # outside_temp=X[:,1]
       # outside_wind=X[:,2]
       # target_temp=X[:,3]
       # PID Regler nun durchlaufen
       
       pwm_p = 50+(pol_p+dp)*(target_pos-position)          # simpler PID-Regler mit Offset
       pwm_d = -(pol_d+dd)*speed
       pwm_i += 0.01 *(pol_i+di)*(target_pos-position)
       pwm_i = np.clip(pwm_i,0,100)
       
       # pwm_p = 50+1.2*(target_pos-position)          # simpler PID-Regler mit Offset
       # pwm_d = -0.2*speed
       # pwm_i += 0.01 *0.35*(target_pos-position)
       # pwm_i = np.clip(pwm_i,0,100)
       
       pwm = np.clip(pwm_p+pwm_d+pwm_i,0,100)
       pwm = 0.01*pwm
       
       #print(pwm)
       speed, position, pwm_f = system_reaction(pwm,pwm_f,voltage,mass,c_feder,speed,position)
       Y[:,t] = position
       X1[:,t] = pwm
       
       if t>20:
          loss[:,0] += (target_pos-Y[:,t])**2
       
       #print(loss)
       
    ueberschw = np.max(Y,axis=1)-target_pos
    print('Überschwinger =',ueberschw)
    print('Überschwinger =',150*max(ueberschw)**2)
    
    avgloss = np.mean(loss)
    maxloss = np.max(loss)
    
    print("Loop nummer",i," epsilon ",eps)
    #print(avgloss)
    #print(maxloss)

    reward = -avgloss*0.5-maxloss*0.5 - 250*max(ueberschw)**2
    print("reward",reward)
    
    if eps <= 0.1:
        lastreward = reward
        print("new lastreward ",lastreward)
    else:
        if reward>lastreward:
            pol_p += dp
            pol_i += di
            pol_d += dd
            print("new parameters",pol_p,pol_i,pol_d)
            lastreward = reward
            

# Zeitvektor erstellen (x-Achse)
time = np.arange(Y.shape[1])  # Zeit von 0 bis 499

# Plot erstellen
plt.figure(figsize=(12, 6))
for i in range(Y.shape[0]):  # Für jede Variante
    plt.plot(time, Y[i], alpha=0.6, linewidth=0.5, label=f'Variante {i+1}' if i < 10 else "")
    plt.plot(time, X1[i]*10, alpha=0.6, linewidth=1.5, label=f'PWM {i+1}' if i < 10 else "")

# Achsen beschriften und Titel hinzufügen
plt.xlabel("Zeit")
plt.ylabel("Wert")
plt.title("Verläufe über die Zeit")
plt.grid(True)

# Optionale Legende (beschränkt auf die ersten 10 Verläufe, um Übersicht zu behalten)
plt.legend(loc="upper right", title="Varianten", ncol=2, fontsize="small", frameon=False)

# Plot anzeigen
plt.tight_layout()
plt.show()



# plt.title("Systemverhalten nach Sprung")
# axes = plt.gca()
# axes.set_xlim([-10,120])
# axes.set_ylim([-10,120])
# #plot_decision_boundary(lambda x: predict_dec(parameters, x.T), X_trainS, Y_trainS)

# #plt.scatter(Y,Y)

