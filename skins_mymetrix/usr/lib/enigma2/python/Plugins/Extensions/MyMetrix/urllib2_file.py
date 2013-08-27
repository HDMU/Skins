"""
extend urllib2 to enable uploading files using multipart/form-data

I was looking for something to make me able to upload files to my photo web site (http://gallery.menalto.com/).
Inspired by http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146306

Example:

import urllib2_file
import urllib2

data = { 'foo':         'bar',
         'form_name':    open("/lib/libc.so.1")
        }
(send something like: 'Content-Disposition: form-data; name="form_name"; filename="form_name";' )

Or if you want to specify a different filename:
data = { 'foo':         'bar',
         'form_name':   { 'fd':          open('/lib/libresolv.so.2',
                          'filename':    'libresolv.so'}
        }
(send something like: 'Content-Disposition: form-data; name="form_name"; filename="libresolv.so";' )

u = urllib2.urlopen('http://site.com/path/upload.php', data)


THANKS to:
- bug fix: kosh @T aesaeion.com
- HTTPS support : Ryan Grow <ryangrow @T yahoo.com>
 - upload is now done with chunks (Adam Ambrose)
 - UTF-8 filenames are now allowed (Eli Golovinsky)
 - File object is no more mandatory, Object only needs to have seek() read() attributes (Eli Golovinsky)
 - StringIO workaround (Laurent Coustet), does not work with cStringIO

 Also modified by Adam Ambrose (aambrose @T pacbell.net) to write data in
chunks (hardcoded to CHUNK_SIZE for now), so the entire contents of the file
don't need to be kept in memory.

"""
__author__ = 'Fabien SEISEN'
__license__ = 'Python Software Foundation License version 2'
__url__ = 'http://fabien.seisen.org/python/'
import httplib
import mimetools
import mimetypes
import os
import os.path
import socket
import stat
import sys
import urllib
import urllib2
CHUNK_SIZE = 65536

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


def send_data(v_vars, v_files, boundary, sock = None):
    """Parse v_vars, v_files and create a buffer with HTTP multipart/form-data
    if sock is set, send data to it
        v_vars = {"key": "value"}
        v_files = {"filename" : open("path/to/file"}
    """
    buffer_len = 0
    for k, v in v_vars:
        buffer = ''
        buffer += '--%s\r\n' % boundary
        buffer += 'Content-Disposition: form-data; name="%s"\r\n' % k
        buffer += '\r\n'
        buffer += v + '\r\n'
        if sock:
            sock.send(buffer)
        buffer_len += len(buffer)

    for k, v in v_files:
        name = k
        filename = k
        if isinstance(v, dict):
            if v.has_key('fd'):
                fd = v['fd']
            else:
                raise TypeError("if value is dict, it must have keys 'fd' and 'filename'")
            if v.has_key('filename'):
                filename = v['filename']
            else:
                raise TypeError("if value is dict, it must have keys 'fd' and 'filename'")
        else:
            fd = v
        if not hasattr(fd, 'seek'):
            raise TypeError('file descriptor MUST have seek attribute')
        if not hasattr(fd, 'read'):
            raise TypeError('file descriptor MUST have read attribute')
        fd.seek(0)
        if hasattr(fd, 'fileno'):
            file_size = os.fstat(fd.fileno())[stat.ST_SIZE]
        else:
            file_size = 0
            while True:
                chunk = fd.read(CHUNK_SIZE)
                if chunk:
                    file_size += len(chunk)
                else:
                    break

        fd.seek(0)
        if isinstance(filename, unicode):
            filename = filename.encode('UTF-8')
        buffer = ''
        buffer += '--%s\r\n' % boundary
        buffer += 'Content-Disposition: form-data; name="%s"; filename="%s";\r\n' % (name, filename)
        buffer += 'Content-Type: %s\r\n' % get_content_type(filename)
        buffer += 'Content-Length: %s\r\n' % file_size
        buffer += '\r\n'
        buffer_len += len(buffer)
        if sock:
            sock.send(buffer)
            if hasattr(fd, 'seek'):
                fd.seek(0)
        if sock:
            while True:
                chunk = fd.read(CHUNK_SIZE)
                if not chunk:
                    break
                if sock:
                    sock.send(chunk)

        buffer_len += file_size

    buffer = '\r\n'
    buffer += '--%s--\r\n' % boundary
    buffer += '\r\n'
    if sock:
        sock.send(buffer)
    buffer_len += len(buffer)
    return buffer_len


class newHTTPHandler(urllib2.BaseHandler):

    def http_open(self, req):
        return self.do_open(httplib.HTTP, req)

    def do_open(self, http_class, req):
        data = req.get_data()
        v_files = []
        v_vars = []
        if req.has_data() and type(data) != str:
            if hasattr(data, 'items'):
                data = data.items()
            else:
                try:
                    if len(data) and not isinstance(data[0], tuple):
                        raise TypeError
                except TypeError:
                    ty, va, tb = sys.exc_info()
                    raise TypeError, 'not a valid non-string sequence or mapping object', tb

            for k, v in data:
                if isinstance(v, dict):
                    if not v.has_key('fd'):
                        raise TypeError("if value is dict, it must have keys 'fd' and 'filename")
                    if not v.has_key('filename'):
                        raise TypeError("if value is dict, it must have keys 'fd' and 'filename")
                    v_files.append((k, v))
                elif hasattr(v, 'read'):
                    v_files.append((k, v))
                else:
                    v_vars.append((k, v))

        if len(v_vars) > 0 and len(v_files) == 0:
            data = urllib.urlencode(v_vars)
            v_files = []
            v_vars = []
        host = req.get_host()
        if not host:
            raise urllib2.URLError('no host given')
        h = http_class(host)
        if req.has_data():
            h.putrequest(req.get_method(), req.get_selector())
            if 'Content-type' not in req.headers:
                if len(v_files) > 0:
                    boundary = mimetools.choose_boundary()
                    l = send_data(v_vars, v_files, boundary)
                    h.putheader('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
                    h.putheader('Content-length', str(l))
                else:
                    h.putheader('Content-type', 'application/x-www-form-urlencoded')
                    if 'Content-length' not in req.headers:
                        h.putheader('Content-length', '%d' % len(data))
        else:
            h.putrequest(req.get_method(), req.get_selector())
        scheme, sel = urllib.splittype(req.get_selector())
        sel_host, sel_path = urllib.splithost(sel)
        h.putheader('Host', sel_host or host)
        for name, value in self.parent.addheaders:
            name = name.capitalize()
            if name not in req.headers:
                h.putheader(name, value)

        for k, v in req.headers.items():
            h.putheader(k, v)

        try:
            h.endheaders()
        except socket.error as err:
            raise urllib2.URLError(err)

        if req.has_data():
            if len(v_files) > 0:
                l = send_data(v_vars, v_files, boundary, h)
            elif len(v_vars) > 0:
                data = urllib.urlencode(v_vars)
                h.send(data)
            else:
                h.send(data)
        code, msg, hdrs = h.getreply()
        fp = h.getfile()
        if code == 200:
            resp = urllib.addinfourl(fp, hdrs, req.get_full_url())
            resp.code = code
            resp.msg = msg
            return resp
        else:
            return self.parent.error('http', req, fp, code, msg, hdrs)


urllib2._old_HTTPHandler = urllib2.HTTPHandler
urllib2.HTTPHandler = newHTTPHandler

class newHTTPSHandler(newHTTPHandler):

    def https_open(self, req):
        return self.do_open(httplib.HTTPS, req)


urllib2.HTTPSHandler = newHTTPSHandler
