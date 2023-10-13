'''
NOTE-TO-SELF 29.09.23
Stream virker, men restarter ikke når kamera blir frakoblet.

NOTE-TO-SELF 06.10.23
Stream virker. Får til restart når vinduet lukkes, men ikke når server 
mister kontakt med kamera.

'''


import gi
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gst, GLib, Gtk
import threading
import time

# Initialize
Gst.init(None)


class CameraViewer:
    
    def __init__(self):
        
        self.init = True
        self.playing = False
        self.terminate = False
        self.restart = False
        
        self.pipeline = None    
        
        
    def _define_pipeline(self):
        """Generates a new pipeline using Gst Elements, instead of Pipeline Desccription
        
        Returns:
            Gst.Pipeline : pipeline
        """
        
        Gst.init(None)

        # Define elements
        source = Gst.ElementFactory.make("pylonsrc", "source")
        if not source:      
            print("ERROR: Could not create pylonsrc element.")
            return None 
        
        capsfilter = Gst.ElementFactory.make("capsfilter", "filter")
        if not capsfilter:  
            print("ERROR: Could not create capsfilter element.")
            return None

        convert = Gst.ElementFactory.make("autovideoconvert", "convert")
        if not convert:     
            print("ERROR: Could not create autovideoconvert element.")
            return None

        sink = Gst.ElementFactory.make("autovideosink", "sink")
        if not sink:        
            print("ERROR: Could not create autovideosink element.")
            return None
        

        # Set properties
        camera = Gst.ChildProxy.get_child_by_name(source, "cam")
        if not camera:      
            print("ERROR: Could not find camera child.")
            return None             
        camera.set_property("GevSCPSPacketSize", 8000)
        source.set_property("capture-error", "skip")
                
        caps = Gst.Caps.from_string("video/x-raw, framerate=60/1")
        capsfilter.set_property("caps", caps)
        
        
        # Create the pipeline and add the elements
        pipeline = Gst.Pipeline("pipeline")
        if not pipeline:
            print("ERROR: Could not create pipeline.")
            return None

        pipeline.add(source)
        pipeline.add(capsfilter)
        pipeline.add(convert)
        pipeline.add(sink)
        
        
        if not source.link(capsfilter):
            print("ERROR: Could not link pylonsrc to capsfilter.")
            return None

        if not capsfilter.link(convert):
            print("ERROR: Could not link capsfilter to convert.")
            return None

        if not convert.link(sink):
            print("ERROR: Could not link convert to sink.")
            return None
     
        return pipeline


    def _create_pipeline(self):
        """Generates a new pipeline using Pipeline Desccription
        
        Returns:
            Gst.Pipeline : pipeline or None if not able to parse
        """
        
        pipeline_desc = "pylonsrc cam::GevSCPSPacketSize=8000 capture-error=skip\
 ! video/x-raw, framerate=60/1\
 ! autovideoconvert\
 ! autovideosink"
                            
        print(f"Setting up pipeline: {pipeline_desc}")

        pipeline = Gst.parse_launch(pipeline_desc)     
        return pipeline    
            
            
    def run(self):
        """
        Main loop of the camera server
        """
        
        while not self.terminate:
            
            if self.init:
                print("Initalizing")
                self.pipeline = self._define_pipeline()
                ret = None              
                if self.pipeline:
                    ret = self.pipeline.set_state(Gst.State.PLAYING)
                while not self.pipeline or ret == Gst.StateChangeReturn.FAILURE:
                    print("Struggling to create pipeline")
                    time.sleep(3)
                    self.pipeline = self._define_pipeline()
                    if not self.pipeline:
                        continue
                    ret = self.pipeline.set_state(Gst.State.PLAYING)
                    
                               
                bus = self.pipeline.get_bus()
                
                               
                # Read message from bus
                message = bus.timed_pop_filtered(
                    Gst.CLOCK_TIME_NONE,
                    Gst.MessageType.ERROR | Gst.MessageType.EOS | Gst.MessageType.STATE_CHANGED)
                
                ret = self.handle_message(message)
                
                if not ret:
                    print("ERROR: Could not read message from bus.")
                    continue
                
                
                if ret == Gst.StateChangeReturn.FAILURE:
                    print("ERROR: Could not change state to PLAYING")
                    self.pipeline.set_state(Gst.State.NULL)
                    self.terminate = True  
                else: 
                    print("Succesfully changed state")
                    self.init = False
                    self.playing = True
                    bus = self.pipeline.get_bus()

            elif self.restart:
                ''' For testing '''
                self.terminate = True
                continue
                ''''            '''
                print ("Trying to restart pipeline")
                self.pipeline.set_state(Gst.State.READY)
                
                
                if not self.pipeline.set_state(Gst.State.NULL):
                    print("ERROR: Could not set state to NULL")
                
                self.pipeline = None
      
                print("Pipeline freed")
                self.init = True
                self.playing = False
                self.restart = False
                
                continue

            elif self.playing:              
                message = bus.timed_pop_filtered(
                    Gst.CLOCK_TIME_NONE, 
                    Gst.MessageType.ERROR | Gst.MessageType.EOS | Gst.MessageType.STATE_CHANGED
                )
                
                if not message:
                    continue
                
                try:
                    self.restart = not self.handle_message(message)
                except KeyboardInterrupt:
                    self.terminate = True
                except Exception as e:
                    print(f'[ERROR]: {e}')
        
        
        self.terminate = False
        self.restart = False
            
        # Stop the pipeline
        self.pipeline.set_state(Gst.State.NULL)
        self.pipeline = None
        print("Pipeline was stopped")
    

    def handle_message(self, message):
        message_type = message.type
        
        if message_type == Gst.MessageType.ERROR:
            err, debug_info = message.parse_error()
            print(f"[handle_message]Error: {err}\n {debug_info}")
            return False
            
        elif message_type == Gst.MessageType.EOS:
            print("[handle_message]End-Of-Stream reached")
            return False
            
        elif message_type == Gst.MessageType.STATE_CHANGED:
            if isinstance(message.src, Gst.Pipeline):
                old_state, new_state, pending_state = message.parse_state_changed()
                print(f"Pipeline state changed from {old_state.value_nick.upper()} to {new_state.value_nick.upper()}")

        return True
    
    
    def on_message(self, bus, message):
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
        
if __name__ == '__main__':
    try:
        counter = 0
        while True:
            counter += 1
            print(f"New viewer {counter}")
            viewer = CameraViewer()
            print(viewer)
            viewer.run()
            print(f"Viewer {counter} exited, restarting in 5 seconds")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Main loop stopped by ctrl+c")
        pass
            
