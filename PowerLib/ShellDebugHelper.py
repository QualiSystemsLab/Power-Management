# import inspect
import functools
import pickle
import pprint

# NOTE: You will need to add C:\Program Files (x86)\QualiSystems\TestShell\ExecutionServer\QsPythonDriverHost as a 'content root'
# Pycharm: File->Settings->Your Project->Project Structure

pickle_dir = 'C:/Quali/pickles/'


def record(func):
    # sig = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func_call = (func.__name__, args, kwargs)
        pickle.dump(func_call, open("C:/Quali/pickles/Debugging.pkl", "ab"))

        return func(*args, **kwargs)

    return wrapper


def show_recording(pickle_file="C:/Quali/pickles/Debugging.pkl"):
    with open(pickle_file, "rb") as f:
        while 1:
            try:
                val = pickle.load(f)
                pprint.pprint(val)
            except (EOFError, pickle.UnpicklingError):
                break
    return


def playback(pickle_file = "C:/Quali/pickles/Debugging.pkl"):
    with open(pickle_file, "rb") as f:
        while 1:
            try:
                (func, args, kwargs) = pickle.load(f)
                obj = args[0]
                val = args[1:]
                getattr(obj, func)(*args[1:], **kwargs)
                # pprint.pprint(val)
            except (EOFError, pickle.UnpicklingError):
                break
    return