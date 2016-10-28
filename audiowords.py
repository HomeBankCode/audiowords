from Tkinter import *
import tkFileDialog

from silences import *
from clanfile import *
from overlaps import *

import os

class MainWindow:

    def __init__(self, master):

        self.root = master                  # main GUI context
        self.root.title("AudioWords")       # title of window
        self.root.geometry("1280x500")       # size of GUI window
        self.main_frame = Frame(root)       # main frame into which all the Gui components will be placed
        self.main_frame.pack()              # pack() basically sets up/inserts the element (turns it on)

        self.silences = []

        self.all_prefix = None
        self.file_prefix = None

        self.sound_regions_file = None

        self.silence_export_file = None
        self.silence_parser = None

        self.clan_file = None
        self.clan__export_file = None

        self.lena_file = None
        self.overlaps = None

        # declare all the GUI buttons and labels
        self.load_sound_button = Button(self.main_frame,
                                        text = "Load Sound Regions",
                                        command = self.load_regions)

        self.export_sound_button = Button(self.main_frame,
                                          text = "Export New Regions",
                                          command = self.export_regions)

        self.load_all_button = Button(self.main_frame,
                                      text="Load All (cex)",
                                      command=self.load_all)
        # for the new clan format
        self.load_all_cha_button = Button(self.main_frame,
                                          text="Load All (cha)",
                                          command=self.load_all_cha)

        self.load_clan_button = Button(self.main_frame,
                                       text = "Load CLAN",
                                       command=self.load_clan)

        self.load_lena_button = Button(self.main_frame,
                                       text="Load Lena",
                                       command=self.load_lena)

        self.export_overlaps_button = Button(self.main_frame,
                                             text="Export Overlaps",
                                             command=self.export_overlaps)

        self.clear_lena_button = Button(self.main_frame,
                                        text="Clear",
                                        command=self.clear_lena)

        self.export_clan_button = Button(self.main_frame,
                                         text = "Export CLAN",
                                         command = self.export_clan)


        self.clear_clan_button = Button(self.main_frame,
                                        text = "clear",
                                        command = self.clear_clan)

        # this is for the box where you enter the minimum interval of sound
        self.minimum_sound_entry = Entry(self.main_frame, width=10)
        self.minimum_sound_entry.insert(0, "10000")
        self.minimum_sound_label = Label(self.main_frame, text="minimum sound interval\n(in milliseconds)")
        self.minimum_sound_missing = Label(self.main_frame, text="missing minimum sound interval", fg="red")

        # this is for selecting how many lena overlap regions to find

        self.top_n_region_entry = Entry(self.main_frame, width=10)
        self.top_n_region_entry.insert(0, "5")
        self.top_n_region_label = Label(self.main_frame, text="# of regions")
        self.top_n_missing_label = Label(self.main_frame, text="enter n", fg="red")

        # warning label if you try to export regions without
        # loading initial sound regions file
        self.sound_file_missing = Label(self.main_frame, text="load sound regions first", fg="red")

        self.clan_loaded_label = Label(self.main_frame, text="Clan file loaded", fg="green")
        self.clan_formatting_error = Label(self.main_frame, text="Clan file was malformed", fg="red")

        # load all the buttons onto the GUI
        self.load_sound_button.grid(row=2, column=0)
        self.export_sound_button.grid(row=3, column=0)
        self.load_all_button.grid(row=2, column=1)
        self.load_all_cha_button.grid(row=3, column=1)
        self.load_clan_button.grid(row=4, column=1)
        self.export_clan_button.grid(row=5, column=1)
        self.clear_clan_button.grid(row=6, column=1)
        self.load_lena_button.grid(row=2, column=2)
        self.export_overlaps_button.grid(row=3, column=2)
        self.clear_lena_button.grid(row=4, column=2)


        # load minimum sound box to GUI
        self.minimum_sound_entry.grid(row=4, column=0)
        self.minimum_sound_label.grid(row=5, column=0, rowspan=2)

        # load # of region box onto the GUI
        self.top_n_region_entry.grid(row=5, column=2)
        self.top_n_region_label.grid(row=6, column=2)


        # declare and load the box where parsed silences will be previewed
        self.silence_list_box = Listbox(self.main_frame, width=26, height=12)
        self.silence_list_box.grid(row=1, column=0, padx=7)

        # declare and load the box for the word density overlap functions
        self.meaningful_region_box = Listbox(self.main_frame, width=40, height=12)
        self.meaningful_region_box.grid(row= 1, column=2, padx=7)

        self.awc_region_box = Listbox(self.main_frame, width=40, height=12)
        self.awc_region_box.grid(row=1, column=3, padx=7)

        self.ctc_region_box = Listbox(self.main_frame, width=40, height=12)
        self.ctc_region_box.grid(row=1, column=4, padx=7)

        self.cvc_region_box = Listbox(self.main_frame, width=40, height=12)
        self.cvc_region_box.grid(row=3, column=3, rowspan=5, padx=7)

        self.ctc_cvc_box = Listbox(self.main_frame, width=40, height=12)
        self.ctc_cvc_box.grid(row=3, column=4, rowspan=5, padx=7)

        # declare and grid all the labels for the density boxes

        self.meaningful_label = Label(self.main_frame, text="Meaningful")
        self.meaningful_label.grid(row=0, column=2)

        self.awc_label = Label(self.main_frame, text="AWC")
        self.awc_label.grid(row=0, column=3)

        self.ctc_label = Label(self.main_frame, text="CTC")
        self.ctc_label.grid(row=0, column=4)

        self.cvc_label = Label(self.main_frame, text="CVC")
        self.cvc_label.grid(row=2, column=3)

        self.ctc_cvc_label = Label(self.main_frame, text="CTC/CVC")
        self.ctc_cvc_label.grid(row=2, column=4)





    def load_regions(self, path=""):

        # check for empty minimum sound box
        if not self.minimum_sound_entry.get():
            self.sound_file_missing.grid_remove()
            self.minimum_sound_missing.grid(row=7, column=0)
            raise Exception("You need to enter a minimum interval of sound to ignore")

        self.minimum_sound_missing.grid_remove()

        # set the path to the audacity regions with a popup directory widget
        if path == "":
            self.sound_regions_file = tkFileDialog.askopenfilename()
            self.sound_file_missing.grid_remove()
        else:
            self.sound_regions_file = path
        # extract the value provided as the minimum sound length
        minimum_sound = float(self.minimum_sound_entry.get())

        # construct the SilenceParser with the regions file and minimum sound.
        # this object extracts the sound regions (ignoring those shorter than minimum_sound
        # and calculates the silences in between them.
        self.silence_parser = SilenceParser(self.sound_regions_file, minimum_sound)

        # load the preview box with all the silences
        self.silence_list_box.delete(0, END)
        for index, item in enumerate(self.silence_parser.silences):
            self.silence_list_box.insert(index, str(item) + " [{}] ".format(index + 1))

    def export_regions(self):

        # check to make sure the initial regions have been loaded
        # and a SilenceParser object has been constructed, otherwise
        # printing warnings and throw an exception
        if self.silence_parser is None:
            self.minimum_sound_missing.grid_remove()
            self.sound_file_missing.grid(row=7, column=0)
            raise Exception("You need to load the audacity sound regions first")

        self.sound_file_missing.grid_remove()

        # get path to new regions export file with a popup directory widget
        self.silence_export_file = tkFileDialog.asksaveasfilename()

        # run the silence parsing anew for each export_silence(),
        # so that the user doesn't have to reload the initial
        # regions every time they need different result
        minimum_sound = float(self.minimum_sound_entry.get())
        self.silence_parser = SilenceParser(self.sound_regions_file, minimum_sound)

        # update the silence preview box
        self.silence_list_box.delete(0, END)
        for index, item in enumerate(self.silence_parser.silences):
            self.silence_list_box.insert(index, str(item) + " [{}] ".format(index + 1))

        # write out each region to a new file (silence_export_file)
        with open(self.silence_export_file, "w") as export_file:

            for index, entry in enumerate(self.silence_parser.sounds):

                # handle the [End] region as a special case
                if (index + 1) == len(self.silence_parser.sounds)\
                    and entry[0] == entry[1]:

                    export_file.write("{0:.6f}\t{1:.6f}\t[End]\n".format(entry[0]/1000,
                                                                         entry[1]/1000))
                else:
                    export_file.write("{0:.6f}\t{1:.6f}\t{2}\n".format(entry[0]/1000,
                                                                       entry[1]/1000,
                                                                       index + 1))

    def export_regions_chain(self, path):

        # check to make sure the initial regions have been loaded
        # and a SilenceParser object has been constructed, otherwise
        # printing warnings and throw an exception
        # if self.silence_parser is None:
        #     self.minimum_sound_missing.grid_remove()
        #     self.sound_file_missing.grid(row=7, column=0)
        #     raise Exception("You need to load the audacity sound regions first")
        #
        # self.sound_file_missing.grid_remove()

        # get path to new regions export file with a popup directory widget
        self.silence_export_file = path

        # run the silence parsing anew for each export_silence(),
        # so that the user doesn't have to reload the initial
        # regions every time they need different result
        minimum_sound = float(self.minimum_sound_entry.get())
        self.silence_parser = SilenceParser(self.sound_regions_file, minimum_sound)

        # update the silence preview box
        self.silence_list_box.delete(0, END)
        for index, item in enumerate(self.silence_parser.silences):
            self.silence_list_box.insert(index, str(item) + " [{}] ".format(index + 1))

        # write out each region to a new file (silence_export_file)
        with open(self.silence_export_file, "w") as export_file:

            for index, entry in enumerate(self.silence_parser.sounds):

                # handle the [End] region as a special case
                if (index + 1) == len(self.silence_parser.sounds)\
                    and entry[0] == entry[1]:

                    export_file.write("{0:.6f}\t{1:.6f}\t[End]\n".format(entry[0]/1000,
                                                                         entry[1]/1000))
                else:
                    export_file.write("{0:.6f}\t{1:.6f}\t{2}\n".format(entry[0]/1000,
                                                                       entry[1]/1000,
                                                                       index + 1))
    def load_all(self):
        """
        This is an all-in-one function that asks for the initial
        CLAN file, and then figures out what the remaining files
        need to be loaded and processed. It assumes that files will
        be named in the following format:


        16_08.cex     <- this is the file to be loaded.
                         the rest will be loaded/generated automatically

        16_08_silences.txt
        16_08_lena5min.csv
        16_08_silences_added.cex
        16_08_subregions.cex

        :return:
        """
        self.clan_formatting_error.grid_remove()
        self.clan_file = tkFileDialog.askopenfilename()

        if self.clan_file != "":
            self.clan_loaded_label.grid(row=1, column=1)

        # pull out the prefix for the path and the filename
        #   e.g.
        #       all_prefix  = /Users/ebergelson/Desktop/Github/SeedlingsBabylab/audiowords/data/input
        #       file_prefix = 16_08
        self.all_prefix = os.path.split(self.clan_file)[0]
        self.file_prefix = os.path.split(self.clan_file)[1][0:5]

        # print "clan file path: " + self.clan_file
        # print "all prefix: " + self.all_prefix
        # print "file prefix: " + self.file_prefix

        labeled_track_filename = "Label_Track.txt"
        silences_filename = self.file_prefix + "_silences.txt"

        # Call load_regions with the Label_Track file
        self.load_regions(path=os.path.join(self.all_prefix, labeled_track_filename))

        self.export_regions_chain(os.path.join(self.all_prefix, silences_filename))

        silences_added_filename = self.file_prefix + "_silences_added.cex"
        silences_added_path = os.path.join(self.all_prefix, silences_added_filename)


        self.export_clan(path=silences_added_path)

        self.clan_file = silences_added_path

        lena_filename = self.file_prefix + "_lena5min.csv"

        self.load_lena(path=os.path.join(self.all_prefix, lena_filename))

        subregions_filename = self.file_prefix + "_subregions.cex"

        self.export_overlaps(path=os.path.join(self.all_prefix, subregions_filename))

    def load_all_cha(self):
        """
        Same principle as load_all(), but refactored to handle the new
        CLAN file format

        This is an all-in-one function that asks for the initial
        CLAN file, and then figures out what the remaining files
        need to be loaded and processed. It assumes that files will
        be named in the following format:


        16_08.cha     <- this is the file to be loaded.
                         the rest will be loaded/generated automatically

        16_08_silences.txt
        16_08_lena5min.csv
        16_08_silences_added.cha
        16_08_subregions.cha

        :return:
        """
        self.clan_formatting_error.grid_remove()
        self.clan_file = tkFileDialog.askopenfilename()

        if self.clan_file != "":
            self.clan_loaded_label.grid(row=1, column=1)

        # pull out the prefix for the path and the filename
        #   e.g.
        #       all_prefix  = /Users/ebergelson/Desktop/Github/SeedlingsBabylab/audiowords/data/input
        #       file_prefix = 16_08
        self.all_prefix = os.path.split(self.clan_file)[0]
        self.file_prefix = os.path.split(self.clan_file)[1][0:5]

        # print "clan file path: " + self.clan_file
        # print "all prefix: " + self.all_prefix
        # print "file prefix: " + self.file_prefix

        labeled_track_filename = "Label_Track.txt"
        silences_filename = self.file_prefix + "_silences.txt"

        # Call load_regions with the Label_Track file
        self.load_regions(path=os.path.join(self.all_prefix, labeled_track_filename))

        self.export_regions_chain(os.path.join(self.all_prefix, silences_filename))

        silences_added_filename = self.file_prefix + "_silences_added.cha"
        silences_added_path = os.path.join(self.all_prefix, silences_added_filename)


        self.export_clan_cha(path=silences_added_path)

        self.clan_file = silences_added_path

        lena_filename = self.file_prefix + "_lena5min.csv"

        self.load_lena(path=os.path.join(self.all_prefix, lena_filename))

        subregions_filename = self.file_prefix + "_subregions.cha"

        self.export_overlaps_cha(path=os.path.join(self.all_prefix, subregions_filename))


    def load_clan(self):
        # get path for initial clan file to be processed,
        # and print a success label to the GUI
        self.clan_formatting_error.grid_remove()
        self.clan_file = tkFileDialog.askopenfilename()
        if self.clan_file != "":
            self.clan_loaded_label.grid(row=1, column=1)

    def export_clan(self, path=""):

        # get path for new/modified clan file
        if path == "":
            self.export_clan_file = tkFileDialog.asksaveasfilename()
        else:
            self.export_clan_file = path
        # We surround the ClanFileParser operations
        # in a try: except: block because in some unlikely
        # circumstances the clan file can be formatted incorrectly,
        # requiring that we stop all operations and report the error.
        try:
            ClanFileParser(self.clan_file, self.export_clan_file)\
                .insert_silences(self.silence_parser.silences)
        except Exception, e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.clan_loaded_label.grid_remove()
            self.clan_formatting_error.grid(row=1, column=1)
            print e.args
            print(exc_type, exc_tb.tb_lineno)

    def export_clan_cha(self, path=""):
        # get path for new/modified clan file
        if path == "":
            self.export_clan_file = tkFileDialog.asksaveasfilename()
        else:
            self.export_clan_file = path
        # We surround the ClanFileParser operations
        # in a try: except: block because in some unlikely
        # circumstances the clan file can be formatted incorrectly,
        # requiring that we stop all operations and report the error.
        try:
            ClanFileParser(self.clan_file, self.export_clan_file)\
                .insert_silences_cha(self.silence_parser.silences)
        except Exception, e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            self.clan_loaded_label.grid_remove()
            self.clan_formatting_error.grid(row=1, column=1)
            print e.args
            print(exc_type, exc_tb.tb_lineno)

    def clear_clan(self):

        self.clan_file = None
        self.clan_loaded_label.grid_remove()

    def clear_silences(self):

        self.silences = None
        self.sound_regions_file = None

        self.silence_list_box.delete(0, END)

    def load_lena(self, path=""):
        self.clear_lena()

        if path == "":
            self.lena_file = tkFileDialog.askopenfilename()
        else:
            self.lena_file = path

        if not self.top_n_region_entry.get():

            self.top_n_missing_label.grid(row=7, column=2)
            #raise Exception("You're missing the top_n entry")
            return
        else:

            self.top_n_missing_label.grid_remove()
            self.overlaps = Overlaps(self.lena_file, int(self.top_n_region_entry.get()))

            for index, x in enumerate(self.overlaps.ranked_meaningful):
                self.meaningful_region_box.insert(index,
                                                  str(x) + "   -   " + str(self.overlaps.meaningful_map[x])+ "   -   " +\
                                                  self.offset_to_hour(x) + "   -   " + \
                                                  str(self.offset_to_millisecond(x)) + " ms ")

            for index, x in enumerate(self.overlaps.ranked_awc_actual):
                self.awc_region_box.insert(index,
                                           str(x) + "   -  " + str(self.overlaps.awc_actual_map[x])+ "   -   " +\
                                           self.offset_to_hour(x) + "   -   " + \
                                           str(self.offset_to_millisecond(x)) + " ms ")

            for index, x in enumerate(self.overlaps.ranked_ctc_actual):
                self.ctc_region_box.insert(index,
                                           str(x) + "   -   " + str(self.overlaps.ctc_actual_map[x])+ "   -   " +\
                                           self.offset_to_hour(x) + "   -   " + \
                                           str(self.offset_to_millisecond(x)) + " ms ")

            for index, x in enumerate(self.overlaps.ranked_cvc_actual):
                self.cvc_region_box.insert(index,
                                           str(x) + "   -  " + str(self.overlaps.awc_actual_map[x])+ "   -   " +\
                                           self.offset_to_hour(x) + "   -   " + \
                                           str(self.offset_to_millisecond(x)) + " ms ")

            for index, x in enumerate(self.overlaps.ranked_ctc_cvc):
                self.ctc_cvc_box.insert(index,
                                        str(x) + "   -  " +str(self.overlaps.ctc_cvc_map[x])+ "   -   " +\
                                        self.offset_to_hour(x) + "   -   " +\
                                        str(self.offset_to_millisecond(x)) + " ms ")

    def clear_lena(self):
        self.lena_file = None
        self.overlaps = None
        self.overlaps_export_file = None

        self.meaningful_region_box.delete(0, END)
        self.awc_region_box.delete(0, END)
        self.ctc_region_box.delete(0, END)
        self.cvc_region_box.delete(0, END)
        self.ctc_cvc_box.delete(0, END)


    def export_overlaps(self, path=""):
        """
        This gets called after the silences have been processed and
        inserted into the clan file. The loaded clan file should be
        this new one with the silences inserted. This function constructs
        a ClanFileParser object, and immediately calls its insert_overlaps()
        method (passing the ranked ctc_cvc offsets, their map, and the
         silence regions from the previous silence inserting step.
        :return:
        """
        if path == "":
            overlaps_export_file = tkFileDialog.asksaveasfilename()
        else:
            overlaps_export_file = path

        ClanFileParser(self.clan_file, overlaps_export_file).\
                        insert_overlaps(self.overlaps.ranked_ctc_cvc,
                                        self.overlaps.ctc_cvc_map, self.silence_parser.silences)

    def export_overlaps_cha(self, path=""):
        """
        This gets called after the silences have been processed and
        inserted into the clan file. The loaded clan file should be
        this new one with the silences inserted. This function constructs
        a ClanFileParser object, and immediately calls its insert_overlaps()
        method (passing the ranked ctc_cvc offsets, their map, and the
         silence regions from the previous silence inserting step.
        :return:
        """
        if path == "":
            overlaps_export_file = tkFileDialog.asksaveasfilename()
        else:
            overlaps_export_file = path

        ClanFileParser(self.clan_file, overlaps_export_file).\
                        insert_overlaps_cha(self.overlaps.ranked_ctc_cvc,
                                        self.overlaps.ctc_cvc_map, self.silence_parser.silences)

    def offset_to_hour(self, offset):

        hours = offset / 12
        minutes = 5 * (offset % 12)

        if minutes < 10:
            return "{}:0{}".format(hours, minutes)
        else:
            return "{}:{}".format(hours, minutes)

    def offset_to_millisecond(self, offset):

        return 5 * offset * 60 * 1000

    def offset_lookup(self, average, map):
        """
        Returns a list of all offsets which have a particular
        average.

        :param average: some value for offset average
        :param map: offset-average mapping
        :return: all the offsets which have "average" as their average
        """
        offsets = []

        for key, value in map.iteritems():
            if value == average:
                offsets.append(key)
        #print "offsets for " + str(average) + "  " + str(offsets)
        milliseconds = [self.offset_to_millisecond(offsets[i]) for i, item in enumerate(offsets)]
        #print "milliseconds: " + str(milliseconds)
        return offsets

if __name__ == "__main__":

    root = Tk()
    MainWindow(root)
    root.mainloop()