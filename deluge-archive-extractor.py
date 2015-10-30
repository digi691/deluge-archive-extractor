#!/usr/bin/env python

import os
from sys import argv
from subprocess import call
from sys import exit
from syslog import syslog

syslog('The script started running')

UNRAR = "/usr/bin/unrar"
UNZIP = "/usr/bin/unzip"


class Torrent:
    def __init__(self, t_id, t_name, t_path):
        self.id = t_id
        self.name = t_name
        self.path = t_path
        self.base_archive_file = ""
        self.capable_archive_types = self.find_supported_archive_types()
        self.archive_type = self.find_archive_type()


    def find_supported_archive_types(self):
        system_supported_types = []
        if os.path.isfile(UNRAR):
            system_supported_types.append("RAR")
        elif os.path.isfile(UNZIP):
            system_supported_types.append("ZIP")
        else:
            syslog('Supported archive formats are not installed, exiting!')
            exit(1)
        return system_supported_types

    def find_archive_type(self):
        if self.rar_detect():
            return "RAR"
        elif self.zip_detect():
            return "ZIP"
        else:
            syslog('deluge-archive-extractor: Did not find a base archive file to extract in %s' % self.path)
            exit(0)

    def rar_detect(self):
        torrent_dir_contents = os.listdir(self.path)
        found_rar = False
        for item in torrent_dir_contents:
            if item.split(".")[-1].lower() == "rar":
                found_rar = True
                self.base_archive_file = item
                break
        return found_rar

    def zip_detect(self):
        torrent_dir_contents = os.listdir(self.path)
        found_zip = False
        for item in torrent_dir_contents:
            if item.split(".")[-1].lower() == "zip":
                found_zip = True
                self.base_archive_file = item
                break
        return found_zip


class Extracter:
    def __init__(self, torrent_object):
        self.torrent = torrent_object

    def extract(self):
        if self.torrent.archive_type == "RAR":
            self.unrar_extract()
        else:
            self.unzip_extract()

    def unrar_extract(self):
        file = self.torrent.path + "/" + self.torrent.base_archive_file
        print file
        exitcode = call([UNRAR,
                         "x",
                         file,
                         self.torrent.path
                         ])
        if exitcode == 0:
            syslog(
                "deluge-archive-extractor: extracted %s into %s" % (
                    self.torrent.path + "/" + self.torrent.base_archive_file, self.torrent.path))
        else:
            syslog("deluge-archive-extractor: unrar failed with exit code %s" % exitcode)

    def unzip_extract(self):
        file = self.torrent.path + "/" + self.torrent.base_archive_file
        exitcode = call([UNZIP, file, "-d", self.torrent.path])
        if exitcode == 0:
            syslog(
                "extracted %s into %s" % ("%s/%s" % (self.torrent.path, torrent.base_archive_file), self.torrent.path))
        else:
            syslog("deluge-archive-extractor: unzip failed with exit code %s" % exitcode)


def main():
    torrent = Torrent(argv[1], argv[2], argv[3])
    extracter = Extracter(torrent)
    extracter.extract()


if __name__ == "__main__":
    main()
    syslog("deluge-archive-extractor: finished")
    exit(0)
