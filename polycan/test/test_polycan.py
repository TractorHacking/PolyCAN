from transform import transform
from extract import extract
import matplotlib.pyplot as plt
from pkg_resources import resource_filename

def test_full_log(list_signals, filter=None):
    path  = resource_filename(__name__, 'start1.csv')
    with extract.CSVFileExtractor(path) as e:
        print(e)
        signals = e.extract()
        print("hi")
        data = transform.decode_j1939(signals)
        print("hi")
        print(data)
        if list_signals:
            for s in set(data['SP Label']):
                if filter:
                    if filter in s:
                        print(s)
                else:
                    print(s)
        engine_speed = data[data['SP Label'] == 'Engine Speed']
        engine_torque = data[data['SP Label'] == 'Actual Engine - Percent Torque']
        engine_oil = data[data['SP Label'] == 'Engine Oil Pressure 1']
        engine_temp = data[data['SP Label'] == 'Engine Temperature 1']
        print(len(engine_speed), len(engine_torque), len(engine_oil), len(engine_temp))
        fig, ax = plt.subplots(4)  # Create a figure containing a single axes.
        fig.tight_layout()
        ax[0].set_title("Engine Speed")
        ax[0].set_ylabel("RPM")
        ax[0].plot(engine_speed['time'].to_numpy(dtype=float),
                engine_speed['data'].to_numpy(dtype=float) * 0.125)  # Plot some data on the axes.
        ax[1].set_title("Actual Engine - Percent Torque")
        ax[1].set_ylabel("%")
        ax[1].plot(engine_torque['time'].to_numpy(dtype=float),
                engine_torque['data'].to_numpy(dtype=float) - 125.0)
        ax[2].set_title("Engine Oil Pressure")
        ax[2].set_ylabel("kPa")
        ax[2].plot(engine_oil['time'].to_numpy(dtype=float),
                engine_oil['data'].to_numpy(dtype=float) * 4)
        ax[3].set_title("Engine Temperature")
        ax[3].set_ylabel("°C")
        ax[3].plot(engine_temp['time'].to_numpy(dtype=float),
                engine_temp['data'].to_numpy(dtype=float) * 0.03125 - 273)
        plt.show()

if __name__ == "__main__":
    test_full_log(list_signals=True, filter="Temperature")
