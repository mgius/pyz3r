from .misc import misc
from .exceptions import alttprException

import itertools
import hashlib

class patch:
    def apply(rom, patches):
        for patch in patches:
            offset = int(list(patch.keys())[0])
            patch_values = list(patch.values())[0]
            for idx, value in enumerate(patch_values):
                rom[offset+idx] = value
        return rom

    def heart_speed(speed='half'):
        if speed==None:
            speed='normal'
        sbyte = {
            'off': 0,
            'double': 16,
            'normal': 32,
            'half': 64,
            'quarter': 128,
        }
        patch = [{
            '1572915': [sbyte[speed]]
        }]
        return patch

    def heart_color(color='red'):
        if speed==None:
            speed='red'
        cbyte = {
            'blue': [44, 13],
            'green': [60, 25],
            'yellow': [40, 9],
            'red': [36, 5],
        }
        byte =  cbyte[color][0]
        file_byte =  cbyte[color][1]
        patch = [
            {'457246': [byte]},
            {'457248': [byte]},
            {'457250': [byte]},
            {'457252': [byte]},
            {'457254': [byte]},
            {'457256': [byte]},
            {'457258': [byte]},
            {'457260': [byte]},
            {'457262': [byte]},
            {'457264': [byte]},
            {'415073': [file_byte]},
        ]
        return patch

    def music(music=True):
        if music:
            return []
        else:
            patch = [
                {'851480': [0]},
                {'851649': [0]},
                {'851968': [0, 0]},
                {'852199': [196, 88]}
            ]
            return patch

    def sprite(spr):
        if spr[:4] == [90, 83, 80, 82]:
            #stolen from VT's code
            gfx_offset = spr[12] << 24 | spr[11] << 16 | spr[10] << 8 | spr[9]
            palette_offset = spr[18] << 24 | spr[17] << 16 | spr[16] << 8 | spr[15]
            patch = [
                {'524288': spr[gfx_offset:gfx_offset+28671]},
                {'905992': spr[palette_offset:palette_offset+120]},
                {'912885': spr[palette_offset+120:palette_offset+120+3]}
            ]
        #Else treat it like a SPR file instead
        else:
            patch = [
                {'524288': spr[0:28671]},
                {'905992': spr[28672:28791]},
                {
                    '912885': [
                        spr[28726],
                        spr[28727],
                        spr[28756],
                        spr[28757],
                    ]
                }
            ]
        return patch

    def checksum(rom):
        sum_of_bytes = sum(rom[:32731]) + sum(rom[32736:])
        checksum = (sum_of_bytes + 510) & 65535
        inverse = checksum ^ 65535
        patch = [
            {
                '32732': [
                    inverse & 255,
                    inverse >> 8,
                    checksum & 255,
                    checksum >> 8,
                ]
            }
        ]
        return patch

    def expand(rom, newlenmb=None):
        newlen = int(newlenmb) * 1024 * 1024
        if len(rom) > newlen:
            raise alttprException('ROM is already larger than {bytes}'.format(
                bytes=newlen
            ))
        diff = len(rom) - newlen
        if diff > 0:
            rom[newlen] = 0
        else:
            rom.extend(itertools.repeat(0, -diff))
            rom.append(0)
        return rom

class romfile:
    def read(srcfilepath):
        expected_rom_sha256='794e040b02c7591b59ad8843b51e7c619b88f87cddc6083a8e7a4027b96a2271'
        sha256_hash = hashlib.sha256()
        with open(srcfilepath,"rb") as f:
            for byte_block in iter(lambda: f.read(4096),b""):
                sha256_hash.update(byte_block)
        if not sha256_hash.hexdigest() == expected_rom_sha256:
            raise alttprException('Expected checksum "{expected_rom_sha256}", got "{actual_checksum}" instead.  Verify the source ROM is an unheadered Japan 1.0 Link to the Past ROM.'.format(
                expected_rom_sha256=expected_rom_sha256,
                actual_checksum=sha256_hash.hexdigest()
            ))
        fr = open(srcfilepath,"rb")
        baserom_array = list(fr.read())
        fr.close()
        return baserom_array

    def write(rom, dstfilepath):
        fw = open(dstfilepath,"wb")
        patchrom = bytes()
        for idx, chunk_array in enumerate(misc.chunk(rom,256)):
            patchrom += bytes(chunk_array)
        fw.write(patchrom)
        fw.close

