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
    STCv1 = STC_Python.STCv_ffsp.open(properties={ 'configureCustom16bitFilter.endOfRange':'ffff', 'configureCustom16bitFilter.mask':'ffff' })
    STCv1.startArpNdOnAllDevices()
    STCv1.startDevices()
    response = STCv1.showResults('Ospfv2Results "OSPFv2" 1', properties={ 'eventHandlers':{ 'OnRepeatStepMaxCountExceeded':[ { 'actionId':'DeclareExecutionIssue', 'actionProperties.message':'Waited for 200 Seconds ROUTER OSPF Adjecency not coming UP' }, { 'actionId':'FailTest' }, { 'actionId':'ExitExecution' } ] } })
    handle_step_results(response, status, logger)
    if response.result == 'success':
        extracted = response.query('AdjacencyStatus("Port //1/1")')
        if not isinstance(extracted, (list, tuple)):
            extracted = [extracted]
        for value in extracted:
            if value == "FULL":
                pass
            else:
                logger.info('Waiting for ROUTER Adjacency Status to be FULL')
                # unsupported action type: RepeatStep
        extracted = response.query('AdjacencyStatus("Port //1/2")')
        if not isinstance(extracted, (list, tuple)):
            extracted = [extracted]
        for value in extracted:
            if value == "FULL":
                pass
            else:
                logger.info('Waiting for ROUTER Adjacency Status to be FULL')
                # unsupported action type: RepeatStep
    response1 = STCv1.showResults('Ospfv2Results "OSPFv2" 1')
    handle_step_results(response1, status, logger)
    if response1.result == 'success':
        extracted = response1.query('AdjacencyStatus("Port //1/2")')
        if not isinstance(extracted, (list, tuple)):
            extracted = [extracted]
        for value in extracted:
            if value == "FULL":
                logger.info('Port1/2 Router OSPF "State=Backup" and "Adjacency=FULL"')
                status.pass_test_if_not_already_failed(log=logger)
            else:
                logger.error('Port1/2 Router OSPF "Adjacency=DOWN"')
                status.fail_test(log=logger)
        extracted = response1.query('AdjacencyStatus("Port //1/1")')
        if not isinstance(extracted, (list, tuple)):
            extracted = [extracted]
        for value in extracted:
            if value == "FULL":
                logger.info('Port1/1 Router OSPF "State=Backup" and "Adjacency=FULL"')
                status.pass_test_if_not_already_failed(log=logger)
            else:
                logger.error('Port1/1 Router OSPF "Adjacency=DOWN"')
                status.fail_test(log=logger)
    Cisco1.command('show ip ospf ')
    response2 = Cisco1.command('show ip ospf neighbor ')
    handle_step_results(response2, status, logger)
    if response2.result == 'success':
        extracted = response2.query('State_by_Neighbor_ID("192.0.0.1")')
        if not isinstance(extracted, (list, tuple)):
            extracted = [extracted]
        for value in extracted:
            if value == "FULL/BDR":
                logger.info('On Router OSPF Neighbor-192.0.0.1 is UP (FULL/BDR)')
                status.pass_test_if_not_already_failed(log=logger)
            else:
                logger.error('On Router OSPF Neighbor-192.0.0.1 is DOWN')
                status.fail_test(log=logger)
        extracted = response2.query('State_by_Neighbor_ID("192.0.0.2")')
        if not isinstance(extracted, (list, tuple)):
            extracted = [extracted]
        for value in extracted:
            if value == "FULL/BDR":
                logger.info('On Router OSPF Neighbor-192.0.0.2 is UP (FULL/BDR)')
                status.pass_test_if_not_already_failed(log=logger)
            else:
                logger.error('On Router OSPF Neighbor-192.0.0.2 is DOWN')
                status.fail_test(log=logger)
    Cisco1.command('clear counters')
    Cisco1.command()
    STCv1.startArpNdOnAllStreamBlocks()
    # new comment
    STCv1.startGenerator()
    time.sleep(10.0000)
    STCv1.stopGenerator()
    STCv1.showResults('BasicTrafficResults "Basic Counters" 1')
    STCv1.clearResults('BasicTrafficResults')
    STCv1.startGenerator()
    time.sleep(60.0000)
    STCv1.stopGenerator()
    response3 = STCv1.showResults('BasicTrafficResults "Basic Counters" 1')
    handle_step_results(response3, status, logger)
    TX1 = None
    TX2 = None
    if response3.result == 'success':
        extracted = response3.query('TotalTxCount_Frames_("Port //1/1")')
        if isinstance(extracted, (list, tuple)) and len(extracted) == 1:
            TX1 = next(iter(extracted))
        else:
            TX1 = extracted
        extracted = response3.query('TotalTxCount_Frames_("Port //1/2")')
        if isinstance(extracted, (list, tuple)) and len(extracted) == 1:
            TX2 = next(iter(extracted))
        else:
            TX2 = extracted
        extracted = response3.query('TotalRxCount_Frames_("Port //1/1")')
        if not isinstance(extracted, (list, tuple)):
            extracted = [extracted]
        for value in extracted:
            if value >= TX2:
                logger.info('Port1/1 OSPF Traffic Stats Tx=Rx')
                status.pass_test_if_not_already_failed(log=logger)
            else:
                logger.error('Port1/1 OSPF Traffic Stats Tx!=Rx')
                status.fail_test(log=logger)
        extracted = response3.query('TotalRxCount_Frames_("Port //1/2")')
        if not isinstance(extracted, (list, tuple)):
            extracted = [extracted]
        for value in extracted:
            if value >= TX1:
                logger.info('Port1/2 OSPF Traffic Stats Tx=Rx')
                status.pass_test_if_not_already_failed(log=logger)
            else:
                logger.error('Port1/2 OSPF Traffic Stats Tx!=Rx')
                status.fail_test(log=logger)
    Cisco1.command('show ip route ospf 1')
    Cisco1.command('show interfaces stats ')
    Cisco1.command('show interfaces gigabitEthernet 2 accounting ')
    Cisco1.command('show interfaces gigabitEthernet 3 accounting')
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
