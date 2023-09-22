'''
NOTE-TO-SELF 29.09.23
Stream virker, men restarter ikke når kamera blir frakoblet
'''






import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, GLib, Gtk
import threading



class CameraViewer:
    def __init__(self):
        
        self.init = True
        self.playing = False
        self.terminate = False
        
        
        # Initialize
        Gst.init(None)
        
        self.pipeline = self._create_pipeline()


    def _create_pipeline(self):
        pipeline_desc = "pylonsrc cam::GevSCPSPacketSize=8000 capture-error=skip ! video/x-raw, framerate=60/1 ! autovideoconvert  ! autovideosink"
        print(f"Setting up pipeline: {pipeline_desc}")
        pipeline = Gst.parse_launch(pipeline_desc)
        
        ret = pipeline.set_state(Gst.State.PAUSED)
        if ret == Gst.StateChangeReturn.FAILURE:
            print("ERROR: Could not change state to PAUSED")
            
        return pipeline    
            
    def run(self):
        
        while not self.terminate:
            
            
            if self.init:
                if not self.pipeline:
                    self.pipeline = self._create_pipeline
            
                # Start the pipeline
                ret = self.pipeline.set_state(Gst.State.PLAYING)
                if ret == Gst.StateChangeReturn.FAILURE:
                    print("ERROR: Could not change state to PLAYING")
                    self.pipeline.set_state(Gst.State.NULL)
                    return  
                
                self.init = False
                self.playing = True

            elif self.playing:
                # Listen to the bus
                bus = self.pipeline.get_bus()

                # Loop
                restart = False
                if restart:
                    self.pipeline.set_state(Gst.State.NULL)
                    self.init = True
                    self.playing = False
                
                message = bus.timed_pop_filtered(
                    Gst.CLOCK_TIME_NONE, 
                    Gst.MessageType.ERROR | Gst.MessageType.EOS | Gst.MessageType.STATE_CHANGED
                )
                
                if not message:
                    continue
                
                try:
                    restart = not self.handle_message(message)
                except KeyboardInterrupt:
                    self.terminate = True
                except Exception as e:
                    print(f'[ERROR]: {e}')
            
            
            
        # Stop the pipeline
        self.pipeline.set_state(Gst.State.NULL)
        print("Pipeline was stopped")
        

    def handle_message(self, message):
        message_type = message.type
        
        if message_type == Gst.MessageType.ERROR:
            err, debug_info = message.parse_error()
            print("[on_message]Error: %s" % err, debug_info)
            return False
            
        elif message_type == Gst.MessageType.EOS:
            print("[on_message]End-Of-Stream reached")
            return False
            
        elif message_type == Gst.MessageType.STATE_CHANGED:
            if isinstance(message.src, Gst.Pipeline):
                old_state, new_state, pending_state = message.parse_state_changed()
                print(f"Pipeline state changed from {old_state.value_nick.upper()} to {new_state.value_nick.upper()}")

        return True
        
if __name__ == '__main__':
    viewer = CameraViewer()
    viewer.run()
