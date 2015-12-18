#!/usr/bin/env python
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import h5py
import os
import datetime

__version__ = "0.0.1"

REDUCTION_LOG = 'reduction_log'
THE_FUTURE = "2300-01-01T00:00"

shareddirlist = []
reduceloglist = []


class GenericFile(object):
    def __init__(self, path):
        self.filename = path
        self.timeCreation = None
        self.filesize = 0

        if self.filename is None:
            return
        if not os.path.exists(self.filename):
            return

        stat = os.stat(self.filename)
        self.timeCreation = datetime.datetime.fromtimestamp(stat.st_ctime)
        self.filesize = stat.st_size

    # called for bool(obj) in python 3.x
    def __bool__(self):
        if self.filename is None:
            return False
        if not os.path.exists(self.filename):
            return False
        return self.filesize > 0

    # called for bool(obj) in python 2.x
    def __nonzero__(self):
        return self.__bool__()

    def iso8601(self):
        if self.timeCreation is None:
            return ''
        else:
            return self.timeCreation.strftime("%Y-%m-%dT%H:%M")

    def filesizeMiB(self):
        return "%.f" % (float(self.filesize)/1024./1024.)

    def filesizehuman(self):
        if self.filesize < 1024:
            return "%dB" % (self.filesize)

        filesize_converted = float(self.filesize) / 1024.  # to kiB
        if filesize_converted < 1024.:
            return "%.1fkiB" % (filesize_converted)

        filesize_converted = float(filesize_converted) / 1024.  # to MiB
        if filesize_converted < 1024.:
            return "%.1fMiB" % (filesize_converted)

        filesize_converted = float(filesize_converted) / 1024.  # to GiB
        return "%.1fGiB" % (filesize_converted)


class ReductionLogFile(GenericFile):
    def __init__(self, logfullname, eventfilename):
        super(ReductionLogFile, self).__init__(logfullname)
        self.mantidVersion = "UNKNOWN"
        self.longestDuration = 0.
        self.longestAlgorithm = ""
        self.loadDurationTotal = 0.
        self.loadEventNexusDuration = 0.
        self.started = ''
        self.host = ''
        self.loadEventNexusDuration = 0.

        if not bool(self):  # something wrong with the log
            return

        self.__findMantidVersion()

        self.__findLongestDuration()
        self.longestDuration = "%.1f" % self.longestDuration
        # self.longestDuration = __class__.durationToHuman(self.longestDuration)

        self.__findLoadNexusTotal(eventfilename)
        self.loadEventNexusDuration = "%.1f" % self.loadEventNexusDuration

        self.__findLoadTotal()
        self.loadDurationTotal = "%.1f" % self.loadDurationTotal

    def durationToHuman(duration):
        (hours, minutes, seconds) = (0., 0., duration)
        if seconds > 60.:
            minutes = int(seconds / 60.)
            seconds = seconds % 60
            if minutes > 60:
                hours = int(minutes / 60)
                minutes = minutes % 60
        return "%dh%02dm%02ds" % (hours, minutes, int(seconds))

    def __findLoadNexusTotal(self, eventfilename):
        with open(self.filename, 'r') as handle:
            lookForDuration = False
            for line in handle:
                if "Load" in line and eventfilename in line:
                    lookForDuration = True
                elif lookForDuration and self.hasLogDuration(line):
                    (_, duration) \
                        = self.logDurationToNameAndSeconds(line)
                    if duration > 0.:
                        self.loadEventNexusDuration += duration
                    lookForDuration = False

    def __findLoadTotal(self):
        self.loadDurationTotal = 0.

        with open(self.filename, 'r') as handle:
            for line in handle:
                if not self.hasLogDuration(line):
                    continue
                if "Load" not in line:
                    continue
                line = line.strip()
                (_, duration) \
                    = self.logDurationToNameAndSeconds(line)
                self.loadDurationTotal += duration

    @staticmethod
    def hasLogDuration(line):
        if "Duration" not in line:
            return False
        if 'successful,' not in line:
            return False
        if "-1 seconds" in line:
            return False
        return True

    @staticmethod
    def logDurationToNameAndSeconds(line):
        (algorithm, duration) = line.split("successful,")
        algorithm = algorithm.split()[-1]
        duration = duration.split()[1:]

        if len(duration) == 2:  # only seconds
            duration = float(duration[0])
        elif len(duration) == 4:  # minutes and seconds
            duration = float(duration[0]) * 60. \
                       + float(duration[2])
        else:
            print(duration)
            raise RuntimeError("Don't know how to parse duration")
        return (algorithm, duration)

    def __findLongestDuration(self):
        self.longestDuration = 0.  # in seconds

        with open(self.filename, 'r') as handle:
            for line in handle:
                if self.hasLogDuration(line):
                    line = line.strip()
                    (algorithm, duration) \
                        = self.logDurationToNameAndSeconds(line)

                    if duration > self.longestDuration:
                        self.longestDuration = duration
                        self.longestAlgorithm = algorithm

    def __findMantidVersion(self):
        with open(self.filename, 'r') as handle:
            for line in handle:
                line = line.strip()
                if "This is Mantid version" in line:
                    self.mantidVersion = line.split("This is Mantid version")[-1]
                    self.mantidVersion = self.mantidVersion.strip().split()[0]
                if 'running on' in line and "starting" in line:
                    line = line.split('running on')[-1].strip()
                    (self.host, self.started) = line.split('starting')


