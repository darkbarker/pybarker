import os
import sys
import pwd
import grp
import platform
import socket
import locale
import pkgutil
from datetime import datetime
from string import Template
from html import escape
# TODO https://gist.github.com/tahajahangir/5275848

output_template = Template("""<!DOCTYPE html>
<html>
<head>
    <style type="text/css">
    body {background-color: #fff; color: #222; font-family: sans-serif;}
    pre {margin: 0; font-family: monospace;}
    a:link {color: #009; text-decoration: none; background-color: #fff;}
    a:hover {text-decoration: underline;}
    table {border-collapse: collapse; border: 0; width: 934px; box-shadow: 1px 2px 3px #ccc;}
    .center {text-align: center;}
    .center table {margin: 1em auto; text-align: left;}
    td, th {border: 1px solid #666; font-size: 75%; vertical-align: baseline; padding: 4px 5px;}
    h1 {font-size: 150%;}
    h2 {font-size: 125%;}
    .p {text-align: left;}
    .e {background-color: #ffffcc; width: 300px; font-weight: bold;}
    .h {background-color: #f2f2f2; font-weight: bold; background: url('http://python.org/images/header-bg2.png') repeat-x;}
    .v {background-color: #f2f2f2; max-width: 300px; overflow-x: auto; word-wrap: break-word;}
    .v i {color: #999;}
    img {float: right; border: 0;}
    </style>
    <title>Python $py_version - pyinfo()</title>
    <meta name="robots" content="noindex,nofollow,noarchive,nosnippet">
</head>
<body><div class="center">
    <table><tr class="h"><td>
        <img src="http://python.org/images/python-logo.gif" alt="Python logo">
        <h1 class="p">Python $py_version</h1>
    </td></tr></table>
    $output
</div></body></html>
""")


def pyinfo():
    output = ""
    output += section_server_info()
    output += section_system()
    output += section_py_internals()
    output += section_os_internals()
    output += section_environ()
    output += section_compression()
    output += section_ldap()
    output += section_socket()
    output += section_multimedia()
    output += section_packages()

    return output_template.substitute(output=output, py_version=platform.python_version())


def make_table(title, data):
    a_name = title.replace(" ", "_").replace(",", "_").lower()
    return '<h2><a name="{}">{}</a></h2><table><tbody>{}</tbody></table>'.format(a_name, title, "".join(
        '<tr><td class="e">{}</td><td class="v">{}</td></tr>'.format(*row) for row in data
    ))


def imported(module):
    """ returns 'enabled' if a module is imported, '-' if it isn't"""
    try:
        if module not in sys.modules:
            __import__(module)
        return "enabled"
    except ImportError:
        return "-"


def _namedtuple(nt):
    # this isnt namedtuple! no iter for items(
    ntstr = str(nt)
    # sys.thread_info(name='pthread', lock='semaphore', version='NPTL 2.36')
    try:
        ntstr = ntstr[ntstr.index("(") + 1:ntstr.rindex(")")]
    except ValueError:
        pass  # ignore not found index/rindex
    return ntstr


def section_system():
    data = []
    data.append(('OS Version', '%s %s' % (platform.system(), platform.release())))
    if hasattr(sys, 'executable'):
        data.append(('Executable', sys.executable))
    data.append(('Python Build Date', platform.python_build()[1]))
    data.append(('Compiler', platform.python_compiler()))
    if hasattr(sys, 'api_version'):
        data.append(('Python API', sys.api_version))
    sysname, nodename, release, osversion, machine = os.uname()
    data.append(('OS Uname', '%s %s %s %s %s' % (sysname, nodename, release, osversion, machine)))

    # Unix Platforms
    if hasattr(platform, 'libc_ver'):
        data.append(('Libc version', " ".join(platform.libc_ver())))  # (lib, version)

    # Linux Platforms
    # The fields NAME, ID, and PRETTY_NAME are always defined according to the standard.
    if hasattr(platform, 'freedesktop_os_release'):
        fr = platform.freedesktop_os_release()
        data.append(('Freedesktop os release', fr["PRETTY_NAME"]))

    data.append(('Architecture', " ".join(platform.architecture())))  # (bits, linkage)
    data.append(('Platform', platform.platform()))
    data.append(('Python implementation', platform.python_implementation()))
    if platform.processor():  # An empty string is returned if the value cannot be determined.
        data.append(('Processor', platform.processor()))

    return make_table('System', data)


