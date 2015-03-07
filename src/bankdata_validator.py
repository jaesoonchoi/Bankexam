# -*- coding: utf-8 -*-

import os, hashlib, random, struct
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64encode
from Crypto import Random

class BankDataValidator(object):

    def __init__(self,txaCons):
        self.txaCons = txaCons

    def checkDataFormat(self,_Dialog):
        self._datafile = _Dialog.fileName
        self.txaCons.append('\''+self._datafile+'\' 파일을 분석합니다.')

        try:
            _file = open(self._datafile,encoding='cp949')
            _file.readline()
            self._fileEnc = 'cp949'
        except UnicodeDecodeError:
            try:
                _file.close()
                _file = open(self._datafile,encoding='utf-8')
                _file.readline()
                self._fileEnc = 'utf-8'
            except UnicodeDecodeError:
                self.txaCons.append('텍스트 파일이 아닙니다. 암호화 되어 있거나 엑셀파일 인지 확인 하세요.')
                return
        _file.close()

        _Dialog.fileEnc = self._fileEnc
        self.lstData = []
        headerColumnNum = len(_Dialog._header.split('\t'))
        fileLineCnt = 1
        for _line in open(self._datafile,encoding=self._fileEnc):
            self.lstData.append(_line)
            if len(_line.split('\t')) == 1:
                self.txaCons.append(str(fileLineCnt)+'행이 탭(TAB)으로 분리되어 있지 않습니다.')
                self.txaCons.append(_line.replace('\t',','))
                return
            if headerColumnNum != len(_line.split('\t')):
                self.txaCons.append(str(fileLineCnt)+'행의 컬럼개수('+str(len(_line.split('\t'))) +
                                    ')가 정의된 헤더 컬럼개수('+str(headerColumnNum)+')와 일치하지 않습니다.')
                self.txaCons.append(_line.replace('\t',','))
                return
            fileLineCnt += 1
        self.txaCons.append('파일은 '+str(fileLineCnt)+'행이고 컬럼은 '+str(headerColumnNum)+'개 입니다.')
        #self.encryptTest()
        self.decrpytTest()
        return self.lstData



    def encryptTest(self):
        public_key = '-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA17wdLrNvfamehn41nOMO\nmo8lZYq5cIuQC+8va8hNVlER8ZG4bJpxHbc9AAbqT9HZqVCLrgcB4iJDH/IZZNgv\nrcLkQDKNra0YYJex8SItgYyjm92Nrw7epnQG4ffmvrTMwR/TnPYA528G/Wkft+Di\neY0szly77MT/4KC/TChFLSDuXHuy/oHDtWcYs0gZZfcPrTku5jHyzfE3FTvYhBRO\nMExRjiXdrISOUOMbQc5VkAP4c/Bqb9u76hZs+uGUFg94M1DgI3/Ao0G6e/Di8F0h\nI9dIEeOldIQsHFzT+rnSIA124mFK0GjoP9Q29O514rAFY8JqkBo2R5mutreFnayT\nzQIDAQAB\n-----END PUBLIC KEY-----'

        #aes_key = b64encode(os.urandom(32)).decode(self._fileEnc)
        aes_key = os.urandom(32)
        encFilename = self._datafile + '.enc'
        #filehash = hashlib.md5('\n'.join(self.lstData).encode(self._fileEnc)).hexdigest()
        #filehash = hashlib.md5(open(self._datafile,encoding=self._fileEnc).read().encode(self._fileEnc)).hexdigest()
        #hashId = hashlib.md5()
        filehash = hashlib.md5(repr(open(self._datafile,encoding=self._fileEnc).read()).encode()).hexdigest()
        rsakey = RSA.importKey(public_key)
        rsakey = PKCS1_OAEP.new(rsakey)
        encKey = rsakey.encrypt(aes_key)
        outFile = open(encFilename, 'wb+')
        outFile.write(bytes(filehash,self._fileEnc))
        #outFile.write(b64encode(encKey).decode(self._fileEnc))
        outFile.write(encKey)

        #iv = ''.join(chr(random.randint(0,0xFF)) for i in range(16))
        iv = Random.new().read(16)
        encryptor = AES.new(aes_key, AES.MODE_CBC, iv)
        filesize = os.path.getsize(self._datafile)
        chunksize = 64*1024

        with open(self._datafile, 'rb') as infile:
            outFile.write(struct.pack('<Q', filesize))
            outFile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' ' * (16 - len(chunk) % 16)
                outFile.write(encryptor.encrypt(chunk))

        outFile.close()
        self.txaCons.append(encFilename + ' 파일 암호화가 성공하였습니다.')

    def validateIntegrity(self,orighash, destfilepath):            # Validate the integrity of the received file
        #desthash = hashlib.md5(open(destfilepath, "rb").read()).hexdigest()        # calculate the received and decrypted file's MD5 checksum
        desthash = hashlib.md5(repr(open(destfilepath,encoding=self._fileEnc).read()).encode()).hexdigest()
        desthash = bytes(desthash,self._fileEnc)
        if(orighash==desthash):
            return True                         # If the original hash matches the decrypted file's hash, return true
        else:
            #os.system("rm "+destfilepath)        # If two hashed do not match, file is either corrupted or modified in the middle. So delete the file..
            return False                        # ..and return false

    def decrpytTest(self):
        dec_filename = self._datafile+'.dec'
        inFile = open(self._datafile+'.enc','rb')
        chunksize = 64*1024
        hash = inFile.read(32)
        encAESKey=inFile.read(256)
        private_key = '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA17wdLrNvfamehn41nOMOmo8lZYq5cIuQC+8va8hNVlER8ZG4\nbJpxHbc9AAbqT9HZqVCLrgcB4iJDH/IZZNgvrcLkQDKNra0YYJex8SItgYyjm92N\nrw7epnQG4ffmvrTMwR/TnPYA528G/Wkft+DieY0szly77MT/4KC/TChFLSDuXHuy\n/oHDtWcYs0gZZfcPrTku5jHyzfE3FTvYhBROMExRjiXdrISOUOMbQc5VkAP4c/Bq\nb9u76hZs+uGUFg94M1DgI3/Ao0G6e/Di8F0hI9dIEeOldIQsHFzT+rnSIA124mFK\n0GjoP9Q29O514rAFY8JqkBo2R5mutreFnayTzQIDAQABAoIBAHUgJ4PcXZKPDYcd\nbIQh7iLRxs7rUyScUPd5w3g0BnDvkNtjbwpfizxD6LVkC8CMQS0gksVH/qjES0dD\nzK+og7JGFmAYUj1RteNzWGN/V893CLitv6ekXhNm+Pmj+r3dMTFE00HrebAs4lGg\nylytlqfBkurzBABXMEjHXTS+xFfsAqSe8WPqgEnHvkP/uGRt6yAOTdCJq4fkrjku\nq3T7D+Bv13yhi+yw6hWZ3/EXhH3QcqpBsktRTpNisoKFABjSYVBFNr80P4ectH4m\nYNE9MjgvHKX0JODR2zIt/n79zO78bwoHRkCXB5WD6hVYWyUAOsSNceL09zvgLcKM\nk+NToKECgYEA4A0N+lYYmT/mwKgD55bfJedwSQroIlpNYEbjc19D0ew6naZgkT7L\n7PH5Ti17ZceSYomD+pu4XnUSmlfoYx1kWyH1Kaxl7uoU01Zq6yQHE39G++WX6hH+\nBisyyZHC65dkmyJ4o4YJ30TjQ8/fMNHL7OjeOV+145CIFFs5hTOuGAkCgYEA9n96\nkj0Fb8H9VSHHeBDLaAVVc0IVuvE3qA4MnUQjFVUwDvISz9dBppVUB3dBzweWDYhB\nIl5pYtkmodqdXb0vZai/ns45LSKK1Li7G/+MizY6bZ8Vf5a1zonqr2UvXcLgsLTr\nha8wzpGKTcE+CGV8QQZMGq4+yxuSF1sB+T+n5qUCgYBuI9zAOHzFMVWlVbL9sPwn\nrPtU3Oi6onuxHYgImkdDtgYmo7iLDjy/UUCGPvOPWClNCV743n4m6RRpDVfvCW7h\nIfNcNiSx6x6ruaq7xy03V3U0tWwVpBylOa0wy9fvarAJV0vIz0ahHENAfbqxTCEc\naGl9+N/4a3+JykKfiYVGyQKBgQC7hL76APHh0vGlkczsydnziBs5U0y0qkxszENM\nYElQMT4eIImvE1IeJ/uEsnSdymecY8spGimRySBagLS2WvVzoKwlYzyb2WtD6ERv\nSDjirp5ERoFUTpKATOr8Az3FVjsYMon5aQz4GD/eZuOJ/6pGzUOYCHY8jPzWR6V4\nt7RDAQKBgBSJoOpCTX5VE1LvahRzwiIWKusJOk/hfpMLhCcm85W11hNp3oppKBoD\nQIZzYaNb1UTBtCv2ADFsoglUdQ/h9x/wQQFSS92evGwQv/TW/z5lP5o2/OEiqwy2\num7Q19tqKKkYd9+9/unz8Vg9IjpzAtwqPViwXG9qu9e6bSQLfNoJ\n-----END RSA PRIVATE KEY-----'

        rsakey = RSA.importKey(private_key)
        rsakey = PKCS1_OAEP.new(rsakey)
        aes_key = rsakey.decrypt(encAESKey)
        origsize = struct.unpack('<Q', inFile.read(struct.calcsize('Q')))[0]
        iv = inFile.read(16)
        decryptor = AES.new(aes_key, AES.MODE_CBC, iv)

        with open(dec_filename, 'wb') as outfile:
            while True:
                chunk = inFile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))


            outfile.truncate(origsize)

        if(self.validateIntegrity(hash, dec_filename)):
            self.txaCons.append('해독 파일의 무결성 검증이 성공하였습니다.')
        else:
            self.txaCons.append('해독 파일의 무결성 검증이 실패하였습니다.')



if __name__ == '__main__':
    print('Bank Data Validator')