class ARstatus:
    def __init__(self, direc, eventfile):

        self.eventfile = eventfile
        self.reduxfiles = [os.path.join(direc, name)
                           for name in shareddirlist
                           if eventfile.isThisRun(name)]

        logdir = os.path.join(direc, REDUCTION_LOG)
        logprefix = os.path.join(logdir, eventfile.shortname)

        self.logfiles = [os.path.join(logdir, filename)
                         for filename in reduceloglist
                         if filename.startswith(eventfile.shortname)]
        self.logfiles = [ReductionLogFile(filename, eventfile.shortname)
                         for filename in self.logfiles]

        # find longest running algorithm
        self.longestAlgorithm = ''
        self.longestDuration = 0.
        for logfile in self.logfiles:
            if logfile.longestDuration > self.longestDuration:
                self.longestAlgorithm = logfile.longestAlgorithm
                self.longestDuration = logfile.longestDuration

    @property
    def host(self):
        for logfile in self.logfiles:
            if len(logfile.host) > 0:
                return logfile.host
        return ''

    @property
    def mantidVersion(self):
        # collect possible mantid version
        choices = [logfile.mantidVersion for logfile in self.logfiles
                   if len(logfile.mantidVersion) > 0]
        # remove all of the unknowns
        choices = [choice for choice in choices
                   if choice != 'UNKNOWN']
        choices = set(choices)

        if len(choices) == 0:
            return 'UNKNOWN'
        elif len(choices) == 1:
            return choices.pop()
        else:
            raise RuntimeError("Too many mantid versions: " + str(choices))

    @staticmethod
    def findOldest(times):
        times = [time for time in times if len(time) > 0]
        if len(times) <= 0:
            return ''

        oldest=THE_FUTURE
        for time in times:
            if len(time) > 0 and time < oldest:
                oldest = time
        if oldest != THE_FUTURE:
            return oldest
        else:
            return ""


    @property
    def logstarted(self):
        times = [logfile.started for logfile in self.logfiles]
        return self.findOldest(times)

    @property
    def logiso8601(self):
        times = [logfile.iso8601() for logfile in self.logfiles]
        return self.findOldest(times)

    @property
    def loadDurationTotal(self):
        total = 0.
        for logfile in self.logfiles:
            total += float(logfile.loadDurationTotal)
        return total

    @property
    def loadEventNexusDuration(self):
        total = 0.
        for logfile in self.logfiles:
            total += float(logfile.loadEventNexusDuration)
        return total

    @staticmethod
    def header():
        return ("runID", "runStart", "runStop", "runCTime", "eventSizeMiB",
                "host", "numReduced", "version", "reduxStart",
                "logCTime", "longAlgo", "algoSec", "loadSecTotal", "loadNexusSecTotal")

    def report(self):
        return (str(self.eventfile),
                self.eventfile.timeStart, self.eventfile.timeStop,
                self.eventfile.iso8601(),
                self.eventfile.filesizeMiB(),
                self.host,
                str(len(self.reduxfiles)), self.mantidVersion,
                self.logstarted,
                self.logiso8601,
                self.longestAlgorithm, self.longestDuration,
                self.loadDurationTotal, self.loadEventNexusDuration)


