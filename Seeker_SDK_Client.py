__author__ = 'duguguang'

from SeekerV1 import *

preFrmNo = 0
curFrmNo = 0


# for test
def py_msg_func(iLogLevel, szLogMessage):
    szLevel = "None"
    if iLogLevel == 4:
        szLevel = "Debug"
    elif iLogLevel == 3:
        szLevel = "Info"
    elif iLogLevel == 2:
        szLevel = "Warning"
    elif iLogLevel == 1:
        szLevel = "Error"

    print("[%s] %s" % (szLevel, cast(szLogMessage, c_char_p).value))


def py_data_func(data):
    if data == None:
        print("Not get the data frame.\n")
        pass
    else:
        frameData = data.contents
        global preFrmNo, curFrmNo
        global x_at, y_at, z_at
        curFrmNo = frameData.iFrame
        if curFrmNo != preFrmNo:
            preFrmNo = curFrmNo
            print("FrameNo: %d " % (frameData.iFrame))
            print("nMarkerset = %d" % frameData.nBodies)

        for iBody in range(frameData.nBodies):
            pBody = pointer(frameData.BodyData[iBody])
            print("Markerset %d: %s" % (iBody + 1, pBody.contents.szName))

            # Markers
            print("\tnMarkers = %d\n" % pBody.contents.nMarkers)
            print("\t{\n")
            for i in range(pBody.contents.nMarkers):
                print("\t\tMarker %d：X:%f Y:%f Z:%f\n" % (
                    i + 1,
                    pBody.contents.Markers[i][0],
                    pBody.contents.Markers[i][1],
                    pBody.contents.Markers[i][2]))
                x_at = pBody.contents.Markers[i][0]
                y_at = pBody.contents.Markers[i][1]
                z_at = pBody.contents.Markers[i][2]
                b = pBody.contents.Markers[i][2]
            print("\t}\n")

            # Segments
            print("\tnSegments = %d\n" % pBody.contents.nSegments)
            print("\t{\n")
            for i in range(pBody.contents.nSegments):
                print("\t\tSegment %d：Tx:%lf Ty:%lf Tz:%lf Rx:%lf Ry:%lf Rz:%lf Length:%lf\n" %
                      (i + 1,
                       pBody.contents.Segments[i][0],
                       pBody.contents.Segments[i][1],
                       pBody.contents.Segments[i][2],
                       pBody.contents.Segments[i][3],
                       pBody.contents.Segments[i][4],
                       pBody.contents.Segments[i][5],
                       pBody.contents.Segments[i][6]))

            print("\t}\n")
            print("}\n")

        # Unidentified Markers
        print("nUnidentifiedMarkers = %d" % data.contents.nUnidentifiedMarkers)
        print("{\n")
        for i in range(data.contents.nUnidentifiedMarkers):
            print("\tUnidentifiedMarkers %d：X:%f Y:%f Z:%f\n" %
                  (i + 1,
                   data.contents.UnidentifiedMarkers[i][0],
                   data.contents.UnidentifiedMarkers[i][1],
                   data.contents.UnidentifiedMarkers[i][2]))

        print("}\n")

        Exit()
        return z_at


# 获取天线位置
def getATposi():
    x_at = 0
    y_at = 0
    z_at = 0
    b = 1

    data = GetCurrentFrame()
    while (data != None):
        try:
            data = GetCurrentFrame()
            frameData = data.contents
            # print(data)
            break
        except:
            print('null error')
    frameData = data.contents
    pBody = pointer(frameData.BodyData[0])
    while (pBody.contents.Markers[0][0] == 9999999.0):
        print('data.contents',data.contents)
        data = GetCurrentFrame()
        while (data != None):
            try:
                data = GetCurrentFrame()
                frameData = data.contents
                # print(data)
                break
            except:
                print('null error')
        frameData = data.contents
        pBody = pointer(frameData.BodyData[0])
    # frameData = data.fr
    frameData = data.contents
    # print(frameData)
    pBody = pointer(frameData.BodyData[0])

    x_at = pBody.contents.Markers[0][0]
    y_at = pBody.contents.Markers[0][1]
    z_at = pBody.contents.Markers[0][2]

    print('x', x_at, 'y', y_at, 'z', z_at)
    return x_at, y_at, z_at


# 获取一个点的位置，SDK中确定没有其他点
def getSinglePoint():
    data = GetCurrentFrame()
    print("nUnidentifiedMarkers = %d" % data.contents.nUnidentifiedMarkers)
    x = data.contents.UnidentifiedMarkers[0][0]
    y = data.contents.UnidentifiedMarkers[0][1]
    z = data.contents.UnidentifiedMarkers[0][2]

    print('x', x, 'y', y, 'z', z)
    return x, y, z


if __name__ == "__main__":
    print("Started the Seeker_SDK_Client Demo")

    print("VERSION:%s" % GetSdkVersion())

    SetVerbosityLevel(4)
    SetErrorMsgHandlerFunc(py_msg_func)

    # Change to your local ip in 10.1.1.0/24
    print("Begin to init the SDK Client")
    ret = Initialize(b"10.1.1.198", b"10.1.1.198")

    if ret == 0:
        print("Connect to the Seeker Succeed")
    else:
        print("Connect Failed: [%d]" % ret)
        Exit()
        exit(0)

    # hostInfo = GetHostInfo()
    # if hostInfo.bFoundHost == 1:
    #     print("Founded the Seeker Server")
    # else:
    #     print("Can't find the Seeker Server")
    #     exit(0)

    SetDataHandlerFunc(py_data_func)

    while (input("Press q to quit\n") != "q"):
        pass

    Exit()
