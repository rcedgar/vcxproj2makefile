#!/usr/bin/python2

from __future__ import print_function

import os
import sys


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

with open("Makefile", "w") as f:
    def Out(s):
        print(s, file=f)

    Out("UNAME_S := $(shell uname -s)")

    Out("")
    Out("CPPFLAGS := $(CPPFLAGS) -DNDEBUG -pthread")

    if CNames:
        Out("")
        Out("CC = gcc")
        Out("CFLAGS := $(CFLAGS) -O3 -fopenmp -ffast-math -msse -mfpmath=sse")

    if CXXNames:
        Out("")
        Out("CXX = g++")
        Out("CXXFLAGS := $(CXXFLAGS) -O3 -fopenmp -ffast-math -msse -mfpmath=sse")

    Out("")
    Out("LDFLAGS := $(LDFLAGS) -O3 -fopenmp -pthread -lpthread")
    Out("ifeq ($(UNAME_S),Linux)")
    Out("    LDFLAGS += -static")
    Out("endif")

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
    Out(".PHONY: clean")

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

    Out("")
    Out("clean:")
    Out("	-rm -rf o/")
