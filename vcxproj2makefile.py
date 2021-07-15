#!/usr/bin/python2

from __future__ import print_function
import sys
import os
import re

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
if ProjFileName == None:
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
def Out(s, OS = "ALL"):
    global f, fo
    if OS == "ALL":
        print(s, file=f)
        print(s, file=fo)
    elif OS == "Linux":
        print(s, file=f)
    elif OS == "OSX":
        print(s, file=fo)
    else:
        Die("OS %s", OS)

CPPNames = []
CNames = []
File = open(ProjFileName)
while 1:
    Line = File.readline()
    if len(Line) == 0:
        break
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
            CPPNames.append(FileName)
        elif FileName.endswith(".c"):
            FileName = FileName.replace(".c", "")
            CNames.append(FileName)
    #     <ProjectName>usearch</ProjectName>
    elif Line.startswith("<ProjectName"):
        Line = Line.replace("<ProjectName>", "")
        Line = Line.replace("</ProjectName>", "")
        progname = Line

assert len(CPPNames) > 0 or len(CNames) > 0

binname = progname
if DEBUG:
    binname += "d"

if binname.find("/") > 0:
    Fields = binname.split("/")
    N = len(Fields)
    binname = Fields[N-1]
if binname.find("\\") > 0:
    Fields = binname.split("\\")
    N = len(Fields)
    binname = Fields[N-1]

# CNames CPPNames

Out("CPP = ccache g++", Linux)
Out("CPP = g++", OSX)
Out("CPPOPTS = -fopenmp -ffast-math -msse -mfpmath=sse -O3 -DNDEBUG -c")

Out("")
Out("CC = ccache gcc", Linux)
Out("CC = gcc", OSX)
Out("CCOPTS = -fopenmp -ffast-math -msse -mfpmath=sse -O3 -DNDEBUG -c")
Out("")

Out("LNK = g++")
Out("LNKOPTS = -O3 -fopenmp -pthread -lpthread -static", Linux)
Out("LNKOPTS = -O3 -fopenmp -pthread -lpthread", OSX)

Out("")
Out("HDRS = \\")
n = len(HdrNames)
for i in range(0, n):
    Name = HdrNames[i]
    Out("  %s \\" % Name)

Out("")
Out("OBJS = \\")
n = len(CPPNames)
for i in range(0, n):
    Name = CPPNames[i]
    Out("  o/%s.o \\" % Name)

n = len(CNames)
for i in range(0, n):
    Name = CNames[i]
    Out("  o/%s.o \\" % Name)

Out("")
Out("%s : o/ $(OBJS)" % progname)
if LRT:
    Out("	$(LNK) $(LNKOPTS) $(OBJS) -o o/%s -lrt" % progname)
else:
    Out("	$(LNK) $(LNKOPTS) $(OBJS) -o o/%s" % progname)
Out("	strip -d o/%s" % progname)

Out("")
Out("o/ :")
Out("	mkdir -p o/")

for Name in CNames:
    Out("")
    Out("o/%s.o : %s.c $(HDRS)" % (Name, Name))
    Out("	$(CC) $(CCOPTS) -o o/%s.o %s.c" % (Name, Name))

for Name in CPPNames:
    Out("")
    Out("o/%s.o : %s.cpp $(HDRS)" % (Name, Name))
    Out("	$(CPP) $(CPPOPTS) -o o/%s.o %s.cpp" % (Name, Name))
