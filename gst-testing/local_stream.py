'''
This script will start a pipeline and show the camerastream in window on the current computer
'''

import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib

from threading import Thread
from time import sleep

class CameraStream:

    def __init__(self):

        self.loop = GLib.MainLoop()        
        self.pipeline = self._generate_pipeline()
        
                   
    def run(self):

        self.loop_thread = Thread(target=self.loop.run)
        self.loop_thread.start()

                
        while True:
            sleep(0.1)
            try:
                if not self.pipeline:
                    self.pipeline = self._generate_pipeline
                else:
                    print(self.pipeline.get_state(0))
                                                            
            except KeyboardInterrupt:
                break
            except BrokenPipeError:
                print("Broken Pipeline")
                pass
            except Exception as e:
                print("Unknown error: ", e)
                pass
            
        
    def __del__(self):
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
            
        self.loop.quit()
        self.loop_thread.join()
        

    def _generate_pipeline(self):
            
        Gst.init(None)
        pipeline = Gst.parse_launch("pylonsrc ! video/x-raw, framerate=60/1 ! autovideoconvert ! autovideosink")
        
        pipeline.set_state(Gst.State.PAUSED)

        return pipeline
        
        
if __name__ == '__main__':
    stream = CameraStream()
    stream.run()
    