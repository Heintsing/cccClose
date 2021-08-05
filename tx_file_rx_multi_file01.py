import sys
import signal
import argparse
import uhd
import time
import numpy as np
import logging
import threading
import scipy.io as scio
import matplotlib.pyplot as plt

global logger
logger = logging.getLogger(__name__)
INIT_DELAY = 0.002  # 50mS initial delay before transmit
numm = 27
thread_start_delay_time = 0.005  # 时间对齐,留出发送指令和（第一次线程运行的0.01ms)
# time_now = 0 #usrp.get_time_now().get_real_secs()
data = []


def rx_multi_file(args, rx_streamer, md, stream_cmd, buffs, result, numm, timer_elapsed_event):
    # global time_now
    global INIT_DELAY
    start1 = time.time()
    if 1:
        global data
        # time_now = usrp.get_time_now().get_real_secs()
        # print('rx cmd--', time_now)
        # 耗时3ms，线程运行到此处最大需要11ms
        for i in range(numm + 1):
            stream_cmd.time_spec = uhd.types.TimeSpec(INIT_DELAY * (i + 1) + thread_start_delay_time)
            rx_streamer.issue_stream_cmd(stream_cmd)
        # time_now = usrp.get_time_now().get_real_secs()
        # print('rx cmd finish--', time_now)
        for i in range(numm):
            # print('rx-i-', i)
            # time_now = usrp.get_time_now().get_real_secs()
            # stream_cmd.time_spec = uhd.types.TimeSpec(time_now + INIT_DELAY) # uhd.types.TimeSpec(INIT_DELAY * (i+1))
            # stream_cmd.time_spec = uhd.types.TimeSpec(INIT_DELAY * (i+1)+thread_start_delay_time)
            # print('rx', usrp.get_time_now().get_real_secs())
            # print('rx--', time_now)
            # tells all channels to stream
            # time_now = usrp.get_time_now().get_real_secs()
            # print('rx--', time_now)
            # if i==0:
            #     time.sleep(0.01)
            # rx_streamer.issue_stream_cmd(stream_cmd)
            # if i==1:
            #     time_now = usrp.get_time_now().get_real_secs()
            #     print('rx--', time_now)

            # the first call to recv() will block this many seconds before receiving
            # number of accumulated samples
            num_acc_samps = 0
            num_rx_samps = np.array([], dtype=np.complex64)

            while num_acc_samps < args.total_num_samps:
                # receive a single packet
                num_rx_samps = rx_streamer.recv(buffs, md)
                # handle the error code
                if md.error_code == uhd.types.RXMetadataErrorCode.timeout:
                    break
                if md.error_code != uhd.types.RXMetadataErrorCode.none:
                    raise ValueError("Receiver error %s" % md.strerror())
                if num_rx_samps:
                    real_samps = min(args.total_num_samps - num_acc_samps, num_rx_samps)
                    result[:, num_acc_samps:num_acc_samps + real_samps] = buffs[:, 0:real_samps]
                    num_acc_samps += real_samps
            # print("Rx samples:", num_acc_samps)
            data.append(result.copy())
            if num_acc_samps < args.total_num_samps:
                print("Receive timeout before all samples received...")
        print("rx thread took %.3f sec." % (time.time() - start1))

        # data = np.array(data)
        # with open(args.output_file, 'wb') as out_file:
        #     if args.numpy:
        #         np.save(out_file, data, allow_pickle=False, fix_imports=False)
        #     else:
        #         data.tofile(out_file)


def tx_from_file(args, tx_streamer, mdtx, tx_buff, numm, timer_elapsed_event):
    # global time_now
    global INIT_DELAY
    start2 = time.time()
    if 1:
        # print("Tx time:", time.time())
        # timer_elapsed_event.wait()

        for i in range(numm):

            mdtx.start_of_burst = True
            mdtx.end_of_burst = True
            mdtx.has_time_spec = True
            mdtx.time_spec = uhd.types.TimeSpec(INIT_DELAY * (i + 1) + thread_start_delay_time)  # (time_now + INIT_DELAY)#

            # time_now = usrp.get_time_now().get_real_secs()
            # mdtx.time_spec = uhd.types.TimeSpec(time_now + INIT_DELAY)#
            # print('tx', usrp.get_time_now().get_real_secs())
            # print('tx', time_now)
            send_samps = 0
            # time_now = usrp.get_time_now().get_real_secs()
            # print('tx', time_now)
            while send_samps < args.total_num_samps:
                samples = tx_streamer.send(tx_buff, mdtx)
                send_samps += samples
                # mdtx.has_time_spec = False
                # mdtx.start_of_burst = False
            # print("Tx samples:", send_samps)
            # mdtx.end_of_burst = False
            tx_streamer.send(np.zeros((1, 0), dtype=np.complex64), mdtx)
    print("tx thread took %.3f sec." % (time.time() - start2))


