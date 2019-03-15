# import inspect
import functools
import pickle
import pprint
# import gc
import sys
import os

# NOTE: You will need to add C:\Program Files (x86)\QualiSystems\TestShell\ExecutionServer\QsPythonDriverHost as a 'content root'
# Pycharm: File->Settings->Your Project->Project Structure

pickle_dir = 'C:/Quali/pickles/'


def record(func):
    """
    Wrapper for functions to record the calls (as called by CloudShell) useful for situations where re-creating the specific context would be difficult.

    Simply:
    import this file
    add @wrapper above your existing functions
    upload your code to CloudShell
    Perform the required task
    Run/Debug the 'show_recording' and/or 'playback' functions from your code
    Example:

        if __name__ == "__main__":
            show_recording(PowerService)
            playback(PowerService)
            pass

    :param func:
    :return:
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        caller = sys._getframe(1).f_code.co_name
        if caller != 'playback':  # Don't double pickle
            class_name = type(args[0]).__name__
            func_call = (func.__name__, args, kwargs)
            pickle.dump(func_call, open(os.path.join(pickle_dir, class_name + ".pkl"), "ab"))

        return func(*args, **kwargs)

    return wrapper


def show_recording(class_obj=None, pickle_file=None):
    """
    prints the contents of the recording. Must specify either class_obj or

    :param class_obj: The class object to determine the filename from
    :param str pickle_file: The specific file to display from
    :return:
    """
    if class_obj is not None:
        pickle_file = os.path.join(pickle_dir, class_obj.__name__ + ".pkl")
    if pickle_file is None:
        raise ValueError("Either class_obj or pickle_file must be specified")
    with open(pickle_file, "rb") as f:
        while 1:
            try:
                val = pickle.load(f)
                pprint.pprint(val)
            except (EOFError, pickle.UnpicklingError):
                break
    return


def playback(class_obj=None, pickle_file=None):
    """
    Plays back a pickle function recording

    :param class_obj: The class object to determine the filename from
    :param str pickle_file: The specific file to playback from
    :return:
    """
    if class_obj is not None:
        pickle_file = os.path.join(pickle_dir, class_obj.__name__ + ".pkl")
    if pickle_file is None:
        raise ValueError("Either class_obj or pickle_file must be specified")
    with open(pickle_file, "rb") as f:
        while 1:
            try:
                (func, args, kwargs) = pickle.load(f)
                obj = args[0]
                getattr(obj, func)(*args[1:], **kwargs)
            except (EOFError, pickle.UnpicklingError):
                break
    return
