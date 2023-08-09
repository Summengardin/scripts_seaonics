# Installing gst-shark
To install gst-shark, just run the [setup script](./setup.sh)

# Using gst-shark

To use gst-shark run the gst commands with the following environment variables

GST_DEBUG="GST_TRACER:7" GST_TRACERS="<Metric>"

## Example:

> GST_DEBUG="GST_TRACER:7" GST_TRACERS="cpuusage" gst-launch-1.0 videotestsrc ! autovideoconvert ! autovideosink

## Metrics
For the complete list look at [the ridgerun wiki](https://developer.ridgerun.com/wiki/index.php/GstShark_-_Tracers)
* graphic
* cpuusage
* framerate
* proctime
* scheduletime
* interlatency

## Plotting traces
> cd gst-shark/scripts/graphics
> ./gstshark-plot <Path to log output dir>
