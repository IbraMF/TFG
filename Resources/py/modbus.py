#!/usr/bin/env python3
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusServerContext
import psutil, time, threading


class CpuDataBlock(ModbusSequentialDataBlock):

    async def async_getValues(self, fx, address, count=1):
        return super().getValues(address, count)

    async def async_setValues(self, fx, address, values):
        super().setValues(address, values)


block = CpuDataBlock(0, [0] * 10)  # HR0-9
context = ModbusServerContext(slaves={1: block}, single=False)


def update_regs():
    while True:
        cpu = int(psutil.cpu_percent() * 10)
        frequency = int(psutil.cpu_freq().current * 10)
        ram = psutil.virtual_memory()
        ram_percent = int((ram.total - ram.available) / ram.total * 100 * 10)
        disk = int(psutil.disk_usage('C:\\').percent * 10)
        values = [cpu, frequency, ram_percent, disk]
        print(
            f"cpu_usage = {cpu/10}   cpu_freq = {frequency/10}   ram_usage = {ram_percent/10}   disk_usage = {disk/10}")

        block.setValues(0, values)
        time.sleep(1)


threading.Thread(target=update_regs, daemon=True).start()

#slave id 1
StartTcpServer(context, address=("0.0.0.0", 1502))
