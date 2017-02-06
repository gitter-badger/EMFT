from difflib import Differ

if __name__ == '__main__':
    from src.sltp.sltp import SLTP
    import re

    re_cmt = re.compile(' \-\- .*$', re.MULTILINE)
    with open('mission', encoding='iso8859_15') as f:
        parser = SLTP()
        txt = parser.decode("\n".join(f.readlines()[1:]))

    # stripped_txt = re.sub(re_cmt, '', txt)
    new_text = parser.encode(txt)
    with open('mission_out', mode="w", encoding='iso8859_15', newline='') as _f:
        _f.write('mission = ')
        _f.write(new_text)

    d = Differ()

    import zlib


    def crc(fileName):
        prev = 0
        for eachLine in open(fileName, "rb"):
            prev = zlib.crc32(eachLine, prev)
        return "%X" % (prev & 0xFFFFFFFF)


    print(crc('mission_out'))
    print(crc('mission'))

    import hashlib

    a = hashlib.md5(open('mission_out', 'rb').read()).hexdigest()
    b = hashlib.md5(open('mission', 'rb').read()).hexdigest()
    print(a)
    print(b)
    print(a == b)