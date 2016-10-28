import re
from collections import deque

from silences import Silence

class ClanFileParser:

    def __init__(self, input_path, output_path):
        self.clan_file = input_path
        self.export_clan_file = output_path

        self.silences_inserted = False
        self.overlaps_inserted = False

    def insert_silences(self, silences):

        # we initialize a queue of silences using the
        # list passed as argument to this function. We don't
        # use the list itself because we need queue behavior (i.e. pop)
        silence_queue = deque(silences)

        # open the export clan file
        output = open(self.export_clan_file, "w")

        with open(self.clan_file, "rU") as file:

            # declare the two time interval arrays we're going to
            # be filling as we iterate through every line of the file
            previous_clan_interval = [None, None]
            current_clan_interval = [None, None]

            # regex object to parse out the timestamp
            # interval from each line
            interval_regx = re.compile("(\d+_\d+)")

            # pop the first silence off the queue
            if silence_queue:
                curr_silence = silence_queue.popleft()

            #initialize the start/end written flags
            start_written = False
            end_written = False

            # We iterate over the clan file line by line
            for index, raw_line in enumerate(file):
                # get rid of preceding and trailing whitespace from the line
                line = raw_line.strip()

                # We only write comments after lines with " *XYZ: " prefixes.
                # The check for curr_silence ensures that there is still a
                # silence waiting to be written
                if line.startswith("*") and curr_silence:
                    # parse out the part of the line with the interval in it
                    interval_string = interval_regx.search(line).group()
                    # tokenize that string into an array of 2 strings ["123", "456"]
                    interval = interval_string.split("_")

                    # assign the integer representation of that interval to
                    # the current_clan_interval array. This keeps track of the
                    # timepoints we're currently dealing with as we iterate
                    # over the file
                    current_clan_interval[0] = int(interval[0])
                    current_clan_interval[1] = int(interval[1])

                    # We check to make sure that in interval ABC_XYZ,
                    # XYZ is strictly > ABC. If not we print warning to
                    # GUI and raise exception, halting the clan file processing
                    if current_clan_interval[1] < current_clan_interval[0]:
                        raise Exception("timestamp interval is malformed: {}_{}".format(interval[0],
                                                                                        interval[1]))

                    # If the currently queued silence starts before the
                    # end of the current clan interval, and start silence has
                    # not been written, we...
                    if curr_silence.start <= current_clan_interval[1]\
                            and not start_written:

                        # alter the ending timestamp to correspond to the beginning
                        # of the silence, and write the new line to the output file
                        output.write(line.replace(interval_string,
                                                  str(current_clan_interval[0]) + "_" +\
                                                  str(int(curr_silence.start))) + "\n")

                        # insert the comment immediately after the altered clan entry
                        output.write("%com:\tsilence {} of {} starts at {} -- previous timestamp adjusted: was {}\n"
                                     .format(curr_silence.number,
                                             len(silences),
                                             curr_silence.start,
                                             current_clan_interval[1]))

                        start_written = True
                        end_written = False

                        # stop progressing though the conditions and
                        # head to next line in the file
                        continue

                    # If the end of the currently queued silence is less than
                    # the end of the current clan time interval...
                    if curr_silence.end <= current_clan_interval[1]\
                            and start_written\
                            and not end_written:

                        # We first alter the clan time interval to match the end of the
                        # silence we are about to insert, and write it to the output file

                        output.write(line.replace(interval_string,
                                                  str(current_clan_interval[0]) + "_" +\
                                                  str(int(curr_silence.end))) + "\n")

                        # then we write the end silence comment right afterwards
                        output.write("%com:\tsilence {} of {} ends at {} -- previous timestamp adjusted: was {}\n"
                                     .format(curr_silence.number,
                                             len(silences),
                                             curr_silence.end,
                                             current_clan_interval[1]))

                        end_written = True
                        start_written = False

                        # make sure queue contains items
                        # and pop the next silence off of it
                        if silence_queue:
                            curr_silence = silence_queue.popleft()
                        else:
                            # if silence_queue is empty, we set curr_silence to None
                            # so that the top level check fails
                            # (if line.startswith("*") and curr_silence:)
                            # this ensures that after all the silences have been handled,
                            # we just write all subsequent lines to output without any
                            # further processing
                            curr_silence = None
                        continue

                # this is a check for a special case. If we've reached @End,
                # but the end of a silence has not been written, we insert that
                # last end-silence comment in before writing out the @End line
                if line.startswith("@End") and not end_written:

                    output.write("%com:\tsilence {} of {} ends at {} -- previous timestamp adjusted: was {}\n"
                                     .format(curr_silence.number,
                                             len(silences),
                                             curr_silence.end,
                                             current_clan_interval[1]))
                    output.write(line)

                else:
                    # if the line is not a bulleted time interval, we just
                    # write it straight to the output file without processing.
                    # This includes %com's and other meta information
                    output.write(line + "\n")

        output.close()

    def insert_silences_cha(self, silences):

        # we initialize a queue of silences using the
        # list passed as argument to this function. We don't
        # use the list itself because we need queue behavior (i.e. pop)
        silence_queue = deque(silences)

        # open the export clan file
        output = open(self.export_clan_file, "w")

        with open(self.clan_file, "rU") as file:

            # declare the two time interval arrays we're going to
            # be filling as we iterate through every line of the file
            previous_clan_interval = [None, None]
            current_clan_interval = [None, None]

            # regex object to parse out the timestamp
            # interval from each line
            interval_regx = re.compile("(\025\d+_\d+)")

            # pop the first silence off the queue
            if silence_queue:
                curr_silence = silence_queue.popleft()
            else:
                curr_silence = None
            #initialize the start/end written flags
            start_written = False
            end_written = False

            last_line = ""

            silence_1000_replaced = False

            # We iterate over the clan file line by line
            for index, line in enumerate(file):
                # # get rid of preceding and trailing whitespace from the line
                # line = raw_line.strip()
                #
                # We only write comments after lines with " *XYZ: " prefixes.
                # The check for curr_silence ensures that there is still a
                # silence waiting to be written
                if line.startswith("*") and curr_silence:
                    # parse out the part of the line with the interval in it
                    interval_reg_result = interval_regx.search(line)

                    if interval_reg_result is None:
                        last_line = line
                        continue

                    # rearrange previous and current intervals
                    previous_clan_interval[0] = current_clan_interval[0]
                    previous_clan_interval[1] = current_clan_interval[1]

                    interval_string = interval_reg_result.group().replace("\025", "")

                    # tokenize that string into an array of 2 strings ["123", "456"]
                    interval = interval_string.split("_")

                    # assign the integer representation of that interval to
                    # the current_clan_interval array. This keeps track of the
                    # timepoints we're currently dealing with as we iterate
                    # over the file
                    current_clan_interval[0] = int(interval[0])
                    current_clan_interval[1] = int(interval[1])

                    if curr_silence.start == 1000:
                        #curr_silence.start = 1000 # avoid 0 millisecond. start at 1000 millisecond.
                        #print "made silence interval 1000 adjustment"
                        #print "silence 1000 index: " + str(index)
                        silence_1000_replaced = True

                    # We check to make sure that in interval ABC_XYZ,
                    # XYZ is strictly > ABC. If not we print warning to
                    # GUI and raise exception, halting the clan file processing
                    if current_clan_interval[1] < current_clan_interval[0]:
                        raise Exception("timestamp interval is malformed: {}_{}".format(interval[0],
                                                                                        interval[1]))

                    # If the currently queued silence starts before the
                    # end of the current clan interval, and start silence has
                    # not been written, we...
                    if curr_silence.start <= current_clan_interval[1]\
                            and not start_written:

                        # alter the ending timestamp to correspond to the beginning
                        # of the silence, and write the new line to the output file

                        # if "." is not in the line, then we're about to write a
                        # comment inside a multi-line entry. In this case, we need
                        # to insert this missing period so that CHECK doesn't fail.
                        if "." not in line:
                            new_line = line.replace("\025" + interval_string + "\025",
                                                    ". \025{}_{}\025".format(current_clan_interval[0],
                                                                             int(curr_silence.start)))
                            output.write(new_line)

                        else:
                            output.write(line.replace(interval_string, "{}_{}".format(current_clan_interval[0],
                                                                                      int(curr_silence.start))))

                        if silence_1000_replaced:
                            output.write("%xcom:\tsilence comment rewrote interval to 0_1, rewriting to 0_1000\n")
                            silence_1000_replaced = False   # reset flag

                        # insert the comment immediately after the altered clan entry
                        output.write("%xcom:\tsilence {} of {} starts at {} -- previous timestamp adjusted: was {}\n"
                                     .format(curr_silence.number,
                                             len(silences),
                                             curr_silence.start,
                                             current_clan_interval[1]))

                        start_written = True
                        end_written = False

                        # stop progressing though the conditions and
                        # head to next line in the file
                        continue

                    # If the end of the currently queued silence is less than
                    # the end of the current clan time interval...
                    if curr_silence.end <= current_clan_interval[1]\
                            and start_written\
                            and not end_written:

                        # We first alter the clan time interval to match the end of the
                        # silence we are about to insert, and write it to the output file

                        # if "." is not in the line, then we're about to write a
                        # comment inside a multi-line entry. In this case, we need
                        # to insert this missing period so that CHECK doesn't fail.
                        if "." not in line:
                            new_line = line.replace("\025" + interval_string + "\025",
                                                    ". \025{}_{}\025".format(current_clan_interval[0],
                                                                             int(curr_silence.end)))
                            output.write(new_line)

                        else:
                            output.write(line.replace(interval_string, "{}_{}".format(current_clan_interval[0],
                                                                                      int(curr_silence.end))))

                        # then we write the end silence comment right afterwards
                        output.write("%xcom:\tsilence {} of {} ends at {} -- previous timestamp adjusted: was {}\n"
                                     .format(curr_silence.number,
                                             len(silences),
                                             curr_silence.end,
                                             current_clan_interval[1]))

                        end_written = True
                        start_written = False

                        # make sure queue contains items
                        # and pop the next silence off of it
                        if silence_queue:
                            curr_silence = silence_queue.popleft()
                        else:
                            # if silence_queue is empty, we set curr_silence to None
                            # so that the top level check fails
                            # (if line.startswith("*") and curr_silence:)
                            # this ensures that after all the silences have been handled,
                            # we just write all subsequent lines to output without any
                            # further processing
                            curr_silence = None
                        continue

                if line.startswith("\t"):
                    # if there are no more silences to be added, just write
                    # out the line and continue to the next line
                    if not curr_silence:
                        output.write(line)
                        continue
                    # parse out the part of the line with the interval in it
                    interval_reg_result = interval_regx.search(line)

                    # if there's no bulleted timestamp on this line,
                    # print out the original line and continue to the next one
                    if interval_reg_result is None:
                        output.write(line)
                        last_line = line
                        continue

                    # rearrange previous and current intervals
                    previous_clan_interval[0] = current_clan_interval[0]
                    previous_clan_interval[1] = current_clan_interval[1]

                    interval_string = interval_reg_result.group().replace("\025", "")

                    # tokenize that string into an array of 2 strings ["123", "456"]
                    interval = interval_string.split("_")

                    # assign the integer representation of that interval to
                    # the current_clan_interval array. This keeps track of the
                    # timepoints we're currently dealing with as we iterate
                    # over the file
                    current_clan_interval[0] = int(interval[0])
                    current_clan_interval[1] = int(interval[1])

                    # If the currently queued silence starts before the
                    # end of the current clan interval, and start silence has
                    # not been written, we...
                    if curr_silence.start <= current_clan_interval[1]\
                            and not start_written:

                        # alter the ending timestamp to correspond to the beginning
                        # of the silence, and write the new line to the output file

                        # if "." is not in the line, then we're about to write a
                        # comment inside a multi-line entry. In this case, we need
                        # to insert this missing period so that CHECK doesn't fail.
                        if "." not in line:
                            new_line = line.replace("\025" + interval_string + "\025",
                                                    ". \025{}_{}\025".format(current_clan_interval[0],
                                                                             int(curr_silence.start)))
                            output.write(new_line)

                        else:
                            output.write(line.replace(interval_string, "{}_{}".format(current_clan_interval[0],
                                                                                      int(curr_silence.start))))


                        # insert the comment immediately after the altered clan entry
                        output.write("%xcom:\tsilence {} of {} starts at {} -- previous timestamp adjusted: was {}\n"
                                     .format(curr_silence.number,
                                             len(silences),
                                             curr_silence.start,
                                             current_clan_interval[1]))

                        start_written = True
                        end_written = False

                        # stop progressing though the conditions and
                        # head to next line in the file
                        continue

                    # If the end of the currently queued silence is less than
                    # the end of the current clan time interval...
                    if curr_silence.end <= current_clan_interval[1]\
                            and start_written\
                            and not end_written:

                        # We first alter the clan time interval to match the end of the
                        # silence we are about to insert, and write it to the output file

                        # if "." is not in the line, then we're about to write a
                        # comment inside a multi-line entry. In this case, we need
                        # to insert this missing period so that CHECK doesn't fail.
                        if "." not in line:
                            new_line = line.replace("\025" + interval_string + "\025",
                                                    ". \025{}_{}\025".format(current_clan_interval[0],
                                                                             int(curr_silence.end)))
                            output.write(new_line)

                        else:
                            output.write(line.replace(interval_string, "{}_{}".format(current_clan_interval[0],
                                                                                      int(curr_silence.end))))

                        # then we write the end silence comment right afterwards
                        output.write("%xcom:\tsilence {} of {} ends at {} -- previous timestamp adjusted: was {}\n"
                                     .format(curr_silence.number,
                                             len(silences),
                                             curr_silence.end,
                                             current_clan_interval[1]))

                        end_written = True
                        start_written = False

                        # make sure queue contains items
                        # and pop the next silence off of it
                        if silence_queue:
                            curr_silence = silence_queue.popleft()
                        else:
                            # if silence_queue is empty, we set curr_silence to None
                            # so that the top level check fails
                            # (if line.startswith("*") and curr_silence:)
                            # this ensures that after all the silences have been handled,
                            # we just write all subsequent lines to output without any
                            # further processing
                            curr_silence = None
                        continue

                # this is a check for a special case. If we've reached @End,
                # but the end of a silence has not been written, we insert that
                # last end-silence comment in before writing out the @End line
                if line.startswith("@End") and not end_written and (curr_silence is not None):

                    output.write("%xcom:\tsilence {} of {} ends at {} -- previous timestamp adjusted: was {}\n"
                                     .format(curr_silence.number,
                                             len(silences),
                                             curr_silence.end,
                                             current_clan_interval[1]))
                    output.write(line)

                else:
                    # if the line is not a bulleted time interval, we just
                    # write it straight to the output file without processing.
                    # This includes %com's and other meta information
                    output.write(line)

        output.close()

    def insert_overlaps(self, region_values, region_map, silences):
        """

        :param region_values:
        :param region_map: map of offsets to averages
        :param silences: list of silent regions parsed earlier
        :return:
        """
        region_number = 1

        # open the export clan file
        output = open(self.export_clan_file, "w")

        lowest_region = region_values[len(region_values) - 1]
        offset_list = region_values # this is a list of interval offsets

        # for index, x in enumerate(region_values):
        #     for key, value in region_map.items():
        #         if value == x:
        #             offset_list.append(key)
        sorted_offsets = sorted(offset_list)

        # we initialize a queue of regions using the
        # list built from the region_map lookup. We don't
        # use the list itself because we need queue behavior (i.e. pop)
        # We also build a queue for the silence regions
        region_queue = deque(sorted_offsets)
        silence_queue = deque(silences)

        # print "region values: " + str(region_values)
        # print "sorted_offsets: " + str(sorted_offsets)
        # print "region queue: " + str(region_queue)

        with open(self.clan_file, "rU") as file:

            # declare the two time interval arrays we're going to
            # be filling as we iterate through every line of the file
            previous_clan_interval = [None, None]
            current_clan_interval = [None, None]

            # regex object to parse out the timestamp
            # interval from each line
            interval_regx = re.compile("(\d+_\d+)")

            # pop the first silence and region off the queue
            curr_region = region_queue.popleft()
            curr_region_start = curr_region * 5 * 60 * 1000 # convert to milliseconds
            curr_region_end   = curr_region_start + 60 * 60 * 1000 # end is 1 hour from start
            if silence_queue:
                curr_silence = silence_queue.popleft()

            # print "curr_region: " + str(curr_region)
            # print "curr_region_start: " + str(curr_region_start)
            # print "curr_region_end: " + str(curr_region_end)

            # initialize the start/end written flags
            start_written = False
            end_written = False

            # initialize the silence/subregion overlap flags
            region_start_in_silence = False
            region_end_in_silence = False
            region_contains_silence = False

            # initialize the global silence/subregion overlap flag
            silence_overlapped = False

            # We iterate over the clan file line by line
            for index, raw_line in enumerate(file):
                # get rid of leading and trailing whitespace from the line
                line = raw_line.strip()

                # We only write comments after lines with " *XYZ: " prefixes.
                # The check for curr_silence ensures that there is still a
                # silence waiting to be written
                if line.startswith("*") and (curr_region is not None):
                    # parse out the part of the line with the interval in it
                    interval_string = interval_regx.search(line).group()
                    # tokenize that string into an array of 2 strings ["123", "456"]
                    interval = interval_string.split("_")

                    # assign the integer representation of that interval to
                    # the current_clan_interval array. This keeps track of the
                    # timepoints we're currently dealing with as we iterate
                    # over the file
                    current_clan_interval[0] = int(interval[0])
                    current_clan_interval[1] = int(interval[1])

                    #print "clan[0]: " + str(current_clan_interval[0]) + "clan[1]: " + str(current_clan_interval[1]) + "    curr_region_start: " + str(curr_region_start)

                    # Handle special case for 0 offset
                    if curr_region_start == 0:
                        curr_region_start = 1 # avoid 0 millisecond. start at 1 millisecond.
                    # We check to make sure that in interval ABC_XYZ,
                    # XYZ is strictly > ABC. If not we print warning to
                    # GUI and raise exception, halting the clan file processing
                    # if current_clan_interval[1] < current_clan_interval[0]:
                    #     print "\n\n***************************************************************************"
                    #     print "timestamp interval is malformed: {}_{}:   CLAN file line# {}"\
                    #         .format(interval[0],
                    #                 interval[1],
                    #                 index)
                    #     print "***************************************************************************\n"

                    if (curr_region_start > curr_silence.start) and\
                            (curr_region_start < curr_silence.end):
                        region_start_in_silence = True
                    else:
                        region_start_in_silence = False

                    if (curr_region_end < curr_silence.end) and\
                            (curr_region_end > curr_silence.start):
                        region_end_in_silence = True
                    else:
                        region_end_in_silence = False

                    if (curr_region_start < curr_silence.start) and\
                            (curr_region_end > curr_silence.end):
                        region_contains_silence = True
                    else:
                        region_contains_silence = False

                    # If the currently queued silence starts before the
                    # end of the current clan interval, and start silence has
                    # not been written, we...
                    if (curr_region_start <= current_clan_interval[1])\
                            and (not start_written):
                        if region_start_in_silence or region_end_in_silence or region_contains_silence:
                            #print "region_start_in_silence: " + str(region_start_in_silence) + "     region_end_in_silence: " + str(region_end_in_silence) + "     region_contains_silence: " + str(region_contains_silence)
                            # alter the ending timestamp to correspond to the beginning
                            # of the subregion, and write the new line to the output file
                            output.write(line.replace(interval_string,
                                                      str(current_clan_interval[0]) + "_" + \
                                                      str(int(curr_region_start))) + "\n")
                            if (curr_region == lowest_region):
                                output.write("%com:\tsubregion {} of {} starts at {} -- previous timestamp adjusted: was {} - lowest ranked region; [contains silent region: [{}, {}] ]\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        curr_region_start,
                                                        current_clan_interval[1],
                                                        curr_silence.start,
                                                        curr_silence.end))
                            else:
                                # insert the comment immediately after the altered clan entry
                                output.write("%com:\tsubregion {} of {} starts at {} -- previous timestamp adjusted: was {} [contains silent region: [{}, {}] ]\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        curr_region_start,
                                                        current_clan_interval[1],
                                                        curr_silence.start,
                                                        curr_silence.end))

                            start_written = True
                            end_written = False
                            silence_overlapped = True

                            # stop progressing though the conditions and
                            # head to next line in the file
                            continue
                        else:
                            #print "region_start_in_silence: " + str(region_start_in_silence) + "     region_end_in_silence: " + str(region_end_in_silence) + "     region_contains_silence: " + str(region_contains_silence)
                            # alter the ending timestamp to correspond to the beginning
                            # of the silence, and write the new line to the output file
                            output.write(line.replace(interval_string,
                                                      str(current_clan_interval[0]) + "_" +\
                                                      str(int(curr_region_start))) + "\n")

                            if (curr_region == lowest_region):
                                output.write("%com:\tsubregion {} of {} starts at {} -- previous timestamp adjusted: was {}. lowest ranked region; skip unless necessary\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        curr_region_start,
                                                        current_clan_interval[1]))
                            else:
                                # insert the comment immediately after the altered clan entry
                                output.write("%com:\tsubregion {} of {} starts at {} -- previous timestamp adjusted: was {}\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        curr_region_start,
                                                        current_clan_interval[1]))

                            start_written = True
                            end_written = False

                            # stop progressing though the conditions and
                            # head to next line in the file
                            continue

                    # If the end of the currently queued subregion is less than
                    # the end of the current clan time interval...
                    if (curr_region_end <= current_clan_interval[1])\
                            and start_written\
                            and (not end_written):
                        #print "inside the end writing section"
                        if region_start_in_silence or region_end_in_silence or region_contains_silence:
                            #print "region_start_in_silence: " + str(region_start_in_silence) + "     region_end_in_silence: " + str(region_end_in_silence) + "     region_contains_silence: " + str(region_contains_silence)
                            # We first alter the clan time interval to match the end of the
                            # subregion we are about to insert, and write it to the output file
                            output.write(line.replace(interval_string,
                                                      str(current_clan_interval[0]) + "_" + \
                                                      str(int(curr_region_end))) + "\n")

                            if curr_region == lowest_region:
                                output.write("%com:\tsubregion {} of {} ends at {} -- previous timestamp adjusted: was {} - lowest ranked region; [contains silent region: [{}, {}] ]\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        curr_region_end,
                                                        current_clan_interval[1],
                                                        curr_silence.start,
                                                        curr_silence.end))

                            else:
                                # then we write the end subregion comment right afterwards
                                output.write("%com:\tsubregion {} of {} ends at {} -- previous timestamp adjusted: was {} [contains silent region: [{}, {}] ]\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        curr_region_end,
                                                        current_clan_interval[1],
                                                        curr_silence.start,
                                                        curr_silence.end))

                            end_written = True
                            start_written = False
                            silence_overlapped = True

                            #region_start_in_silence = False
                            #region_end_in_silence = False

                            # make sure queue contains items
                            # and pop the next silence off of it
                            if region_queue:
                                curr_region = region_queue.popleft()
                                #print "curr_region: " + str(curr_region)
                                curr_region_start = curr_region * 5 * 60 * 1000 # convert to milliseconds
                                curr_region_end   = curr_region_start + 60 * 60 * 1000 # end is 1 hour from start
                                #print "curr_region_start: " + str(curr_region_start)
                                #print "curr_region_end: " + str(curr_region_end)
                                region_number = region_number + 1
                            else:
                                # if region_queue is empty, we set curr_region to None
                                # so that the top level check fails
                                # (if line.startswith("*") and curr_silence:)
                                # this ensures that after all the subregions have been handled,
                                # we just write all subsequent lines to output without any
                                # further processing
                                curr_region = None
                            continue
                        else:
                            #print "region_start_in_silence: " + str(region_start_in_silence) + "     region_end_in_silence: " + str(region_end_in_silence) + "     region_contains_silence: " + str(region_contains_silence)
                            # We first alter the clan time interval to match the end of the
                            # silence we are about to insert, and write it to the output file
                            output.write(line.replace(interval_string,
                                                      str(current_clan_interval[0]) + "_" +\
                                                      str(int(curr_region_end))) + "\n")

                            if (curr_region == lowest_region):
                                output.write("%com:\tsubregion {} of {} ends at {} -- previous timestamp adjusted: was {}. lowest ranked region; skip unless necessary\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        curr_region_end,
                                                        current_clan_interval[1]))
                            else:
                                # then we write the end subbregion comment right afterwards
                                output.write("%com:\tsubregion {} of {} ends at {} -- previous timestamp adjusted: was {}\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        curr_region_end,
                                                        current_clan_interval[1]))

                            end_written = True
                            start_written = False



                            # make sure queue contains items
                            # and pop the next subregion off of it
                            if region_queue:
                                curr_region = region_queue.popleft()
                                curr_region_start = curr_region * 5 * 60 * 1000 # convert to milliseconds
                                curr_region_end   = curr_region_start + 60 * 60 * 1000 # end is 1 hour from start
                                region_number = region_number + 1
                            else:
                                # if silence_queue is empty, we set curr_silence to None
                                # so that the top level check fails
                                # (if line.startswith("*") and curr_silence:)
                                # this ensures that after all the silences have been handled,
                                # we just write all subsequent lines to output without any
                                # further processing
                                curr_region = None
                            continue

                if current_clan_interval[1] >= curr_silence.end and silence_queue:
                    #print "queue pre-pop: " + str(silence_queue)
                    curr_silence = silence_queue.popleft()
                # this is a check for a special case. If we've reached @End,
                # but the end of a silence has not been written, we insert that
                # last end-silence comment in before writing out the @End line
                if line.startswith("@End") and not end_written:

                    output.write("%com:\tsubregion {} of {} ends at {} -- previous timestamp adjusted: was {}\n"
                                     .format(region_number,
                                             len(region_values),
                                             curr_region_end,
                                             current_clan_interval[1]))
                    output.write(line)
                    region_number = region_number + 1

                else:
                    # if the line is not a bulleted time interval, we just
                    # write it straight to the output file without processing.
                    # This includes %com's and other meta information
                    output.write(line + "\n")

        output.close()
        self.find_interval_errors()

    def insert_overlaps_cha(self, region_values, region_map, silences):
        """

        :param region_values:
        :param region_map: map of offsets to averages
        :param silences: list of silent regions parsed earlier
        :return:
        """
        region_number = 1

        # open the export clan file
        output = open(self.export_clan_file, "w")

        lowest_region = region_values[-1]

        offset_list = region_values # this is a list of interval offsets

        # for index, x in enumerate(region_values):
        #     for key, value in region_map.items():
        #         if value == x:
        #             offset_list.append(key)
        sorted_offsets = sorted(offset_list)

        # we initialize a queue of regions using the
        # list built from the region_map lookup. We don't
        # use the list itself because we need queue behavior (i.e. pop)
        # We also build a queue for the silence regions
        region_queue = deque(sorted_offsets)
        silence_queue = deque(silences)

        # print "region values: " + str(region_values)
        # print "sorted_offsets: " + str(sorted_offsets)
        # print "region queue: " + str(region_queue)

        last_line = ""

        region_1000_replaced = False

        with open(self.clan_file, "rU") as file:

            # declare the two time interval arrays we're going to
            # be filling as we iterate through every line of the file
            previous_clan_interval = [None, None]
            current_clan_interval = [None, None]

            # regex object to parse out the timestamp
            # interval from each line
            interval_regx = re.compile("(\025\d+_\d+)")

            # pop the first silence and region off the queue
            curr_region = region_queue.popleft()
            curr_region_start = curr_region * 5 * 60 * 1000 # convert to milliseconds
            curr_region_end   = curr_region_start + 60 * 60 * 1000 # end is 1 hour from start

            if silence_queue:
                curr_silence = silence_queue.popleft()
            else:
                curr_silence = None
            # else:
            #     curr_silence = Silence(1, 2, 1)
            # print "curr_region: " + str(curr_region)
            # print "curr_region_start: " + str(curr_region_start)
            # print "curr_region_end: " + str(curr_region_end)

            # initialize the start/end written flags
            start_written = False
            end_written = False

            # initialize the silence/subregion overlap flags
            region_start_in_silence = False
            region_end_in_silence = False
            region_contains_silence = False

            # initialize the global silence/subregion overlap flag
            silence_overlapped = False

            # We iterate over the clan file line by line
            for index, line in enumerate(file):
                # # get rid of leading and trailing whitespace from the line
                # line = raw_line.strip()

                # We only write comments after lines with " *XYZ: " prefixes.
                # The check for curr_silence ensures that there is still a
                # silence waiting to be written
                if line.startswith("*") and (curr_region is not None):
                    # parse out the part of the line with the interval in it
                    interval_reg_result = interval_regx.search(line)

                    if interval_reg_result is None:
                        last_line = line
                        continue

                    # pull out the string, and replace the hidden bullet characters
                    interval_string = interval_reg_result.group().replace("\025", "")

                    # tokenize that string into an array of 2 strings ["123", "456"]
                    interval = interval_string.split("_")

                    # assign the integer representation of that interval to
                    # the current_clan_interval array. This keeps track of the
                    # timepoints we're currently dealing with as we iterate
                    # over the file
                    current_clan_interval[0] = int(interval[0])
                    current_clan_interval[1] = int(interval[1])

                    #print "clan[0]: " + str(current_clan_interval[0]) + "clan[1]: " + str(current_clan_interval[1]) + "    curr_region_start: " + str(curr_region_start)

                    # Handle special case for 0 offset
                    if curr_region_start == 0:
                        curr_region_start = 1000 # avoid 0 millisecond. start at 1000 millisecond.
                        #print "made subregion interval 1000 adjustment"
                        #print "line" + str(index)
                        region_1000_replaced = True
                    # We check to make sure that in interval ABC_XYZ,
                    # XYZ is strictly > ABC. If not we print warning to
                    # GUI and raise exception, halting the clan file processing
                    # if current_clan_interval[1] < current_clan_interval[0]:
                    #     print "\n\n***************************************************************************"
                    #     print "timestamp interval is malformed: {}_{}:   CLAN file line# {}"\
                    #         .format(interval[0],
                    #                 interval[1],
                    #                 index)
                    #     print "***************************************************************************\n"

                    if curr_silence:
                        if (curr_region_start > curr_silence.start) and\
                                (curr_region_start < curr_silence.end):
                            region_start_in_silence = True
                        else:
                            region_start_in_silence = False

                        if (curr_region_end < curr_silence.end) and\
                                (curr_region_end > curr_silence.start):
                            region_end_in_silence = True
                        else:
                            region_end_in_silence = False

                        if (curr_region_start < curr_silence.start) and\
                                (curr_region_end > curr_silence.end):
                            region_contains_silence = True
                        else:
                            region_contains_silence = False

                    # If the currently queued silence starts before the
                    # end of the current clan interval, and start silence has
                    # not been written, we...
                    if (curr_region_start <= current_clan_interval[1])\
                            and (not start_written):
                        if region_start_in_silence or region_end_in_silence or region_contains_silence:

                            # alter the ending timestamp to correspond to the beginning
                            # of the subregion, and write the new line to the output file

                            # if "." is not in the line, then we're about to write a
                            # comment inside a multi-line entry. In this case, we need
                            # to insert this missing period so that CHECK doesn't fail.
                            if "." not in line:
                                new_line = line.replace("\025" + interval_string + "\025",
                                                        ". \025{}_{}\025".format(current_clan_interval[0],
                                                                                 int(curr_region_start)))
                                output.write(new_line)

                            else:
                                output.write(line.replace(interval_string, "{}_{}".format(current_clan_interval[0],
                                                                                      int(curr_region_start))))

                            if region_1000_replaced:
                                output.write("%xcom:\tsubregion comment rewrote interval to 0_1, rewriting to {}_{}"\
                                             .format(current_clan_interval[0], int(curr_region_start)))
                                region_1000_replaced = False    # reset flag

                            if (curr_region == lowest_region):
                                output.write("%xcom:\tsubregion {} of {}  (ranked {} of {})  starts at {} -- previous timestamp adjusted: was {} - lowest ranked region; [contains silent region: [{}, {}] ]\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        region_values.index(curr_region) + 1,
                                                        len(region_values),
                                                        curr_region_start,
                                                        current_clan_interval[1],
                                                        curr_silence.start,
                                                        curr_silence.end))
                            else:
                                # insert the comment immediately after the altered clan entry
                                output.write("%xcom:\tsubregion {} of {} (ranked {} of {}) starts at {} -- previous timestamp adjusted: was {} [contains silent region: [{}, {}] ]\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        region_values.index(curr_region) + 1,
                                                        len(region_values),
                                                        curr_region_start,
                                                        current_clan_interval[1],
                                                        curr_silence.start,
                                                        curr_silence.end))

                            start_written = True
                            end_written = False
                            silence_overlapped = True

                            # stop progressing though the conditions and
                            # head to next line in the file
                            continue
                        else:

                            # alter the ending timestamp to correspond to the beginning
                            # of the silence, and write the new line to the output file

                            # if "." is not in the line, then we're about to write a
                            # comment inside a multi-line entry. In this case, we need
                            # to insert this missing period so that CHECK doesn't fail.
                            if "." not in line:
                                new_line = line.replace("\025" + interval_string + "\025",
                                                        ". \025{}_{}\025".format(current_clan_interval[0],
                                                                                 int(curr_region_start)))
                                output.write(new_line)

                            else:
                                output.write(line.replace(interval_string, "{}_{}".format(current_clan_interval[0],
                                                                                          int(curr_region_start))))

                            if region_1000_replaced:
                                output.write("%xcom:\tsubregion comment rewrote interval to 0_1, rewriting to {}_{}\n"\
                                             .format(current_clan_interval[0], int(curr_region_start)))
                                region_1000_replaced = False

                            if (curr_region == lowest_region):
                                output.write("%xcom:\tsubregion {} of {}   (ranked {} of {})  starts at {} -- previous timestamp adjusted: was {}. lowest ranked region; skip unless necessary\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        region_values.index(curr_region) + 1,
                                                        len(region_values),
                                                        curr_region_start,
                                                        current_clan_interval[1]))
                            else:
                                # insert the comment immediately after the altered clan entry
                                output.write("%xcom:\tsubregion {} of {}  (ranked {} of {})  starts at {} -- previous timestamp adjusted: was {}\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        region_values.index(curr_region) + 1,
                                                        len(region_values),
                                                        curr_region_start,
                                                        current_clan_interval[1]))

                            start_written = True
                            end_written = False

                            # stop progressing though the conditions and
                            # head to next line in the file
                            continue

                    # If the end of the currently queued subregion is less than
                    # the end of the current clan time interval...
                    if (curr_region_end <= current_clan_interval[1])\
                            and start_written\
                            and (not end_written):
                        #print "inside the end writing section"
                        if region_start_in_silence or region_end_in_silence or region_contains_silence:

                            # We first alter the clan time interval to match the end of the
                            # subregion we are about to insert, and write it to the output file

                            # if "." is not in the line, then we're about to write a
                            # comment inside a multi-line entry. In this case, we need
                            # to insert this missing period so that CHECK doesn't fail.
                            if "." not in line:
                                new_line = line.replace("\025" + interval_string + "\025",
                                                        ". \025{}_{}\025".format(current_clan_interval[0],
                                                                                 int(curr_region_end)))
                                output.write(new_line)

                            else:
                                output.write(line.replace(interval_string, "{}_{}".format(current_clan_interval[0],
                                                                                          int(curr_region_end))))


                            if curr_region == lowest_region:
                                output.write("%xcom:\tsubregion {} of {}   (ranked {} of {})  ends at {} -- previous timestamp adjusted: was {} - lowest ranked region; [contains silent region: [{}, {}] ]\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        region_values.index(curr_region) + 1,
                                                        len(region_values),
                                                        curr_region_end,
                                                        current_clan_interval[1],
                                                        curr_silence.start,
                                                        curr_silence.end))

                            else:
                                # then we write the end subregion comment right afterwards
                                output.write("%xcom:\tsubregion {} of {}  (ranked {} of {})  ends at {} -- previous timestamp adjusted: was {} [contains silent region: [{}, {}] ]\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        region_values.index(curr_region) + 1,
                                                        len(region_values),
                                                        curr_region_end,
                                                        current_clan_interval[1],
                                                        curr_silence.start,
                                                        curr_silence.end))

                            end_written = True
                            start_written = False
                            silence_overlapped = True

                            #region_start_in_silence = False
                            #region_end_in_silence = False

                            # make sure queue contains items
                            # and pop the next silence off of it
                            if region_queue:
                                curr_region = region_queue.popleft()
                                #print "curr_region: " + str(curr_region)
                                curr_region_start = curr_region * 5 * 60 * 1000 # convert to milliseconds
                                curr_region_end   = curr_region_start + 60 * 60 * 1000 # end is 1 hour from start
                                #print "curr_region_start: " + str(curr_region_start)
                                #print "curr_region_end: " + str(curr_region_end)
                                region_number = region_number + 1
                            else:
                                # if region_queue is empty, we set curr_region to None
                                # so that the top level check fails
                                # (if line.startswith("*") and curr_silence:)
                                # this ensures that after all the subregions have been handled,
                                # we just write all subsequent lines to output without any
                                # further processing
                                curr_region = None
                            continue
                        else:
                            # We first alter the clan time interval to match the end of the
                            # silence we are about to insert, and write it to the output file

                            # if "." is not in the line, then we're about to write a
                            # comment inside a multi-line entry. In this case, we need
                            # to insert this missing period so that CHECK doesn't fail.
                            if "." not in line:
                                new_line = line.replace("\025" + interval_string + "\025",
                                                        ". \025{}_{}\025".format(current_clan_interval[0],
                                                                                 int(curr_region_end)))
                                output.write(new_line)

                            else:
                                output.write(line.replace(interval_string, "{}_{}".format(current_clan_interval[0],
                                                                                          int(curr_region_end))))


                            if (curr_region == lowest_region):
                                output.write("%xcom:\tsubregion {} of {}   (ranked {} of {})  ends at {} -- previous timestamp adjusted: was {}. lowest ranked region; skip unless necessary\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        region_values.index(curr_region) + 1,
                                                        len(region_values),
                                                        curr_region_end,
                                                        current_clan_interval[1]))
                            else:
                                # then we write the end subbregion comment right afterwards
                                output.write("%xcom:\tsubregion {} of {}  (ranked {} of {})  ends at {} -- previous timestamp adjusted: was {}\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        region_values.index(curr_region) + 1,
                                                        len(region_values),
                                                        curr_region_end,
                                                        current_clan_interval[1]))

                            end_written = True
                            start_written = False



                            # make sure queue contains items
                            # and pop the next subregion off of it
                            if region_queue:
                                curr_region = region_queue.popleft()
                                curr_region_start = curr_region * 5 * 60 * 1000 # convert to milliseconds
                                curr_region_end   = curr_region_start + 60 * 60 * 1000 # end is 1 hour from start
                                region_number = region_number + 1
                            else:
                                # if silence_queue is empty, we set curr_silence to None
                                # so that the top level check fails
                                # (if line.startswith("*") and curr_silence:)
                                # this ensures that after all the silences have been handled,
                                # we just write all subsequent lines to output without any
                                # further processing
                                curr_region = None
                            continue

                if line.startswith("\t"):
                    # if there's no more subregions to insert, then just write
                    # out the original line and continue
                    if not curr_region:
                        output.write(line)
                        continue


                    # parse out the part of the line with the interval in it
                    interval_reg_result = interval_regx.search(line)

                    # if there's no interval on this line, just write it out
                    # and continue to the next one
                    if interval_reg_result is None:
                        output.write(line)
                        last_line = line
                        continue

                    # pull out the string, and replace the hidden bullet characters
                    interval_string = interval_reg_result.group().replace("\025", "")

                    # tokenize that string into an array of 2 strings ["123", "456"]
                    interval = interval_string.split("_")

                    # assign the integer representation of that interval to
                    # the current_clan_interval array. This keeps track of the
                    # timepoints we're currently dealing with as we iterate
                    # over the file
                    current_clan_interval[0] = int(interval[0])
                    current_clan_interval[1] = int(interval[1])


                    if curr_silence:
                        if (curr_region_start > curr_silence.start) and\
                                (curr_region_start < curr_silence.end):
                            region_start_in_silence = True
                        else:
                            region_start_in_silence = False

                        if (curr_region_end < curr_silence.end) and\
                                (curr_region_end > curr_silence.start):
                            region_end_in_silence = True
                        else:
                            region_end_in_silence = False

                        if (curr_region_start < curr_silence.start) and\
                                (curr_region_end > curr_silence.end):
                            region_contains_silence = True
                        else:
                            region_contains_silence = False

                    # If the currently queued silence starts before the
                    # end of the current clan interval, and start silence has
                    # not been written, we...
                    if (curr_region_start <= current_clan_interval[1])\
                            and (not start_written):
                        if region_start_in_silence or region_end_in_silence or region_contains_silence:
                            # alter the ending timestamp to correspond to the beginning
                            # of the subregion, and write the new line to the output file

                            # if "." is not in the line, then we're about to write a
                            # comment inside a multi-line entry. In this case, we need
                            # to insert this missing period so that CHECK doesn't fail.
                            if "." not in line:
                                new_line = line.replace("\025" + interval_string + "\025",
                                                        ". \025{}_{}\025".format(current_clan_interval[0],
                                                                                 int(curr_region_start)))
                                output.write(new_line)

                            else:
                                output.write(line.replace(interval_string, "{}_{}".format(current_clan_interval[0],
                                                                                          int(curr_region_start))))
                            if (curr_region == lowest_region):
                                output.write("%xcom:\tsubregion {} of {}   (ranked {} of {})  starts at {} -- previous timestamp adjusted: was {} - lowest ranked region; [contains silent region: [{}, {}] ]\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        region_values.index(curr_region) + 1,
                                                        len(region_values),
                                                        curr_region_start,
                                                        current_clan_interval[1],
                                                        curr_silence.start,
                                                        curr_silence.end))
                            else:
                                # insert the comment immediately after the altered clan entry
                                output.write("%xcom:\tsubregion {} of {}   (ranked {} of {})  starts at {} -- previous timestamp adjusted: was {} [contains silent region: [{}, {}] ]\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        region_values.index(curr_region) + 1,
                                                        len(region_values),
                                                        curr_region_start,
                                                        current_clan_interval[1],
                                                        curr_silence.start,
                                                        curr_silence.end))

                            start_written = True
                            end_written = False
                            silence_overlapped = True

                            # stop progressing though the conditions and
                            # head to next line in the file
                            continue
                        else:
                            # alter the ending timestamp to correspond to the beginning
                            # of the silence, and write the new line to the output file

                            # if "." is not in the line, then we're about to write a
                            # comment inside a multi-line entry. In this case, we need
                            # to insert this missing period so that CHECK doesn't fail.
                            if "." not in line:
                                new_line = line.replace("\025" + interval_string + "\025",
                                                        ". \025{}_{}\025".format(current_clan_interval[0],
                                                                                 int(curr_region_start)))
                                output.write(new_line)

                            else:
                                output.write(line.replace(interval_string, "{}_{}".format(current_clan_interval[0],
                                                                                          int(curr_region_start))))

                            if (curr_region == lowest_region):
                                output.write("%xcom:\tsubregion {} of {}   (ranked {} of {})  starts at {} -- previous timestamp adjusted: was {}. lowest ranked region; skip unless necessary\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        region_values.index(curr_region) + 1,
                                                        len(region_values),
                                                        curr_region_start,
                                                        current_clan_interval[1]))
                            else:
                                # insert the comment immediately after the altered clan entry
                                output.write("%xcom:\tsubregion {} of {}   (ranked {} of {})  starts at {} -- previous timestamp adjusted: was {}\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        region_values.index(curr_region) + 1,
                                                        len(region_values),
                                                        curr_region_start,
                                                        current_clan_interval[1]))

                            start_written = True
                            end_written = False

                            # stop progressing though the conditions and
                            # head to next line in the file
                            continue

                    # If the end of the currently queued subregion is less than
                    # the end of the current clan time interval...
                    if (curr_region_end <= current_clan_interval[1])\
                            and start_written\
                            and (not end_written):
                        if region_start_in_silence or region_end_in_silence or region_contains_silence:
                            # We first alter the clan time interval to match the end of the
                            # subregion we are about to insert, and write it to the output file

                            # if "." is not in the line, then we're about to write a
                            # comment inside a multi-line entry. In this case, we need
                            # to insert this missing period so that CHECK doesn't fail.
                            if "." not in line:
                                new_line = line.replace("\025" + interval_string + "\025",
                                                        ". \025{}_{}\025".format(current_clan_interval[0],
                                                                                 int(curr_region_end)))
                                output.write(new_line)

                            else:
                                output.write(line.replace(interval_string, "{}_{}".format(current_clan_interval[0],
                                                                                          int(curr_region_end))))

                            if curr_region == lowest_region:
                                output.write("%xcom:\tsubregion {} of {}   (ranked {} of {})  ends at {} -- previous timestamp adjusted: was {} - lowest ranked region; [contains silent region: [{}, {}] ]\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        region_values.index(curr_region) + 1,
                                                        len(region_values),
                                                        curr_region_end,
                                                        current_clan_interval[1],
                                                        curr_silence.start,
                                                        curr_silence.end))

                            else:
                                # then we write the end subregion comment right afterwards
                                output.write("%xcom:\tsubregion {} of {}   (ranked {} of {})  ends at {} -- previous timestamp adjusted: was {} [contains silent region: [{}, {}] ]\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        region_values.index(curr_region) + 1,
                                                        len(region_values),
                                                        curr_region_end,
                                                        current_clan_interval[1],
                                                        curr_silence.start,
                                                        curr_silence.end))

                            end_written = True
                            start_written = False
                            silence_overlapped = True

                            #region_start_in_silence = False
                            #region_end_in_silence = False

                            # make sure queue contains items
                            # and pop the next silence off of it
                            if region_queue:
                                curr_region = region_queue.popleft()
                                #print "curr_region: " + str(curr_region)
                                curr_region_start = curr_region * 5 * 60 * 1000 # convert to milliseconds
                                curr_region_end   = curr_region_start + 60 * 60 * 1000 # end is 1 hour from start
                                #print "curr_region_start: " + str(curr_region_start)
                                #print "curr_region_end: " + str(curr_region_end)
                                region_number = region_number + 1
                            else:
                                # if region_queue is empty, we set curr_region to None
                                # so that the top level check fails
                                # (if line.startswith("*") and curr_silence:)
                                # this ensures that after all the subregions have been handled,
                                # we just write all subsequent lines to output without any
                                # further processing
                                curr_region = None
                            continue
                        else:
                            # We first alter the clan time interval to match the end of the
                            # silence we are about to insert, and write it to the output file

                            # if "." is not in the line, then we're about to write a
                            # comment inside a multi-line entry. In this case, we need
                            # to insert this missing period so that CHECK doesn't fail.
                            if "." not in line:
                                new_line = line.replace("\025" + interval_string + "\025",
                                                        ". \025{}_{}\025".format(current_clan_interval[0],
                                                                                 int(curr_region_end)))
                                output.write(new_line)

                            else:
                                output.write(line.replace(interval_string, "{}_{}".format(current_clan_interval[0],
                                                                                          int(curr_region_end))))

                            if (curr_region == lowest_region):
                                output.write("%xcom:\tsubregion {} of {}   (ranked {} of {})  ends at {} -- previous timestamp adjusted: was {}. lowest ranked region; skip unless necessary\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        region_values.index(curr_region) + 1,
                                                        len(region_values),
                                                        curr_region_end,
                                                        current_clan_interval[1]))
                            else:
                                # then we write the end subbregion comment right afterwards
                                output.write("%xcom:\tsubregion {} of {}   (ranked {} of {})   ends at {} -- previous timestamp adjusted: was {}\n"
                                                .format(region_number,
                                                        len(region_values),
                                                        region_values.index(curr_region) + 1,
                                                        len(region_values),
                                                        curr_region_end,
                                                        current_clan_interval[1]))

                            end_written = True
                            start_written = False



                            # make sure queue contains items
                            # and pop the next subregion off of it
                            if region_queue:
                                curr_region = region_queue.popleft()
                                curr_region_start = curr_region * 5 * 60 * 1000 # convert to milliseconds
                                curr_region_end   = curr_region_start + 60 * 60 * 1000 # end is 1 hour from start
                                region_number = region_number + 1
                            else:
                                # if silence_queue is empty, we set curr_silence to None
                                # so that the top level check fails
                                # (if line.startswith("*") and curr_silence:)
                                # this ensures that after all the silences have been handled,
                                # we just write all subsequent lines to output without any
                                # further processing
                                curr_region = None
                            continue



                if curr_silence:
                    if current_clan_interval[1] >= curr_silence.end and silence_queue:
                    #print "queue pre-pop: " + str(silence_queue)
                        curr_silence = silence_queue.popleft()
                # this is a check for a special case. If we've reached @End,
                # but the end of a silence has not been written, we insert that
                # last end-silence comment in before writing out the @End line
                if line.startswith("@End") and not end_written:

                    output.write("%xcom:\tsubregion {} of {}   (ranked {} of {})  ends at {} -- previous timestamp adjusted: was {}\n"
                                     .format(region_number,
                                             len(region_values),
                                             region_values.index(curr_region) + 1,
                                             len(region_values),
                                             curr_region_end,
                                             current_clan_interval[1]))
                    output.write(line)
                    region_number = region_number + 1

                else:
                    # if the line is not a bulleted time interval, we just
                    # write it straight to the output file without processing.
                    # This includes %com's and other meta information
                    output.write(line)

        output.close()
        self.find_interval_errors_cha()

    def find_interval_errors(self):

        # regex object to parse out the timestamp
        # interval from each line

        interval_regx = re.compile("(\d+_\d+)")
        current_clan_interval = [None, None]

        with open(self.export_clan_file, "rU") as file:

            for index, raw_line in enumerate(file):
                # get rid of preceding and trailing whitespace from the line
                line = raw_line.strip()

                # We only write comments after lines with " *XYZ: " prefixes.
                # The check for curr_silence ensures that there is still a
                # silence waiting to be written
                if line.startswith("*"):
                    # parse out the part of the line with the interval in it
                    interval_string = interval_regx.search(line).group()
                    # tokenize that string into an array of 2 strings ["123", "456"]
                    interval = interval_string.split("_")

                    # assign the integer representation of that interval to
                    # the current_clan_interval array. This keeps track of the
                    # timepoints we're currently dealing with as we iterate
                    # over the file
                    current_clan_interval[0] = int(interval[0])
                    current_clan_interval[1] = int(interval[1])

                    # We check to make sure that in interval ABC_XYZ,
                    # XYZ is strictly > ABC. If not we print warning

                    if current_clan_interval[1] < current_clan_interval[0]:
                        print "\n\n***********************************************************************"
                        print "timestamp onset > offset: {}_{}:   CLAN line# {}"\
                            .format(interval[0],
                                    interval[1],
                                    index)
                        print "***********************************************************************\n"

    def find_interval_errors_cha(self):

        # regex object to parse out the timestamp
        # interval from each line

        interval_regx = re.compile("(\025\d+_\d+)")
        current_clan_interval = [None, None]

        with open(self.export_clan_file, "rU") as file:

            for index, line in enumerate(file):
                # parse out the part of the line with the interval in it
                interval_regx_result = interval_regx.search(line)

                if interval_regx_result is None:
                    continue

                interval_string = interval_regx_result.group().replace("\025", "")
                interval = interval_string.split("_")

                current_clan_interval[0] = int(interval[0])
                current_clan_interval[1] = int(interval[1])

                if current_clan_interval[1] < current_clan_interval[0]:
                        print "\n\n***********************************************************************"
                        print "timestamp onset > offset: {}_{}:   CLAN line# {}"\
                            .format(interval[0],
                                    interval[1],
                                    index)
                        print "***********************************************************************\n"