def load_from_file(filename, samps_per_buff):
    data = scio.loadmat(filename)
    buff_t = data['LFMs']
    l_buff = len(buff_t.T)
    if l_buff != samps_per_buff:
        raise ValueError("The length of imported file does not match %f" % samps_per_buff)
    else:
        tx_buff = buff_t
    return tx_buff


stop_signal_called = False


def sig_int_handler(_sig, _frame):
    print("Caught Ctrl-C, exiting...")
    global stop_signal_called
    stop_signal_called = True


waveforms = {
    "sine": lambda n, tone_offset, rate: np.exp(n * 2j * np.pi * tone_offset / rate),
    "square": lambda n, tone_offset, rate: np.sign(waveforms["sine"](n, tone_offset, rate)),
    "const": lambda n, tone_offset, rate: 1 + 1j,
    "ramp": lambda n, tone_offset, rate:
    2 * (n * (tone_offset / rate) - np.floor(float(0.5 + n * (tone_offset / rate))))
}


def parse_args():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--args", default="addr=10.1.1.2",  # ip=192.168.10.3
                        help="USRP Dev56    0i1ce Args")
    parser.add_argument("-f", "--freq", type=float, default=2442000000,  # required=True,
                        help="Center Frequency")
    parser.add_argument("-r", "--rate", default=1e6, type=float, help="Sampling Rate")
    parser.add_argument("--total_num_samps", type=int, default=1000,
                        help="total number of samples to receive/transmit.")
    parser.add_argument("--tx_antenna", default='TX/RX', help="USRP TX Antenna")
    parser.add_argument("--rx_antenna", default='RX2', help="USRP RX Antenna")
    parser.add_argument("--tx_gain", type=int, default=10)
    parser.add_argument("--rx_gain", type=int, default=15)
    parser.add_argument("--rx_sync", type=str, default='now',
                        help="synchronization method: now, pps, mimo.")
    parser.add_argument("--tx_subdev", type=str, default='A:0',
                        help="subdev spec (homogeneous across motherboards).")
    parser.add_argument("--rx_subdev", type=str, default='A:0 B:0',
                        help="subdev spec (homogeneous across motherboards).")
    parser.add_argument("--tx_channel", default=0, nargs="+", type=int,
                        help="which channel(s) to use (specify \"0\", \"1\", \"0,1\", etc)")
    parser.add_argument("--rx_channel", default=[0, 1], nargs="+", type=int,
                        help="which channel(s) to use (specify \"0\", \"1\", \"0,1\", etc)")
    parser.add_argument("--tx_power", default=0, type=float,
                        help="Transmit power (if USRP supports it)")
    parser.add_argument("--ref", type=str, default='internal',
                        help="reference source (internal, external, mimo).")
    parser.add_argument("--bw", default=100000000, type=float,
                        help="analog frontend filter bandwidth in Hz")
    parser.add_argument("--wirefmt", type=str, default='sc16',
                        help="wire format (sc8 or sc16)")
    parser.add_argument("--cpu", type=str, default="fc32",
                        help="specify the host/cpu sample mode for TX")
    parser.add_argument("-o", "--output-file", type=str, default=r'C:\Users\admin\Desktop\CCC_laptop\Pycode\out.fc32')
    parser.add_argument("-n", "--numpy", default=False, action="store_true",
                        help="Save output file in NumPy format (default: No)")
    parser.add_argument("--seconds_in_future", type=float, default=1.5,
                        help="number of seconds in the future to receive.")
    parser.add_argument("--repeat", default=1, type=int,
                        help="repeatedly transmit file")
    parser.add_argument("--int_n", default=1, type=int,
                        help="tune USRP with integer-n tuning")
    parser.add_argument("--wave-freq", default=1e5, type=float)
    parser.add_argument("--wave-ampl", default=0.3, type=float)
    parser.add_argument(
        "-w", "--waveform", default="sine", choices=waveforms.keys(), type=str)
    return parser.parse_args()


