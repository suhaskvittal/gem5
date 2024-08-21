"""
    author: Suhas Vittal
"""

import m5
from m5.objects import *

# Define system and clock frequency
# Voltage domain is left untouched (default power model).
sys = System()
sys.clk_domain = SrcClockDomain()
sys.clk_domain.clock = "1GHz"
sys.clk_domain.voltage_domain = VoltageDomain()
# Declare timing mode (common) + components (memory, cpu).
sys.mem_mode = "timing"
sys.mem_ranges = [AddrRange("512MB")]
sys.cpu = X86TimingSimpleCPU()
sys.membus = SystemXBar()  # system-wide memory bus
# Define no caches.
sys.cpu.icache_port = sys.membus.cpu_side_ports
sys.cpu.dcache_port = sys.membus.cpu_side_ports

# X86 ONLY-------
sys.cpu.createInterruptController()
sys.cpu.interrupts[0].pio = sys.membus.mem_side_ports
sys.cpu.interrupts[0].int_requestor = sys.membus.cpu_side_ports
sys.cpu.interrupts[0].int_responder = sys.membus.mem_side_ports

sys.mem_ctrl = MemCtrl()
sys.mem_ctrl.dram = DDR3_1600_8x8()
sys.mem_ctrl.dram.range = sys.mem_ranges[0]
sys.mem_ctrl.port = sys.membus.mem_side_ports

# Setup binary.
binary = "tests/test-progs/hello/bin/x86/linux/hello"
sys.workload = SEWorkload.init_compatible(binary)

proc = Process()
proc.cmd = [binary]
sys.cpu.workload = proc
sys.cpu.createThreads()

# Instantiate system and begin execution.
rt = Root(full_system=False, system=sys)
m5.instantiate()

print("========= SIM START ==========")
ee = m5.simulate()
print(f"=== Exiting @ tick {m5.curTick()} because {ee.getCause()}")