class EventFile(GenericFile):
    def __init__(self, direc, filename):
        super(EventFile, self).__init__(os.path.join(direc, filename))
        self.shortname = filename
        self.prefix = filename.replace('.nxs.h5', '').replace('_event.nxs', '')

        with h5py.File(self.filename, 'r') as handle:
            entry = handle.get("entry")
            self.timeStart = entry.get("start_time").value[0].decode('utf-8')[:16]
            self.timeStop = entry.get("end_time").value[0].decode('utf-8')[:16]

    def __str__(self):
        return self.prefix

    def __repr__(self):
        return self.prefix

    def isThisRun(self, filename):
        return filename.startswith(self.prefix)

def getPropDir(descr):
    # if this points to a runfile, guess the proposal directory
    if os.path.isfile(descr):
        parts = [str(item) for item in descr.split('/')[:4]]
        fullpath = os.path.join('/', *parts)
    else:
        fullpath = descr

    # error check the result
    if not os.path.exists(fullpath):
        raise RuntimeError("%s does not exist" % fullpath)
    if not os.path.isdir(fullpath):
        raise RuntimeError("%s is not a directory" % fullpath)
    if not (fullpath.startswith("/SNS/") and ("IPTS" in fullpath)):
        raise RuntimeError("%s does not appear to be a proposal directory" % fullpath)

    return fullpath

def getRuns(propdir):
    # find the data directory
    datadirs = [os.path.join(propdir, subdir) for subdir in ['data', 'nexus']]
    datadirs = [direc for direc in datadirs if os.path.isdir(direc)]
    if len(datadirs) != 1:
        raise RuntimeError("Expected only one data directory, found " \
                           + ','.join(datadirs))

    # get a list of event files in that directory
    files = os.listdir(datadirs[0])
    files = [name for name in files if not name.endswith("_histo.nxs")]
    files = [EventFile(datadirs[0], name) for name in files]

    return files


def getOutFilename(propdir):
    (parent, prop) = os.path.split(propdir)
    (parten, inst) = os.path.split(parent)
    return "%s-%s.csv" % (inst, prop)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Report information on ' \
                                                 + 'auto-reduction in a proposal')
    # parser.add_argument('-p', '--propdir', metavar="IPTSDIR",
                        # help="proposal directory to report on")
    parser.add_argument('runfile', metavar="NEXUSFILE",
                        help="path to a nexus file, changes to append or proposal directory")
    parser.add_argument('outputdir',
                        help="directory to write csv to, " \
                             + "defaults to instrument shared")
    args = parser.parse_args()

    runfile = os.path.abspath(args.runfile)
    propdir = getPropDir(runfile)
    # one mode is to append a single run, the other is to parse an entire proposal
    if runfile == propdir:
        runfile = None

    print("Finding event nexus files in '%s'" % propdir)
    if runfile is not None:
        runs = [EventFile(*(os.path.split(runfile)))]
    else:
        runs = getRuns(propdir)
    reducedir = os.path.join(propdir, 'shared', 'autoreduce')
    shareddirlist = os.listdir(reducedir)
    reduceloglist = os.listdir(os.path.join(reducedir, REDUCTION_LOG))

    outfile = getOutFilename(propdir)
    outfile = os.path.join(args.outputdir, outfile)
    print("Writing results to '%s'" % outfile)
    total_runs = len(runs)
    total_reduced = 0
    if runfile is None or (not os.path.exists(outfile)):
        mode = 'w'
    else:
        mode = 'a'
    with open(outfile, mode) as handle:
        if mode == 'w':
            handle.write(','.join(ARstatus.header()) + "\n")
        for eventfile in runs:
            ar = ARstatus(reducedir, eventfile)
            report = [str(item) for item in ar.report()]
            if len(ar.reduxfiles) > 0:
                total_reduced += 1
            handle.write(','.join(report) + "\n")
    print("%d of %d files reduced" % (total_reduced, total_runs))
