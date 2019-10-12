from SpirentSLC import SLC
from SpirentSLC.Execution import *

import re
import io
import sys
import logging
import collections
import json
import time
import math
import random
from datetime import datetime

param = Params({
    'DUT': 'SGW',
    'TFTP_SERVER': '10.62.224.10',
    'Landslide_IP': 'http://10.62.224.23:8080/api/',
    'Platform': 'Nokia',
    'ElasticSearch_Index': 'rjil5',
    'URL': 'https://10.62.224.11',
    'Release': '2.0',
})


def main(slc, logger, status):
    procedure_result = '{}'
    STC_Python = slc.open('STC_Python')
    Cisco1 = STC_Python.CSR_Router_ffsp.open()
    Cisco1.command('enable ', properties={ 'applicationProperties.promptProperties.stepPrompts':{ 'autoPrompt1':{ 'Content':'Password: ' } } })
    Cisco1.command(properties={ 'command.body':'SrqvrrOjrgE=', 'command.body.masked':'true' })
    Cisco1.command('terminal length 0')
    STCv1 = STC_Python.STCv_ffsp.open(properties={ 'config':'project://STC_Python/configuration/STCv_Router_Etherent_Traffic_Testing.xml', 'configureCustom16bitFilter.endOfRange':'ffff', 'configureCustom16bitFilter.mask':'ffff' })
    STCv1.startArpNdOnAllDevices()
    time.sleep(5.00000)
    STCv1.startArpNdOnAllStreamBlocks()
    Cisco1.command('clear counters')
    Cisco1.command()
    STCv1.startGenerator()
    time.sleep(60.0000)
    STCv1.stopGenerator()
    response = STCv1.showResults('BasicTrafficResults "Basic Counters" 1')
    handle_step_results(response, status, logger)
    TX1 = None
    TX2 = None
    if response.result == 'success':
        extracted = []
        for line in response.text.split('\n'):
            match = re.search('^Port //\\d+/\\d+\\s+(\\d+)\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+$', line, flags=re.M)
            if match:
                extracted.append(match.group(1))
        if isinstance(extracted, (list, tuple)) and len(extracted) == 1:
            TX1 = next(iter(extracted))
        else:
            TX1 = extracted
        extracted = []
        for line in response.text.split('\n'):
            match = re.search('^Port //\\d+/\\d+\\s+(\\d+)\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+$', line, flags=re.M)
            if match:
                extracted.append(match.group(1))
        if isinstance(extracted, (list, tuple)) and len(extracted) == 1:
            TX2 = next(iter(extracted))
        else:
            TX2 = extracted
        extracted = []
        for line in response.text.split('\n'):
            match = re.search('^Port //\\d+/\\d+\\s+\\d+\\s+(\\d+)\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+$', line, flags=re.M)
            if match:
                extracted.append(match.group(1))
        if not isinstance(extracted, (list, tuple)):
            extracted = [extracted]
        for value in extracted:
            if value >= TX2:
                logger.info('Port1/1 Ethernet Traffic Stats Tx=Rx')
                status.pass_test_if_not_already_failed(log=logger)
            else:
                logger.error('Port1/1 Ethernet Traffic Stats Tx!=Rx')
                status.fail_test(log=logger)
        extracted = []
        for line in response.text.split('\n'):
            match = re.search('^Port //\\d+/\\d+\\s+\\d+\\s+(\\d+)\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+\\d+\\s+$', line, flags=re.M)
            if match:
                extracted.append(match.group(1))
        if not isinstance(extracted, (list, tuple)):
            extracted = [extracted]
        for value in extracted:
            if value >= TX1:
                logger.info('Port1/2 Ethernet Traffic Stats Tx=Rx')
                status.pass_test_if_not_already_failed(log=logger)
            else:
                logger.error('Port1/2 Ethernet Traffic Stats Tx!=Rx')
                status.fail_test(log=logger)
    Cisco1.command('show interfaces gigabitEthernet 2 accounting ')
    Cisco1.command('show interfaces gigabitEthernet 3 accounting')
    STCv1.close()
    Cisco1.close()
    return procedure_result


if __name__ == '__main__':
    status = Status()
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    begin = time.time()
    logger.info('Execution started')
    try:
        with SLC.init(host='localhost:9000') as slc:
            main(slc, logger, status)
    except TestTermination:
        pass
    except:
        status.fail_test()
        raise
    finally:
        logger.info('Execution completed (%ds)' % int(time.time()-begin))
        logger.info('Status: %s' % status.get())
