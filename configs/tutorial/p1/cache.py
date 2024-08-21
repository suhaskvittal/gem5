"""
    author: Suhas Vittal
"""

import m5
from m5.objects import *


class L1Cache(Cache):
    def __init__(self, size: str):
        super().__init__()
        self.size = size
        self.assoc = 2
        self.tag_latency = 2
        self.data_latency = 2
        self.response_latency = 2
        self.mshrs = 4
        self.tgts_per_mshr = 20


class L2Cache(Cache):
    size = "256kB"
    assoc = 8
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    mshrs = 20
    tgts_per_mshr = 12


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
sys.membus = SystemXBar()
# Define Memory Hierarchy
l1d, l1i, l2 = L1Cache("64kB"), L1Cache("16kB"), L2Cache()
l1i.cpu_side = sys.cpu.icache_port
l1d.cpu_side = sys.cpu.dcache_port

sys.l2bus = L2XBar()
for cc in [l1i, l1d]:
    cc.mem_side = sys.l2bus.cpu_side_ports
l2.cpu_side = sys.l2bus.mem_side_ports
l2.mem_side = sys.membus.cpu_side_ports

sys.cpu.icache = l1i
sys.cpu.dcache = l1d
sys.cpu.l2cache = l2

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
