#
# Makefile for creating a PyCmd.zip binary distribution
# Requires:
#	* Python >= 2.7 (32-bit or 64-bit)
#	* MinGW (make, rm, cp etc) and python in the %PATH%
#	* cx_freeze, pywin32 and pefile installed in the Python dist
#
# Author: Horea Haitonic
#
RM = rm -f
CP = cp
MV = mv
ZIP = zip
SHELL = cmd

SRC = PyCmd.py InputState.py DirHistory.py common.py completion.py console.py fsm.py
SRC_TEST = common_tests.py

PYTHONHOME_W32 = C:\Python27
PYTHONHOME_W64 = C:\Python27-amd64

PYTHON_W32 = (set PYTHONHOME=$(PYTHONHOME_W32)) && "$(PYTHONHOME_W32)\python.exe"
PYTHON_W64 = (set PYTHONHOME=$(PYTHONHOME_W64)) && "$(PYTHONHOME_W64)\python.exe"

ifndef BUILD_INFO
	BUILD_INFO = $(shell WMIC os GET LocalDateTime | grep -v Local | cut -c 1-8)
endif

.PHONY: all
all: 
	$(MAKE) clean
	$(MAKE) dist_w32 
	$(MAKE) clean
	$(MAKE) dist_w64

doc: pycmd_public.py
	$(PYTHON_W32) -c "import pycmd_public, pydoc; pydoc.writedoc('pycmd_public')"

dist_w32: clean $(SRC) doc
	echo build_info = '$(BUILD_INFO)' > buildinfo.py
	$(PYTHON_W32) setup.py build
	$(MV) build\exe.win32-2.7 PyCmd
	$(CP) README.txt PyCmd
	(echo Release $(BUILD_INFO): && echo. && type NEWS.txt) > PyCmd\NEWS.txt
	$(ZIP) -r PyCmd-$(BUILD_INFO)-w32.zip PyCmd

dist_w64: clean $(SRC) doc
	echo build_info = '$(BUILD_INFO)' > buildinfo.py
	$(PYTHON_W64) setup.py build
	$(MV) build\exe.win-amd64-2.7 PyCmd
	$(CP) README.txt PyCmd
# cx_freeze on Py64 fails to include pywintypes27.dll:
	$(CP) $(PYTHONHOME_W64)\Lib\site-packages\pywin32_system32\pywintypes27.dll PyCmd
	(echo Release $(BUILD_INFO): && echo. && type NEWS.txt) > PyCmd\NEWS.txt
	$(ZIP) -r PyCmd-$(BUILD_INFO)-w64.zip PyCmd

.PHONY: clean
clean:
	$(RM) buildinfo.*
	$(RM) $(SRC:%.py=%.pyc)
	$(RM) pycmd_public.html
	cd tests && $(RM) $(SRC_TEST:%.py=%.pyc) && $(RM) __init__.pyc
	$(RM) -r build PyCmd
