#!/usr/bin/env python3
#
# Copyright 2020 Ettus Research, a National Instruments Brand
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
"""
Use a calibrated USRP as a power meter
"""

import sys
import signal
import argparse
import uhd


def parse_args():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--args", default="",  # ip=192.168.10.3
                        help="USRP Device Args")
    parser.add_argument("-f", "--freq", type=float, default=2442000000,  # required=True,
                        help="Center Frequency")
    parser.add_argument("-o", "--lo-offset", type=float, default=0.0,
                        help="Optional LO offset")
    parser.add_argument("-c", "--channel", type=int, default=[0,1],
                        help="USRP RX Channel Index")
    parser.add_argument("-t", "--antenna", default='RX2',  #'TX/RX',
                        help="USRP RX Antenna")
    parser.add_argument("-r", "--rate", default=1e6, type=float,
                        help="Sampling Rate")
    parser.add_argument("-b", "--bandwidth", type=float,
                        help="Analog filter bandwidth (if supported)")
    parser.add_argument("-l", "--ref-level", type=float, default=-15,
                        help="RX reference power level. "
                             "This should be higher than the expected power.")
    parser.add_argument("-n", "--samps-per-est", type=float, default=1e3,
                        help="Samples per estimate.")
    parser.add_argument("--mode", choices=['one-shot', 'continuous'], default='continuous',
                        help="Measure once, or keep measuring until Ctrl-C is pressed.")
    return parser.parse_args()


def get_streamer(usrp, chan):
    """
    Return an RX streamer with fc32 output
    """
    stream_args = uhd.usrp.StreamArgs('fc32', 'sc16')
    stream_args.channels = [chan]
    return usrp.get_rx_stream(stream_args)


def setup_device(usrp, args):
    """
    Apply the settings from args to the device
    """
    chan = args.channel[0]
    # if chan > usrp.get_rx_num_channels():
    #     print("ERROR: Invalid channel selected: {} (only {} channels available!)"
    #           .format(chan, usrp.get_rx_num_channels()))
    #     raise RuntimeError("Invalid channel selected")
    # print("Using channel: {}".format(chan))

    if args.antenna:
        print("Setting RX antenna to `{}'...".format(args.antenna), end='')
        usrp.set_rx_antenna(args.antenna, chan)
        print("OK")

    # if not usrp.has_rx_power_reference(chan):
    #     antenna = usrp.get_rx_antenna()
    #     print("ERROR: This device is not calibrated for RX at RF%d-%s!" % (chan, antenna))
    #     raise RuntimeError("Device not calibrated for selected antenna")

    print("Requesting RX rate of {} Msps...".format(args.rate / 1e6), end='')
    usrp.set_rx_rate(args.rate, chan)
    if abs(usrp.get_rx_rate(chan) - args.rate) > 1.0:
        print("ALMOST. Actual rate: {} Msps"
              .format(usrp.get_rx_rate(chan) / 1e6))
    else:
        print("OK")

    print("Requesting RX frequency of {} MHz...".format(args.freq / 1e6), end='')
    tr = uhd.types.TuneRequest(args.freq, args.lo_offset)
    usrp.set_rx_freq(tr, chan)
    if abs(usrp.get_rx_freq(chan) - args.freq) > 1.0:
        print("ALMOST. Actual frequency: {} MHz".format(usrp.get_rx_freq(chan) / 1e6))
    else:
        print("OK")

    print("Requesting RX power reference level of {:.2f} dBm..."
          .format(args.ref_level), end='')
    # usrp.set_rx_power_reference(args.ref_level, chan)
    # # ref_level = usrp.get_rx_power_reference(chan)
    # if abs(ref_level - args.ref_level) > 1.0:
    #     print("ALMOST. Actual ref level: {:.2f} dBm".format(ref_level))
    # else:
    #     print("OK")

    if args.bandwidth:
        print("Requesting analog RX bandwidth of {} Msps..."
              .format(args.bandwidth), end='')
        usrp.set_rx_bandwidth(args.bandwidth, chan)
        if abs(usrp.get_rx_bandwidth(chan) - args.bandwidth) > 1.0:
            print("ALMOST. Actual bandwidth: {} MHz"
                  .format(usrp.get_rx_bandwidth(chan) / 1e6))
        else:
            print("OK")
    ref_level = 0
    return (chan, ref_level)