args = parse_args()

if not (args.rate):
    logger.error("Please specify --rx_rate and/or --tx_rate")

#  create a usrp device
usrp = uhd.usrp.MultiUSRP(args.args)

# Always select the subdevice first, the channel mapping affects the other settings
if args.rx_subdev:
    usrp.set_rx_subdev_spec(uhd.usrp.SubdevSpec(args.rx_subdev))
if args.tx_subdev:
    usrp.set_tx_subdev_spec(uhd.usrp.SubdevSpec(args.tx_subdev))
logger.info("Using Device: %s", usrp.get_pp_string())

if args.tx_antenna:
    print("Setting TX antenna to `{}'...".format(args.tx_antenna), end='')
    usrp.set_tx_antenna(args.tx_antenna, args.tx_channel)
    print("OK")
if args.rx_antenna:
    print("Setting RX antenna to `{}'...".format(args.rx_antenna), end='')
    usrp.set_rx_antenna(args.rx_antenna, args.rx_channel[0])
    usrp.set_rx_antenna(args.rx_antenna, args.rx_channel[1])
    print("OK")

#  set the rx sample rate (sets across all channels)
print("Requesting rate of {} Msps...".format(args.rate / 1e6), end='')
usrp.set_rx_rate(args.rate, args.rx_channel[0])
usrp.set_rx_rate(args.rate, args.rx_channel[1])
usrp.set_tx_rate(args.rate)
if abs(usrp.get_rx_rate() - args.rate) > 1.0:
    print("ALMOST. Actual rx rate: {} Msps"
          .format(usrp.get_rx_rate() / 1e6))
else:
    print("RX OK")
if abs(usrp.get_tx_rate() - args.rate) > 1.0:
    print("ALMOST. Actual tx rate: {} Msps"
          .format(usrp.get_tx_rate() / 1e6))
else:
    print("TX OK")

# set the tf gain
usrp.set_tx_gain(args.tx_gain)
print("ALMOST. Actual tx gain: {} ".format(usrp.get_tx_gain()))
usrp.set_rx_gain(args.rx_gain, args.rx_channel[0])
usrp.set_rx_gain(args.rx_gain, args.rx_channel[1])
print("ALMOST. Actual rx gain: {} ".format(usrp.get_rx_gain()))

# print("Requesting TX frequency of {} MHz...".format(args.freq / 1e6), end='')
tx_tune_request = uhd.types.TuneRequest(args.freq)
# if args.int_n:
#     tx_tune_request.args = uhd.types.DeviceAddr("mode_n=integer")
# usrp.set_tx_freq(tx_tune_request, args.tx_channel)
# if abs(usrp.get_tx_freq() - args.freq) > 1.0:
#     print("ALMOST. Actual frequency: {} MHz".format(usrp.get_tx_freq() / 1e6))
# else:
#     print("OK")

print("Requesting RX frequency of {} MHz...".format(args.freq / 1e6), end='')
rx_tune_request = uhd.types.TuneRequest(args.freq)
# Align LOs in the front-end (SBX, UBX)
# This timed-tuning ensures that the phase offsets between VCO/PLL chains will remain constant after each re-tune
# Phase synchronization with the UBX
cmd_time = usrp.get_time_now() + uhd.types.TimeSpec(0.1)
usrp.set_command_time(cmd_time)
usrp.set_rx_freq(rx_tune_request, args.rx_channel[0])
usrp.set_rx_freq(rx_tune_request, args.rx_channel[1])
usrp.set_tx_freq(tx_tune_request, args.tx_channel)
usrp.clear_command_time()
if abs(usrp.get_rx_freq() - args.freq) > 1.0:
    print("ALMOST. Actual frequency: {} MHz".format(usrp.get_rx_freq() / 1e6))
else:
    print("OK")

