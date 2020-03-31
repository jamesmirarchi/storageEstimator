import math
import click
from decimal import *
# Asumptions
#       * 0.90 of disk because of disk match (0.9313%) and reserved free space
#       * 0.035 as an average for PCAP to ES
#       * 0.05 as a max for PCAP to ES

class BitConversion():
    def __init__(self, BYTE):
        self.byte = BYTE

    @property
    def create(self):
        try:
            self.byte = self.byte * 8
        except ValueError as err:
            print(err)
        return self.byte

class ReverseEstimate:
    def __init__(self, Gbps):
        self.gbps = Gbps

    def calculation(self):
        bps = (self.gbps)*1024*1024*1024/8
        return bps

class WireSpeed(BitConversion):
    def __init__(self, BYTE, rate):
        super().__init__(BYTE)
        self.rate = (1/ rate)

    def __repr__(self):
        return(f'{Decimal(self.estimate())}')

    def estimate(self):
        Gbps = (((self.create/self.rate)/1024)/1024/1024)
        #return (math.ceil(Gbps))
        return Gbps

class DiskEstimator(WireSpeed):
    def __init__(self, BYTE, rate, retentionDays, diskSize, disksPerMachine, percentageTLS, averageGbpsMachine, esReplicas, esRetention):
        super().__init__(BYTE, rate)
        self.retentionDays = retentionDays
        self.diskSize = diskSize
        self.disksPerMachine = disksPerMachine
        self.percentageTLS = percentageTLS
        self.averageGbpsMachine = averageGbpsMachine
        self.esReplicas = esReplicas
        self.esRetention = esRetention

    def __repr__(self):
        return(f'[CAPTURE] Estimated Space required: {self.storageEstimate()}  TB \n[SEARCH] Estimated Space Required: {self.esStorageEstimate()} TB')

    @property
    def captureDay(self):
        return (self.percentageTLS * self.estimate() * self.retentionDays * 24 * 60 * 60/8)
    @property
    def captureDiskInput(self):
        return (self.diskSize * 0.90)
    @property
    def captureDisks(self):
        return (self.disksPerMachine)
    @property
    def captureMin(self):
        return (self.estimate()/self.averageGbpsMachine)

    def storageEstimate(self):
        return (math.ceil(self.captureDay/1000))

    @property
    def esCaptureDay(self):
        return (self.esReplicas * 0.035 * self.estimate() * 24 * 60 * 60 / 8)

    def esStorageEstimate(self):
        return (math.ceil(self.esCaptureDay/1000))