def setup_device2(usrp, args):
    """
    Apply the settings from args to the device
    """
    chan = args.channel[0]
    # if chan > usrp.get_rx_num_channels():
    #     print("ERROR: Invalid channel selected: {} (only {} channels available!)"
    #           .format(chan, usrp.get_rx_num_channels()))
    #     raise RuntimeError("Invalid channel selected")
    # print("Using channel: {}".format(chan))

    if args.antenna:
        print("Setting RX antenna to `{}'...".format(args.antenna), end='')
        usrp.set_rx_antenna(args.antenna, chan)
        print("OK")

    # if not usrp.has_rx_power_reference(chan):
    #     antenna = usrp.get_rx_antenna()
    #     print("ERROR: This device is not calibrated for RX at RF%d-%s!" % (chan, antenna))
    #     raise RuntimeError("Device not calibrated for selected antenna")

    print("Requesting RX rate of {} Msps...".format(args.rate / 1e6), end='')
    usrp.set_rx_rate(args.rate, chan)
    if abs(usrp.get_rx_rate(chan) - args.rate) > 1.0:
        print("ALMOST. Actual rate: {} Msps"
              .format(usrp.get_rx_rate(chan) / 1e6))
    else:
        print("OK")

    print("Requesting RX frequency of {} MHz...".format(args.freq / 1e6), end='')
    tr = uhd.types.TuneRequest(args.freq, args.lo_offset)
    usrp.set_rx_freq(tr, chan)
    if abs(usrp.get_rx_freq(chan) - args.freq) > 1.0:
        print("ALMOST. Actual frequency: {} MHz".format(usrp.get_rx_freq(chan) / 1e6))
    else:
        print("OK")

    print("Requesting RX power reference level of {:.2f} dBm..."
          .format(args.ref_level), end='')
    # usrp.set_rx_power_reference(args.ref_level, chan)
    # # ref_level = usrp.get_rx_power_reference(chan)
    # if abs(ref_level - args.ref_level) > 1.0:
    #     print("ALMOST. Actual ref level: {:.2f} dBm".format(ref_level))
    # else:
    #     print("OK")

    if args.bandwidth:
        print("Requesting analog RX bandwidth of {} Msps..."
              .format(args.bandwidth), end='')
        usrp.set_rx_bandwidth(args.bandwidth, chan)
        if abs(usrp.get_rx_bandwidth(chan) - args.bandwidth) > 1.0:
            print("ALMOST. Actual bandwidth: {} MHz"
                  .format(usrp.get_rx_bandwidth(chan) / 1e6))
        else:
            print("OK")
    ref_level = 0
    return (chan, ref_level)


RUN = True


def handle_sigint(_sig, _frame):
    print("Caught Ctrl-C, exiting...")
    global RUN
    RUN = False


def SetUsrp():
    args = argparse.Namespace()
    args.args = 'ip=192.168.10.2'
    args.freq = 2442000000
    args.lo_offset = 0.0
    args.channel = [0,1]
    args.antenna =  'TX/RX'#'RX2'
    args.bandwidth = None
    args.ref_level = -15
    args.samps_per_est = 1000
    args.mode = 'continuous'
    args.rate = 1000000

    usrp = uhd.usrp.MultiUSRP(args.args)
    uhd.usrp.SubdevSpec("A:0 B:1")
    (chan, ref_level) = setup_device(usrp, args)
    streamer = get_streamer(usrp, args.channel[0])

    signal.signal(signal.SIGINT, handle_sigint)
    return usrp, streamer, args, chan


def GetPower(streamer, args, chan):
    try:
        power_dbfs = uhd.dsp.signals.get_usrp_power(streamer, num_samps=int(args.samps_per_est), chan=chan)
    except RuntimeError:
        print('USRP fail')
    # This is a hack b/c the signal handler is not gracefully handling
    # SIGINT

    power_dbm = power_dbfs + -15
    # print("Received power: {:+6.2f} dBm".format(power_dbm))

    return power_dbm



def main():
    """
    gogogo
    """
    args = parse_args()
    print(args)
    usrp = uhd.usrp.MultiUSRP(args.args)
    uhd.usrp.SubdevSpec("A:0 B:1")
    (chan, ref_level) = setup_device(usrp, args)
    setup_device2(usrp, args)

    streamer = get_streamer(usrp, args.channel[1])
    if args.mode == 'continuous':
        def handle_sigint(_sig, _frame):
            print("Caught Ctrl-C, exiting...")
            global RUN
            RUN = False

        signal.signal(signal.SIGINT, handle_sigint)
    while RUN:
        try:
            power_dbfs = uhd.dsp.signals.get_usrp_power(
                streamer, num_samps=int(args.samps_per_est), chan=chan)
        except RuntimeError:
            # This is a hack b/c the signal handler is not gracefully handling
            # SIGINT
            break
        power_dbm = power_dbfs + ref_level
        print("Received power: {:+6.2f} dBm".format(power_dbm))
        if args.mode == 'one-shot':
            break
    return True


if __name__ == "__main__":
    sys.exit(not main())