#  set the analog frontend filter bandwidth
print("Requesting TX bandwidth of {} Msps...".format(args.bw / 1e6), end='')
usrp.set_tx_bandwidth(args.bw, args.tx_channel)
if abs(usrp.get_tx_bandwidth() - args.bw) > 1.0:
    print("ALMOST. Actual bandwidth: {} Msps"
          .format(usrp.get_tx_bandwidth() / 1e6))
else:
    print("OK")

# allow for some setup time:
time.sleep(1)

# Setup the reference clock
# usrp.set_clock_source(args.ref)

# Check Ref and LO Lock detect
sensor_names = usrp.get_tx_sensor_names(0)
if sensor_names == 'lo_locked':
    lo_locked = usrp.get_tx_sensor("lo_locked", 0)
    logger.info("Checking TX: %s", lo_locked.to_pp_string())
sensor_names = usrp.get_mboard_sensor_names(0)
if (args.ref == "mimo") and (sensor_names == 'mimo_locked'):
    mimo_locked = usrp.get_mboard_sensor("mimo_locked", 0)
    logger.info("Checking TX: %s", mimo_locked.to_pp_string())
if (args.ref == "external") and (sensor_names == 'ref_locked'):
    ref_locked = usrp.get_mboard_sensor("ref_locked", 0)
    logger.info("Checking TX: %s", ref_locked.to_pp_string())

print("Setting device timestamp to 0...")
if args.rx_sync == "now":
    # This is not a true time lock, the devices will be off by a few RTT.
    # Rather, this is just to allow for demonstration of the code below.
    usrp.set_time_now(uhd.types.TimeSpec(0.0))
elif args.rx_sync == "pps":
    usrp.set_time_source("external")
    usrp.set_time_unknown_pps(uhd.types.TimeSpec(0))
    time.sleep(1)
    # wait for pps sync pulse
elif args.rx_sync == "mimo":
    # uhd.UHD_ASSERT_THROW(usrp.get_num_mboards() == 2)
    # make mboard 1 a slave over the MIMO Cable
    usrp.set_clock_source("mimo", 1)
    usrp.set_time_source("mimo", 1)
    # set time on the master (mboard 0)
    usrp.set_time_now(uhd.types.TimeSpec(0), 0)
    # sleep a bit while the slave locks its time to the master
    time.sleep(0.1)
print("Are the times across all motherboards synchronized: ", usrp.get_time_synchronized())

filename = r'C:\Users\admin\Desktop\CCC_laptop\Pycode\LFMs1000.mat'
tx_buff = load_from_file(filename, args.total_num_samps)

# tx_buff = np.array(
#         list(map(lambda n: args.wave_ampl * waveforms[args.waveform](n, args.wave_freq, args.rate),
#             np.arange(
#                 int(10 * np.floor(args.rate / args.wave_freq)),
#                 dtype=np.complex64))),
#         dtype=np.complex64)  # One period
# proto_len = tx_buff .shape[-1]
# if proto_len < args.total_num_samps:
#     tx_buff = np.tile(tx_buff, (1, int(np.ceil(float(args.total_num_samps) / proto_len))))

