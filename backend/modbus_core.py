from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import (
    ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
)
import threading

def start_modbus(port: int = 1502):
    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [0] * 64),
        co=ModbusSequentialDataBlock(0, [False] * 64),
        hr=ModbusSequentialDataBlock(0, [0] * 64),
        ir=ModbusSequentialDataBlock(0, [0] * 64),
    )
    ctx = ModbusServerContext(store, single=True)
    thr = threading.Thread(
        target=StartTcpServer,
        args=(ctx,),
        kwargs=dict(address=("127.0.0.1", port)),
        daemon=True,
    )
    thr.start()
    return ctx
