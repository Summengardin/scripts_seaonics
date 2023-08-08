# Using gst-shark

To use gst-shark run the gst commands with the following environment variables

GST_DEBUG="GST_TRACER:7" GST_TRACERS="<Metric>"

## Example:

> GST_DEBUG="GST_TRACER:7" GST_TRACERS="cpuusage" gst-launch-1.0 videotestsrc ! autovideoconvert ! autovideosink

## Metrics
* cpuusage
* framerate
* proctime
* scheduletime
* interlatency