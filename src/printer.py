class Printer:

    print_code = None
    iterator = 0
    buffer_store = []

    @staticmethod
    def init(output_file):
        def write_to_file(instruction):
            output_file.write(f"{instruction} \n")
            return
        Printer.print_code = write_to_file

    @staticmethod
    def buffer(instruction):
        Printer.buffer_store.append(instruction)
        Printer.iterator += 1

    @staticmethod
    def print_buffer_store():
        for instruction in Printer.buffer_store:
            Printer.print_code(instruction)
        Printer.buffer_store = []

    @staticmethod
    def get():
        Printer.buffer(f"GET")

    @staticmethod
    def put():
        Printer.buffer(f"PUT")

    @staticmethod
    def load(i):
        Printer.buffer(f"LOAD {i}")

    @staticmethod
    def store(i):
        Printer.buffer(f"STORE {i}")

    @staticmethod
    def loadI(i):
        Printer.buffer(f"LOADI {i}")

    @staticmethod
    def storeI(i):
        Printer.buffer(f"STOREI {i}")

    @staticmethod
    def add(i):
        Printer.buffer(f"ADD {i}")

    @staticmethod
    def sub(i):
        Printer.buffer(f"SUB {i}")

    @staticmethod
    def shift(i):
        Printer.buffer(f"SHIFT {i}")

    @staticmethod
    def inc():
        Printer.buffer(f"INC")

    @staticmethod
    def dec():
        Printer.buffer(f"DEC")

    @staticmethod
    def jump(j):
        Printer.buffer(f"JUMP {Printer.iterator + j}")

    @staticmethod
    def jump_abs(j):
        Printer.buffer(f"JUMP {j}")

    @staticmethod
    def jpos(j):
        Printer.buffer(f"JPOS {Printer.iterator + j}")

    @staticmethod
    def jzero(j):
        Printer.buffer(f"JZERO {Printer.iterator + j}")

    @staticmethod
    def jzero_abs(j):
        Printer.buffer(f"JZERO {j}")

    @staticmethod
    def jneg(j):
        Printer.buffer(f"JNEG {Printer.iterator + j}")

    @staticmethod
    def halt():
        Printer.buffer(f"HALT")

    @staticmethod
    def template():
        Printer.buffer(f"TEMPLATE")
        return Printer.iterator - 1

    @staticmethod
    def replace(position, instruction):
        Printer.buffer_store[position] = f"{instruction} {Printer.iterator}"

    @staticmethod
    def get_iterator():
        return Printer.iterator