if args.rate:
    # create a receive streamer
    # linearly map channels (index0 = channel0, index1 = channel1, ...)
    # Return an RX streamer with fc64 output
    stream_args = uhd.usrp.StreamArgs(args.cpu, args.wirefmt)
    stream_args.channels = args.rx_channel
    rx_streamer = usrp.get_rx_stream(stream_args)
    # meta-data will be filled in by recv()
    md = uhd.types.RXMetadata()

    # setup streaming
    stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.num_more)
    stream_cmd.num_samps = args.total_num_samps
    stream_cmd.stream_now = False
    # stream_cmd.time_spec = uhd.types.TimeSpec(usrp.get_time_now().get_real_secs() + INIT_DELAY)
    # # tells all channels to stream
    # rx_streamer.issue_stream_cmd(stream_cmd)

    # allocate buffers to receive with samples (one buffer per channel)
    # samps_per_buff = rx_streamer.get_max_num_samps()
    buffs = np.zeros((len(args.rx_channel), args.total_num_samps), dtype=np.complex64)
    result = np.empty((len(args.rx_channel), args.total_num_samps), dtype=np.complex64)

    stream_args = uhd.usrp.StreamArgs(args.cpu, args.wirefmt)
    stream_args.channels = [args.tx_channel]
    tx_streamer = usrp.get_tx_stream(stream_args)
    mdtx = uhd.types.TXMetadata()
    # mdtx.start_of_burst = True
    # mdtx.end_of_burst = False
    # mdtx.has_time_spec = True
    # mdtx.time_spec = uhd.types.TimeSpec(usrp.get_time_now().get_real_secs() + INIT_DELAY)

    # for i in range(3):
    # Make a signal for the threads to stop running
    quit_event = threading.Event()
    quit_event.clear()

    # --------------------------------------- 单次收发
    # threads = []
    # rx_thread = threading.Thread(target=rx_multi_file,
    #                          args=(args, rx_streamer, md, stream_cmd, buffs, result, numm, quit_event))
    # threads.append(rx_thread)
    # # 主线程在其他非守护线程运行完毕后才算运行完毕(守护线程在此时就被回收)
    # rx_thread.setDaemon(True) # 设置子线程为守护线程时
    #
    # # rx_thread.setName("rx_stream")
    #
    # tx_thread = threading.Thread(target=tx_from_file,
    #                              args=(args, tx_streamer, mdtx, tx_buff, numm, quit_event))
    # threads.append(tx_thread)
    # tx_thread.setDaemon(True) # 主线程执行完自己的任务以后，子进程立刻退出
    #
    # rx_thread.start()
    # tx_thread.start()
    #
    #
    # # tx_thread.setName("tx_stream")
    # # quit_event.set() # 本意是用来使进程结束
    #
    # # Interrupt and join the threads
    # logger.debug("Sending signal to stop!")
    # for thr in threads: # 等一个子线程运行完了才继续执行此线程（主线程）
    #     thr.join()  # 即主线程任务结束之后，进入阻塞状态，一直等待其他的子线程执行结束之后，主线程在终止 https://www.cnblogs.com/cnkai/p/7504980.html

    # --------------------------------------- 多线程循环
    num_showtime = 8
    threads = []
    for i_thread in range(0, num_showtime):  # 等一个子线程运行完了才继续执行此线程（主线程）
        rx_thread = threading.Thread(target=rx_multi_file, args=(args, rx_streamer, md, stream_cmd, buffs, result, numm, quit_event))
        rx_thread.setDaemon(True)  # 设置子线程为守护线程时
        threads.append(rx_thread)

        tx_thread = threading.Thread(target=tx_from_file, args=(args, tx_streamer, mdtx, tx_buff, numm, quit_event))
        threads.append(tx_thread)
        tx_thread.setDaemon(True)  # 主线程执行完自己的任务以后，子进程立刻退出
    delay = 0
    data_200 = np.ones([200, 2, 1000], dtype=complex)
    data_2002 = []
    start_echo = time.time()
    for i_thread in range(0, num_showtime):  # 等一个子线程运行完了才继续执行此线程（主线程）
        usrp.set_time_now(uhd.types.TimeSpec(0.0))
        print('echo ', i_thread)
        threads[i_thread * 2].start()
        threads[i_thread * 2 + 1].start()
        threads[i_thread * 2].join()
        threads[i_thread * 2 + 1].join()
        data_np = np.array(data)
        data_200[25 * (i_thread % 4):25 * (i_thread % 4 + 1), :, :] = data_np[2:27, :, :]
        if i_thread % 4 == 0 and i_thread != 0:
            print(data_200.shape)
            print("200_echo took %.3f sec." % (time.time() - start_echo))
            start_echo = time.time()
        # time.sleep(1)

    # logger.debug("Sending signal to stop!")
    # for thr in threads: # 等一个子线程运行完了才继续执行此线程（主线程）
    #     thr.join()  # 即主线程任务结束之后，进入阻塞状态，一直等待其他的子线程执行结束之后，主线程在终止 https://www.cnblogs.com/cnkai/p/7504980.html

    # tx_threadd = threading.Thread(target=tx_from_file,
    #                              args=(args, tx_streamer, mdtx, tx_buff, numm, quit_event))
    # threads.append(tx_threadd)
    # tx_threadd.setDaemon(True)  # 主线程执行完自己的任务以后，子进程立刻退出
    # tx_threadd.start()
    # tx_threadd.join()

##############
# for i in range(1,100):
#     print(usrp.get_time_now().get_real_secs())
