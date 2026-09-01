import cv2
import depthai as dai

with dai.Pipeline() as pipeline:
    rgb = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_A)

    rgb_output = rgb.requestOutput(
        (1280, 720),
        type=dai.ImgFrame.Type.BGR888p,
    )

    rgb_queue = rgb_output.createOutputQueue()
    left = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_B)
    right = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_C)

    left_output = left.requestOutput(
        (640, 400),
        type=dai.ImgFrame.Type.GRAY8,
    )

    right_output = right.requestOutput(
        (640, 400),
        type=dai.ImgFrame.Type.GRAY8,
    )

    left_queue = left_output.createOutputQueue()
    right_queue = right_output.createOutputQueue()

    stereo = pipeline.create(dai.node.StereoDepth)

    left_output.link(stereo.left)
    right_output.link(stereo.right)

    depth_queue = stereo.depth.createOutputQueue()

    print("Starting OAK-D...")
    pipeline.start()

    print("Streaming.")
    print("Press Q or ESC to quit.")

    while pipeline.isRunning():
        rgb_frame = rgb_queue.get()
        rgb_image = rgb_frame.getCvFrame()

        depth_frame = depth_queue.get()
        depth = depth_frame.getFrame()

        depth_vis = cv2.normalize(
            depth,
            None,
            0,
            255,
            cv2.NORM_MINMAX,
            dtype=cv2.CV_8U,
        )

        depth_color = cv2.applyColorMap(
            depth_vis,
            cv2.COLORMAP_JET,
        )

        left_frame = left_queue.get()
        left_image = left_frame.getCvFrame()

        cv2.imshow("OAK-D RGB", rgb_image)
        cv2.imshow("OAK-D Stereo Depth", depth_color)
        cv2.imshow("OAK-D Left", left_image)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q") or key == 27:
            break

    pipeline.stop()

cv2.destroyAllWindows()
