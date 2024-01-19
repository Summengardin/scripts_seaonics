from pypylon import pylon
import cv2

def main():
    # Connecting to the first available camera
    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

    # Open the camera
    camera.Open()

    # Grabbing Continuously (video) with minimal delay
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly) 
    converter = pylon.ImageFormatConverter()

    # Converting to OpenCV bgr format
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    while camera.IsGrabbing():
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

        if grabResult.GrabSucceeded():
            # Access the image data
            image = converter.Convert(grabResult)
            img = image.GetArray()
            cv2.namedWindow('title', cv2.WINDOW_NORMAL)
            cv2.imshow('title', img)
            k = cv2.waitKey(1)
            if k == 27:  # Esc key to stop
                break
        grabResult.Release()

    # Releasing the resource    
    camera.StopGrabbing()
    camera.Close()

    cv2.destroyAllWindows()

def pylon_demo():
    from pypylon import pylon

    camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    camera.Open()

    # demonstrate some feature access
    new_width = camera.Width.Value - camera.Width.Inc
    if new_width >= camera.Width.Min:
        camera.Width.Value = new_width

    numberOfImagesToGrab = 100
    camera.StartGrabbingMax(numberOfImagesToGrab)

    while camera.IsGrabbing():
        grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
        print("GrabSucceeded: ", grabResult.GrabSucceeded())
        if grabResult.GrabSucceeded():
            # Access the image data.
            print("SizeX: ", grabResult.Width)
            print("SizeY: ", grabResult.Height)
            img = grabResult.Array
            print("Gray value of first pixel: ", img[0, 0])

        grabResult.Release()
    camera.Close()

if __name__ == '__main__':
    main()
    #pylon_demo()    