class main():
    def __init__(self):
        self.bits = int()
        self.bytes = int()
        self.rate = int()
        self.Gbps = float()
        self.retentionDays = int()
        self.diskSize = int()
        self.disksPerMachine = int()
        self.percentageTLS = int()
        self.averageGbpsMachine = int()
        getcontext().prec = 10
        self.userInput()

    def tls_mapping(self, tls):
        mapper = {
            50: 0.55,
            40: 0.65,
            30: 0.75,
            20: 0.80,
            10: 0.90,
            0: 1.0
        }
        return mapper.get(tls, 1)

    def es_rep_mapper(self, es):
        mapper = {
            0 : 1,
            1 : 2,
            2 : 3
        }
        return mapper.get(es, 1)

    def tb_mapping(self, tb):
        mapper = {
            1: 1000,
            2: 2000,
            3: 3000,
            4: 4000,
            6: 6000,
            8: 8000,
            10:10000,
            12:12000,
            14:14000,
            16:16000,
        }
        return mapper.get(tb, 1000)

    def defineFreq(self):
        self.rate = (int(input('[DATATYPE][DATARATE] Please enter Hz rate (i.e. 1) : ')))
        while True:
            try:
                validRate = int(self.rate)
            except ValueError:
                print('[DATATYPE][DATARATE] Please enter rate as an integer.')
                continue
            if self.rate != None:
                return self.rate
            else:
                print('[DATATYPE][DATARATE] Please enter rate as an integer.')
                continue

    def formatCalc(self):
        bitsbytesChoice = {'bits', 'bytes'}
        while True:
            b = click.prompt('[DATATYPE] Please enter data type', type=click.Choice(bitsbytesChoice, False))
            try:
                validCheck = (str(b))
            except ValueError:
                print('[ERROR] Please enter either bytes or bits')
                continue
            if (validCheck and (b == 'bytes' or b == 'BYTES')):
                while True:
                    try:
                        self.bytes = int(input('[DATATYPE] Please enter bytes size: '))
                    except ValueError:
                        print('[ERROR] Please enter an integer or float')
                        continue
                    if self.bytes != None:
                        return self.bytes
                    else:
                        print('[ERROR] Please enter an integer or float')
                        continue
            elif (validCheck and (b == 'bits' or b == 'BITS')):
                while True:
                    try:
                        self.bytes = ((int(input('[DATATYPE] Please enter bits size: '))) / 8)
                    except ValueError:
                        print('[ERROR] Please enter either an integer or float.')
                        continue
                    if self.bytes != None:
                        return (self.bytes)
                    else:
                        print('[ERROR] Please enter either an integer or float.')
                        continue
            else:
                print('[ERROR] Please enter either bytes or bits')
                continue

    def dataRetention(self):
        while True:
            try:
                self.retentionDays = click.prompt('[DATATYPE][DATARATE][RETENTION] Please enter number of days for retention (i.e. 14)', type=int)
            except ValueError:
                print('[ERROR] Please enter days as an integer.')
                continue
            if self.retentionDays != None:
                return self.retentionDays
            else:
                print('[ERROR] Please enter days as an integer.')
                continue

    def hddSize(self):
        while True:
            try:
                diskSize = click.prompt(
                    '[DATATYPE][DATARATE][RETENTION][SIZE] Please enter the size of HDDs to be used in TB (i.e. 4)', type=int)
            except ValueError:
                print('[ERROR] Please enter HDD size as an integer.')
                continue
            if self.tb_mapping(diskSize) != None:
                self.diskSize = self.tb_mapping(diskSize)
                return self.diskSize
            else:
                print('[ERROR] Please enter HDD size as an integer.')
                continue

    def numOfDisks(self):
        while True:
            try:
                self.disksPerMachine = click.prompt(
                    '[DATATYPE][DATARATE][RETENTION][SIZE][HDD#] Please enter the number of HDDs to be used per storage device (i.e. 8)', type=int)
            except ValueError:
                print('[ERROR] Please enter HDD number as an integer.')
                continue
            if self.disksPerMachine != None:
                return self.disksPerMachine
            else:
                print('[ERROR] Please enter HDD number as an integer.')
                continue

    def tlsPercentage(self):
        while True:
            try:
                TLS = click.prompt(
                    '[DATATYPE][DATARATE][RETENTION][SIZE][HDD#][TLS] Please enter the percentage of TLS traffic (0, 10, 20, 25, 30, 40, 50)', type=click.IntRange(0,50),show_choices=False)
            except ValueError:
                print('[ERROR] Please enter TLS percentage as an integer.')
                continue
            if TLS != None:
                self.percentageTLS = self.tls_mapping(TLS)
                self.TLS = TLS
                return self.percentageTLS
            else:
                print('[ERROR] Please enter either (0, 10, 20, 25, 30, 40, 50) TLS percentage.')
                continue

    def avgGbpsMachine(self):
        while True:
            try:
                self.averageGbpsMachine = click.prompt(
                    '[DATATYPE][DATARATE][RETENTION][SIZE][HDD#][TLS][AVG] Please enter the average Gbps per machine: ', type=click.IntRange(0,10))
            except ValueError:
                print('[ERROR] Please enter average Gbps per machine as an integer.')
                continue
            if self.averageGbpsMachine != None:
                return self.averageGbpsMachine
            else:
                print('[ERROR] Please enter average Gbps per machine as an integer.')
                continue

    def esReplication(self):
        while True:
            try:
                ES = click.prompt(
                    '[DATATYPE][DATARATE][RETENTION][SIZE][HDD#][TLS][AVG][ESR] Please enter number of ES replicas (0, 1, 2)',
                    type=click.IntRange(0, 2), show_choices=False)
            except ValueError:
                print('[ERROR] Please enter number of ES replicas as an integer.')
                continue
            if ES != None:
                self.ES = self.es_rep_mapper(ES)
                return self.ES
            else:
                print('[ERROR] Please enter either (0, 10, 20, 25, 30, 40, 50) TLS percentage.')
                continue

    def esDays(self):
        while True:
            try:
                self.retentionDaysES = click.prompt('[DATATYPE][DATARATE][RETENTION][SIZE][HDD#][TLS][AVG][ES-REP][ES-RET] Please enter number of days for ES retention (i.e. 14)', type=int)
            except ValueError:
                print('[ERROR] Please enter days as an integer.')
                continue
            if self.retentionDaysES != None:
                return self.retentionDaysES
            else:
                print('[ERROR] Please enter days as an integer.')
                continue

    def userInput(self):
        while True:
            gbpsChoice = {'Y', 'N'}
            try:
                calc = click.prompt('Do you already have Gbps calculation?', type=click.Choice(gbpsChoice,True))
            except TypeError as err:
                continue
            if ((calc == 'y' or calc =='Y')):
                self.Gbps = click.prompt('Enter Gbps (i.e. 0.45): ', type=float)
                self.bytes = (self.Gbps) * 1024 * 1024 * 1024 / 8
                self.bits = (self.bytes*8)
                self.rate = 1
                break
            else:
                self.Gbps = None
                self.formatCalc()
                self.defineFreq()
                self.bits = self.bytes * 8
                if self.Gbps == None:
                    self.Gbps = WireSpeed(self.bytes, self.rate)
                else:
                    pass
                break
        self.dataRetention()
        self.hddSize()
        self.numOfDisks()
        self.tlsPercentage()
        self.avgGbpsMachine()
        self.esReplication()
        self.esDays()
        print(f'Packet Size [Bits]: {self.bits}')
        print(f'Packet Size [Bytes]: {self.bytes}')
        print(f'Data Rate [Hz]: {self.rate}')
        print(f'Estimated Gbps: {self.Gbps}')
        print(f'Data Retention [Days]: {self.retentionDays}')
        print(f'HDD size used [TB]: {self.diskSize}')
        print(f'Number of HDD per machine: {self.disksPerMachine}')
        print(f'Estimated TLS traffic [%]: {self.TLS}')
        print(f'Average Gbps per machine: {self.averageGbpsMachine}')
        print(DiskEstimator(self.bytes, self.rate, self.retentionDays, self.diskSize, self.disksPerMachine, self.percentageTLS, self.averageGbpsMachine, self.ES, self.retentionDaysES))

if __name__ == '__main__':
    main()
