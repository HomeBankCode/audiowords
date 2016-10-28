
class SilenceParser:

    def __init__(self, path_to_file, minimum_sound):
        self.min_sound_length = minimum_sound
        self.sounds = self.parse_sounds(path_to_file)
        self.silences = self.parse_silences2(self.sounds)

    def parse_sounds(self, path_to_file):

        sounds = []

        with open(path_to_file, "rU") as file:

            # iterating through the initial sound regions file
            for line in file:
                # tokenize each value into an array of string. - e.g. ["123.321", "456.654", "3"]
                entries = line.split()

                # convert the entries to milliseconds and store their values
                # into an array of floats called sound
                sound = [float(entries[0])*1000, float(entries[1])*1000]

                # if sound[0] == sound[1]:
                #     continue
                # if the length of the sound is greater than the
                # minimum sound length, or entry is an [End] marker,
                # add it to the sounds[], which will be returned
                # as the result of parsing
                if (sound[1] - sound[0]) > self.min_sound_length\
                        or entries[2] == "[End]":
                    sounds.append(sound)
        return sounds

    def parse_silences(self, sounds):

        silences = []

        prev_sound = None
        curr_sound = None

        num = 1

        # assuming all Label_Track.txt files end with a region indicating
        # the length of the track, with equal onset/offset, having only 2
        # sounds implies that there is only 1 sound region apart from this
        # end marker. In that case, we add an artificial silence to keep the
        # script running. Quick fix for now.
        if len(sounds) == 2:
            silences.append(Silence(1, 3, 1))
            return silences
        # iterating through an array of sound intervals.
        # this was provided by the parse_sounds() function
        # earlier
        for sound in sounds:
            curr_sound = sound
            # for the first iteration, we set prev_sound as the first
            # sound and jump to the next iteration. This provides a trailing
            # variable to compare the interval between sounds. curr_sound is
            # what the loop is currently on, while prev_sound was the sound from
            # the last iteration
            if prev_sound == None:
                prev_sound = curr_sound
                continue
            else:
                # Construct silence object, using:
                #
                #    start = prev_sound end
                #    end   = curr_count start
                #
                # The values are converted back to seconds before construction.
                # Then, add this Silence object to the silences[] we are going to return
                if curr_sound[0] == curr_sound[1]:
                    if curr_sound[0] - prev_sound[1] > 0:
                        silence = Silence(prev_sound[1]/1000, curr_sound[0]/1000, num)
                    else:
                        continue
                silence = Silence(prev_sound[1]/1000, curr_sound[0]/1000, num)
                silences.append(silence)

                prev_sound = curr_sound # shift things over for next iteration
                num += 1

        return silences

    def parse_silences2(self, sounds):
        silences = []
        prev_sound = None
        curr_sound = None
        num = 1
        # set start marker at 1000 millisecond
        start = [1000, 1000]

        for sound in sounds:
            if prev_sound is None:
                prev_sound = start
            curr_sound = sound
            silence = Silence(float(prev_sound[1])/1000, curr_sound[0]/1000, num)
            # silences less than 15 milliseconds are probably rounding errors
            if silence.end - silence.start > 15:
                silences.append(silence)
                num += 1
            print "silence #" + str(num) + " " + str(silence)
            prev_sound = curr_sound
        return silences


class Silence(object):

    def __init__(self, start, end, number):
        self.start = start * 1000   # silence onset (converted to milliseconds)
        self.end = end * 1000       # silence offset (converted to milliseconds)
        self.number = number        # count relative to other silences

    def __repr__(self):
        return str(self.start) + " - " + str(self.end)

    def __str__(self):
        return str(self.start) + " - " + str(self.end)

    def length(self):
        return self.end - self.start

