#!/usr/bin/python2

from __future__ import print_function

import os
import sys


def Die(s):
    print("***ERROR***", sys.argv[0], s, file=sys.stderr)
    sys.exit(1)


LRT = False
DEBUG = False
SVNVER = False

ProjFileName = None
HdrNames = []
for FileName in os.listdir("."):
    if FileName.endswith(".vcxproj"):
        ProjFileName = FileName
    elif FileName.endswith(".h"):
        HdrNames.append(FileName)
if ProjFileName is None:
    print("Project file not found in current directory", file=sys.stderr)

Fields = ProjFileName.split("/")
n = len(Fields)
Name = Fields[n-1]
Fields = Name.split(".")
progname = Fields[0]

f = open("Makefile", "w")
fo = open("Makefile_osx", "w")

Linux = "Linux"
OSX = "OSX"


def Out(s, OS="ALL"):
    if OS == "ALL":
        print(s, file=f)
        print(s, file=fo)
    elif OS == Linux:
        print(s, file=f)
    elif OS == OSX:
        print(s, file=fo)
    else:
        Die("OS %s", OS)


CXXNames = []
CNames = []
with open(ProjFileName) as File:
    for Line in File:
        Line = Line.strip()
        Line = Line.replace('"', '')
        Line = Line.replace(' ', '')
        # <ClCompile Include="betadiv.cpp" />
        if Line.startswith("<ClCompileInclude"):
            Fields = Line.split("=")
            if len(Fields) != 2:
                continue
            FileName = Fields[1]
            FileName = FileName.replace("/>", "")
            if FileName.endswith(".cpp"):
                FileName = FileName.replace(".cpp", "")
                CXXNames.append(FileName)
            elif FileName.endswith(".c"):
                FileName = FileName.replace(".c", "")
                CNames.append(FileName)
        #     <ProjectName>usearch</ProjectName>
        elif Line.startswith("<ProjectName"):
            Line = Line.replace("<ProjectName>", "")
            Line = Line.replace("</ProjectName>", "")
            progname = Line

assert len(CXXNames) > 0 or len(CNames) > 0

binname = progname
if DEBUG:
    binname += "d"

if "/" in binname:
    binname = binname.split("/")[-1]
if "\\" in binname:
    binname = binname.split("\\")[-1]

if CNames:
    Out("CC = gcc", Linux)
    Out("CC = gcc", OSX)
    Out("CFLAGS = -O3 -DNDEBUG -fopenmp -ffast-math -msse -mfpmath=sse")
    Out("")

if CXXNames:
    Out("CXX = g++", Linux)
    Out("CXX = g++", OSX)
    Out("CXXFLAGS = -O3 -DNDEBUG -fopenmp -ffast-math -msse -mfpmath=sse")
    Out("")

Out("LDFLAGS = -O3 -fopenmp -pthread -lpthread -static", Linux)
Out("LDFLAGS = -O3 -fopenmp -pthread -lpthread", OSX)

Out("")
Out("HDRS = \\")
for Name in sorted(HdrNames):
    Out("  %s \\" % Name)

Out("")
Out("OBJS = \\")
for Name in CXXNames:
    Out("  o/%s.o \\" % Name)

for Name in CNames:
    Out("  o/%s.o \\" % Name)

Out("")
Out("o/%s : o/ $(OBJS)" % progname)
Out("	%s $(LDFLAGS) $(OBJS) -o $@%s" % (
    "$(CXX)" if CXXNames else "$(CC)",
    " -lrt" if LRT else "",
))
Out("	strip -d o/%s" % progname)

Out("")
Out("o/ :")
Out("	mkdir -p o/")

if CNames:
    Out("")
    Out("o/%.o : %.c $(HDRS)")
    Out("	$(CC) $(CPPFLAGS) $(CFLAGS) -c -o $@ $<")

if CXXNames:
    Out("")
    Out("o/%.o : %.cpp $(HDRS)")
    Out("	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c -o $@ $<")

f.close()
fo.close()