def section_server_info():
    data = []
    data.append(('Hostname', socket.gethostname()))
    data.append(('Domain', socket.getfqdn()))
    try:
        data.append(('IP Address', socket.gethostbyname(socket.gethostname())))
    except Exception:
        pass
    data.append(('Local time', str(datetime.now())))
    data.append(('UTC time', str(datetime.utcnow())))
    return make_table('Server Info', data)


def get_packages():
    return list([modname for _importer, modname, ispkg in pkgutil.walk_packages(onerror=lambda x:x) if ispkg and '.' not in modname])


def section_py_internals():
    data = []
    if hasattr(sys, 'builtin_module_names'):
        data.append(('Built-in Modules', ', '.join(sys.builtin_module_names)))

    if hasattr(sys, 'stdlib_module_names'):  # New in version 3.10
        data.append(('Stdlib modules', ', '.join(sys.stdlib_module_names)))

    data.append(('Byte Order', sys.byteorder + ' endian'))

    # Deprecated since version 3.2: Use getswitchinterval() instead.
    if hasattr(sys, 'getcheckinterval'):
        data.append(('Check Interval', sys.getcheckinterval()))
    # Return the interpreter’s “thread switch interval”; see setswitchinterval().
    # New in version 3.2.
    if hasattr(sys, 'getswitchinterval'):
        data.append(('Thread switch Interval', sys.getswitchinterval()))

    if hasattr(sys, 'getfilesystemencoding'):
        data.append(('File System Encoding', sys.getfilesystemencoding()))
    if hasattr(sys, 'getdefaultencoding'):
        data.append(('Default Encoding', sys.getdefaultencoding()))

    data.append(('Maximum Integer Size', str(sys.maxsize) + ' (%s)' % str(hex(sys.maxsize)).upper().replace("X", "x")))
    if hasattr(sys, 'getrecursionlimit'):
        data.append(('Maximum Recursion Depth', sys.getrecursionlimit()))

    # When this variable is set to an integer value, it determines the maximum number of levels of traceback information
    # printed when an unhandled exception occurs. The default is 1000.
    if hasattr(sys, 'tracebacklimit'):
        data.append(('Maximum Traceback Limit', sys.tracebacklimit))
    else:
        data.append(('Maximum Traceback Limit', '1000(default)'))

    data.append(('Maximum Unicode Code Point', sys.maxunicode))
    if hasattr(locale, 'getdefaultlocale'):
        data.append(('Default Locale', locale.getdefaultlocale()))

    data.append(('Installed Packages', ', '.join(sorted(get_packages()))))

    if hasattr(sys, 'base_exec_prefix'):  # New in version 3.3
        data.append(('Base exec prefix', sys.base_exec_prefix))
    if hasattr(sys, 'base_prefix'):  # New in version 3.3
        data.append(('Base prefix', sys.base_prefix))
    data.append(('Exec prefix', sys.exec_prefix))
    data.append(('Prefix', sys.prefix))

    data.append(('Path', "; ".join(sys.path)))

    data.append(('Flags', _namedtuple(sys.flags)))

    if hasattr(sys, 'hash_info'):  # New in version 3.2.
        data.append(('Hash info', _namedtuple(sys.hash_info)))

    if hasattr(sys, 'int_info'):  # New in version 3.1.
        data.append(('Int info', _namedtuple(sys.int_info)))

    if hasattr(sys, 'thread_info'):  # New in version 3.3.
        data.append(('Thread info', _namedtuple(sys.thread_info)))

    if hasattr(sys, 'float_info'):
        data.append(('Float info', _namedtuple(sys.float_info)))
    if hasattr(sys, 'float_repr_style'):  # New in version 3.1.
        data.append(('Float repr style', sys.float_repr_style))

    # Return the number of memory blocks currently allocated by the interpreter, regardless of their size.
    if hasattr(sys, 'getallocatedblocks'):  # New in version 3.4.
        data.append(('Allocated blocks', sys.getallocatedblocks()))

    # Returns the current value for the integer string conversion length limitation. See also set_int_max_str_digits().
    if hasattr(sys, 'get_int_max_str_digits'):  # New in version 3.10.7.
        data.append(('Int max str digits', sys.get_int_max_str_digits()))

    data.append(('Copyright', sys.copyright))

    return make_table('Python Internals', data)


def userinfo(uid):
    return '%s (%s)' % (uid, pwd.getpwuid(uid)[0])


def groupinfo(gid):
    return '%s (%s)' % (gid, grp.getgrgid(gid)[0])


