from typing import Dict

class PipelineConfig:
    def __init__(self, config: Dict):
        self.source = self.parse_source(config.get('source'))
        self.device = self.parse_device(config.get('device'))
        self.inference = self.parse_inference(config.get('inference'))
        self.protocol = self.parse_protocol(config.get('protocol'))
        self.width = self.parse_width(config.get('width'))
        self.height = self.parse_height(config.get('height'))

    def parse_source(self, source: str or None):
        if source is None or source == 'test':
            return 'test'
        elif source == 'v4l2' or source == 'basler':
            return source
        raise Exception(f"Unknown source {source}")

    def parse_device(self, device: str or None):
        if self.source == 'test':
            return None
        if self.source == 'v4l2' and device is None:
            return "/dev/video0"
        return device
    
    def parse_inference(self, inference: str or None):
        return None

    def parse_protocol(self, protocol: str or None):
        return "RTSP"

    def parse_width(self, width: str or None):
        if width is None:
            width = '1280'
        return str(width)

    def parse_height(self, height: str or None):
        if height is None:
            height = '720'
        return str(height)

    def __str__(self):
        return f"source: {self.source}\ndevice: {self.device}\nresolution: {self.width}x{self.height}\nprotocol: {self.protocol}\ninference: {self.inference}\n"


class PipelineBuilder:
    def __format_basler_device_string(device: str):
        if device is None:
            return ''
        return f"device-serial-number={device} "

    def build(config: PipelineConfig):
        source = PipelineBuilder.__format_source(config)
        sink = PipelineBuilder.__format_sink(config)

        return source + sink


    def __format_source(config: PipelineConfig):
        if config.source == 'test':
            return f"videotestsrc ! video/x-raw, width={config.width}, height={config.height} ! nvvidconv ! "
        elif config.source == 'v4l2':
            return f"v4l2src device={config.device} ! nvv4l2decoder mjpeg=1 enable-max-performance=true disable-dpb=true ! nvvidconv ! video/x-raw(memory:NVMM), width={config.width}, height={config.height} ! "
        elif config.source == 'basler':
            return f"pylonsrc {PipelineBuilder.__format_basler_device_string(config.device)}! video/x-raw, width={config.width}, height={config.height}, format=(string)YUY2, framerate=60/1 ! nvvidconv ! "
        
    def __format_sink(config: PipelineConfig):
        if config.protocol == 'RTSP':
            return "nvv4l2h264enc ! rtph264pay pt=96 name=pay0"


if __name__ == '__main__':
    config = PipelineConfig({'source': 'basler'})
    print(config)    
    pipeline = PipelineBuilder.build(config)
    print(pipeline)
