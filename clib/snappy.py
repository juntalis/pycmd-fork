from ctypes import *
from .import is_x64
import os.path as _path

# Utility declaration.
__dir__ = _path.abspath(_path.dirname(__file__))

# Our Snappy DLL
_snappy = CDLL(_path.join(__dir__, 'snappy.x64.dll')) if is_x64() else CDLL(_path.join(__dir__, 'snappy.dll'))

##########
# Consts #
##########

SNAPPY_OK = 0
SNAPPY_INVALID_INPUT = 1
SNAPPY_BUFFER_TOO_SMALL = 2

#############
# Functions #
#############

_compress = _snappy.snappy_compress
_compress.restype = c_int
_compress.argtypes = [c_char_p, c_size_t, c_char_p, POINTER(c_size_t)]

_uncompress = _snappy.snappy_uncompress
_uncompress.restype = c_int
_uncompress.argtypes = [c_char_p, c_size_t, c_char_p, POINTER(c_size_t)]

_maxclen = _snappy.snappy_max_compressed_length
_maxclen.restype = c_size_t
_maxclen.argtypes = [c_size_t]

_ulen = _snappy.snappy_uncompressed_length
_ulen.restype = c_int
_ulen.argtypes = [c_char_p, c_size_t, POINTER(c_size_t)]

_validate = _snappy.snappy_validate_compressed_buffer
_validate.restype = c_int
_validate.argtypes = [c_char_p, c_size_t]

#####################
# Exception Classes #
#####################

class InvalidInputException(Exception):
	pass

#####################
# Function Wrappers #
#####################

def compress(inbuf):
	""" Given a string, unicode string, char array, or file object, return a snappy-compressed string. """
	t = type(inbuf)
	if t == str or t == unicode: inbuf = create_string_buffer(inbuf)
	elif t == file: inbuf = create_string_buffer(inbuf.read())
	elif t != c_char_p: raise NotImplementedError("Don't know how to process instance of type: %s" % t)
	inlen = sizeof(inbuf)
	outlen = c_size_t(_maxclen(inlen))
	outbuf = create_string_buffer(outlen.value)
	result = _compress(inbuf, inlen, outbuf, byref(outlen))
	if result == SNAPPY_OK:
		return outbuf.raw[0:outlen.value]
	elif result == SNAPPY_INVALID_INPUT:
		raise InvalidInputException('Failed to compress input!')
	elif result == SNAPPY_BUFFER_TOO_SMALL:
		raise Exception('This should not happen.')


def uncompress(inbuf):
	""" Given a string, unicode string, char array, or file object, return the contents uncompressed. """
	t = type(inbuf)
	if t == str or t == unicode: inbuf = create_string_buffer(inbuf)
	elif t == file: inbuf = create_string_buffer(inbuf.read())
	elif t != c_char_p: raise NotImplementedError("Don't know how to process instance of type: %s" % t)
	inlen = sizeof(inbuf)
	outlen = c_size_t(0)
	result = _ulen(inbuf, inlen, byref(outlen))
	if result != SNAPPY_OK: raise InvalidInputException('Failed to compress input!')
	outbuf = create_string_buffer(outlen.value)
	result = _uncompress(inbuf, outlen, outbuf, byref(outlen))
	if result == SNAPPY_OK:
		return outbuf.raw[0:outlen.value]
	elif result == SNAPPY_INVALID_INPUT:
		raise InvalidInputException('Failed to uncompress input!')
	elif result == SNAPPY_BUFFER_TOO_SMALL:
		raise Exception('This should not happen.')
	return outbuf.raw


def loadf(fpath):
	f = open(fpath, 'rb')
	buf = uncompress(f)
	f.close()
	return buf


def savef(fpath, buf):
	f = open(fpath, 'wb')
	f.write(compress(buf))
	f.close()