def section_os_internals():
    data = []
    if hasattr(os, 'getcwd'):
        data.append(('Current Working Directory', os.getcwd()))

    if hasattr(os, 'getegid'):  # Availability: Unix.
        data.append(('Effective Group ID', groupinfo(os.getegid())))
    if hasattr(os, 'geteuid'):  # Availability: Unix.
        data.append(('Effective User ID', userinfo(os.geteuid())))
    if hasattr(os, 'getgid'):  # Availability: Unix.
        data.append(('Group ID', groupinfo(os.getgid())))
    if hasattr(os, 'getgroups'):  # Availability: Unix.
        data.append(('Group Membership', ', '.join(map(groupinfo, os.getgroups()))))

    if hasattr(os, 'linesep'):
        data.append(('Line Seperator', repr(os.linesep)[1:-1]))
    if hasattr(os, 'pathsep'):
        data.append(('Path Seperator', os.pathsep))

    if hasattr(os, 'getloadavg'):
        data.append(('Load Average', ', '.join(str(round(x, 2)) for x in os.getloadavg())))

    try:
        if hasattr(os, 'getpid') and hasattr(os, 'getppid'):
            data.append(('Process ID', ('%s (parent: %s)' % (os.getpid(), os.getppid()))))
    except Exception:
        pass
    if hasattr(os, 'getuid'):
        data.append(('User ID', userinfo(os.getuid())))

    # Return the id of the current process group.
    if hasattr(os, 'getpgrp'):  # Availability: Unix.
        data.append(('Process group', os.getpgrp()))

    data.append(('OS name', os.name))

    # Return the filename corresponding to the controlling terminal of the process.
    if hasattr(os, 'ctermid'):  # Availability: Unix.
        data.append(('Controlling terminal', os.ctermid()))

    if hasattr(os, 'getlogin'):  # Availability: Unix, Windows.
        data.append(('Login', os.getlogin()))

    if hasattr(os, 'get_exec_path'):  # New in version 3.2.
        data.append(('Exec path', os.get_exec_path()))

    if hasattr(os, 'cpu_count'):  # New in version 3.4.
        data.append(('CPU count', os.cpu_count() or "?"))  # None if indeterminable

    return make_table('OS Internals', data)


def section_environ():
    envvars = list(os.environ.keys())
    envvars.sort()
    data = []
    for envvar in envvars:
        data.append((envvar, escape(str(os.environ[envvar]))))
    return make_table("Environment", data)


def section_compression():
    return make_table('Compression and archiving', [
        ('SQLite3', imported('sqlite3')),
        ('Bzip2 Support', imported('bz2')),
        ('Gzip Support', imported('gzip')),
        ('Tar Support', imported('tarfile')),
        ('Zip Support', imported('zipfile')),
        ('Zlib Support', imported('zlib')),
        ('Lzma Support', imported('lzma')),
    ])


def section_ldap():
    try:
        import ldap
    except (ImportError):
        return ""
    return make_table('LDAP support', [
        ('Python-LDAP Version', ldap.__version__),
        ('API Version', ldap.API_VERSION),
        ('Default Protocol Version', ldap.VERSION),
        ('Minimum Protocol Version', ldap.VERSION_MIN),
        ('Maximum Protocol Version', ldap.VERSION_MAX),
        ('SASL Support (Cyrus-SASL)', ldap.SASL_AVAIL),
        ('TLS Support (OpenSSL)', ldap.TLS_AVAIL),
        ('Vendor Version', ldap.VENDOR_VERSION)
    ])


