from wtforms import Form, FloatField, validators
from flask import Flask, render_template, request
import numpy as np
import matplotlib.pyplot as plt
import os, time, glob


#==============================================================================

class Electron:
    def __init__(self):
        self.name = "Electron"
        self.mass = 9.1e-31
        self.charge = 1.6e-19
        self.velocity = np.array([0.0, 0.0])
        self.position = np.array([0.0, 0.0])
        self.acceleration = np.array([0.0, 0.0])

rotation = np.array( [(0, 1),(-1,0)])

def cathode(electron, voltage):
    electron.velocity[0] = -np.sqrt((2*electron.charge*voltage)/electron.mass)

def agg_vector(electron, current, k):
    Perpendicular = np.dot(rotation,electron.velocity)
    Acceleration = (electron.charge*-current*k*Perpendicular/electron.mass)
    return Acceleration

def motion(electron, current, k, timestep):
    electron.position += timestep*electron.velocity
    electron.velocity += timestep*agg_vector(electron, current, k)

#==============================================================================

def electron_path(voltage, current):
    test = Electron()
    cathode(test, voltage)
    position_x = []
    position_y = []
    while test.position[0] > -0.1 and test.position[1] > -0.04 and len(position_x) < 10000:
        motion(test, current, 4.231e-3, 0.00000000001)
        position_x.append(test.position[0])
        position_y.append(test.position[1])
    
    r = abs( round( (position_x[-1]**2+position_y[-1]**2)/(position_y[-1]*2), 2 ) )

    plt.figure()
    plt.plot(position_x, position_y, label = str(r)+'m radius')
    plt.ylim((-0.04,0.04))
    plt.xlim((-0.1,0))
    plt.title(str( round(voltage) )+'V cathode voltage with a '+str(current)+'A field')
    plt.xlabel('x(m)')
    plt.ylabel('y(m)')
    plt.legend(loc='upper right')
    plt.grid()
    
    #Bookeeping on the Server

    if not os.path.isdir('static'):
        os.mkdir('static')
    else:
        for filename in glob.glob(os.path.join('static','*png')):
            os.remove(filename)

    #save figure for display

    fig = os.path.join('static', str(time.time())+'.png')
    plt.savefig(fig)
    plt.close()
    return fig    

#===============================================================================

class InputForm(Form):
    Current = FloatField(label='(A)', default=0.2,
                validators=[validators.InputRequired()])
    Voltage = FloatField(label='(V)', default=4000,
                validators=[validators.InputRequired()])

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])

def index():
    
    form = InputForm(request.form)
    
    try: 
        int(form.Voltage.data)
        
        int(form.Current.data)

        if request.method == 'POST' and form.validate() and form.Voltage.data > 0:

            result = electron_path(form.Voltage.data, form.Current.data)

        else:

            result = None

        return render_template('pyWeb.html', form=form, result=result)

    except:

        result = None

        return render_template('pyWeb.html', form=form, result=result)

if __name__=='__main__':
    
    app.run(host='0.0.0.0', port= 8090)