def section_socket():
    data = []

    data.append(('IPv6 Support', getattr(socket, 'has_ipv6', False)))
    data.append(('Fqdn', socket.getfqdn()))
    data.append(('Default Timeout', socket.getdefaulttimeout() or "no"))

    # Return True if the platform supports creating a TCP socket which can handle both IPv4 and IPv6 connections.
    if hasattr(socket, 'has_dualstack_ipv6'):  # New in version 3.8.
        data.append(("Has dualstack ipv6", socket.has_dualstack_ipv6()))

    # list of network interface information
    if hasattr(socket, 'if_nameindex'):  # New in version 3.3.
        data.append(("Network interfaces", ", ".join(ni[1] for ni in socket.if_nameindex())))  # [(1, 'lo'), (2, 'eno1')]

    # Testing for SSL support
    # To test for the presence of SSL support in a Python installation, user code should use the following idiom:
    try:
        import ssl
    except ImportError:
        data.append(("SSL Support", False))
    else:
        data.append(("SSL Support", True))

        # New in version 3.2.
        data.append(("Openssl version", getattr(ssl, "OPENSSL_VERSION", "?")))

        # Whether the OpenSSL library has built-in support for the Application-Layer Protocol Negotiation TLS extension as described in RFC 7301.
        # New in version 3.5.
        data.append(("Has ALPN", getattr(ssl, "HAS_ALPN", "?")))

        # Whether the OpenSSL library has built-in support not checking subject common name and SSLContext.hostname_checks_common_name is writeable.
        # New in version 3.7.
        data.append(("Has never_check CN", getattr(ssl, "HAS_NEVER_CHECK_COMMON_NAME", "?")))

        # Whether the OpenSSL library has built-in support for the Elliptic Curve-based Diffie-Hellman key exchange. This should be true unless the feature was explicitly disabled by the distributor.
        # New in version 3.3.
        data.append(("Has ECDH", getattr(ssl, "HAS_ECDH", "?")))
        # Whether the OpenSSL library has built-in support for the Server Name Indication extension (as defined in RFC 6066).
        # New in version 3.2.
        data.append(("Has SNI", getattr(ssl, "HAS_SNI", "?")))
        # Whether the OpenSSL library has built-in support for the Next Protocol Negotiation as described in the Application Layer Protocol Negotiation. When true, you can use the SSLContext.set_npn_protocols() method to advertise which protocols you want to support.
        # New in version 3.3.
        data.append(("Has NPN", getattr(ssl, "HAS_NPN", "?")))

        # Whether the OpenSSL library has built-in support for the SSL 2.0 protocol.
        # New in version 3.7.
        data.append(("Has SSLv2", getattr(ssl, "HAS_SSLv2", "?")))
        # Whether the OpenSSL library has built-in support for the SSL 3.0 protocol.
        # New in version 3.7.
        data.append(("Has SSLv3", getattr(ssl, "HAS_SSLv3", "?")))
        # Whether the OpenSSL library has built-in support for the TLS 1.0 protocol.
        # New in version 3.7.
        data.append(("Has TLSv1", getattr(ssl, "HAS_TLSv1", "?")))
        # Whether the OpenSSL library has built-in support for the TLS 1.1 protocol.
        # New in version 3.7.
        data.append(("Has TLSv1_1", getattr(ssl, "HAS_TLSv1_1", "?")))
        # Whether the OpenSSL library has built-in support for the TLS 1.2 protocol.
        # New in version 3.7.
        data.append(("Has TLSv1_2", getattr(ssl, "HAS_TLSv1_2", "?")))
        # Whether the OpenSSL library has built-in support for the TLS 1.3 protocol.
        # New in version 3.7.
        data.append(("Has TLSv1_3", getattr(ssl, "HAS_TLSv1_3", "?")))

        # List of supported TLS channel binding types. Strings in this list can be used as arguments to SSLSocket.get_channel_binding().
        if hasattr(ssl, 'CHANNEL_BINDING_TYPES'):  # New in version 3.3.
            data.append(("Channel binding types", ", ".join(ssl.CHANNEL_BINDING_TYPES)))

    return make_table('Socket, SSL', data)


def section_multimedia():
    return make_table('Multimedia support', [
        ('AIFF Support', imported('aifc')),
        ('Color System Conversion', imported('colorsys')),
        ('curses Support', imported('curses')),
        ('IFF Chunk Support', imported('chunk')),
        ('Image Header Support', imported('imghdr')),
        ('OSS Audio Device Support', imported('ossaudiodev')),
        ('Raw Audio Support', imported('audioop')),
        ('SGI RGB Support', imported('rgbimg')),
        ('Sound Header Support', imported('sndhdr')),
        ('Sun Audio Device Support', imported('sunaudiodev')),
        ('Sun AU Support', imported('sunau')),
        ('Wave Support', imported('wave')),
    ])


def section_packages():
    data = []
    try:
        import pkg_resources
    except ImportError:
        return ""
    for pkg in pkg_resources.working_set:
        assert isinstance(pkg, pkg_resources.Distribution)
        data.append((pkg.project_name, pkg.version if pkg.has_version() else "[unknown]"))
    return make_table("Miscellaneous External Modules (Site Packages)", sorted(data, key=lambda a: a[0].lower()))


if __name__ == "__main__":
    def make_table(title, data):
        return "===== {} =====\n{}\n\n".format(title, "\n".join(
            "{:30} {}".format(*row) for row in data
        ))
    output_template = Template("$output")
    print(pyinfo())
