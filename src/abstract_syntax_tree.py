from printer import Printer
from error_printer import ErrorPrinter

variables = {}
arrays = {}
uninitialized_variables = set()
memory_counter = 17
memory_pivot = 0

GENERATED_VALUE = 1
NUMBER_POSITION = 2
NUMBER_VALUE = 3
ASSIGN_VALUE = 4
MATH_POSITION = 5
MATH_VALUE = 6
MATH_FIRST_VALUE = 7
MATH_SECOND_VALUE = 8
MATH_THIRD_VALUE = 9
MATH_FOURTH_VALUE = 10
MATH_FIFTH_VALUE = 11
MATH_RESULT_VALUE = 12
CONDITION = 13
MINUS_ONE_CONSTANT = 14
ZERO_CONSTANT = 15
ONE_CONSTANT = 16


def generate_constant(value):
    Printer.sub(0)
    if value >= 0:
        for bit in f"{value:b}":
            Printer.shift(ONE_CONSTANT)
            if bit == "1":
                Printer.inc()
    else:
        value = -(value + 1)
        Printer.dec()
        for bit in f"{value:b}":
            Printer.shift(ONE_CONSTANT)
            if bit == "0":
                Printer.inc()
    Printer.store(GENERATED_VALUE)


class Program:
    declarations = None
    commands = None

    def __init__(self, declarations, commands):
        self.declarations = declarations
        self.commands = commands
        self.generate()

    def generate(self):
        global memory_pivot
        self.generate_allocate_constants()
        self.declarations.generate()
        memory_pivot = memory_counter
        self.commands.generate()
        self.generate_stop_program()

    @staticmethod
    def generate_allocate_constants():
        Printer.sub(0)
        Printer.dec()
        Printer.store(MINUS_ONE_CONSTANT)
        Printer.inc()
        Printer.store(ZERO_CONSTANT)
        Printer.inc()
        Printer.store(ONE_CONSTANT)

    @staticmethod
    def generate_stop_program():
        Printer.halt()
        Printer.print_buffer_store()


class Declarations:
    declarations = None

    def __init__(self, declarations):
        self.declarations = declarations

    def add(self, declaration):
        self.declarations.append(declaration)

    def generate(self):
        for declaration in self.declarations:
            declaration.generate()


class DeclareVariable:
    identifier = None

    def __init__(self, identifier):
        self.identifier = identifier

    def generate(self):
        if self.identifier in variables:
            ErrorPrinter.raise_error(f"redeclaration of variable {self.identifier}")
        self.generate_variable()

    def generate_variable(self):
        global memory_counter
        variables[self.identifier] = memory_counter
        uninitialized_variables.add(self.identifier)
        memory_counter += 1


class DeclareArray:
    identifier = None
    begin = None
    end = None

    def __init__(self, identifier, begin, end):
        self.identifier = identifier
        self.begin = begin
        self.end = end

    def generate(self):
        if self.identifier in arrays:
            ErrorPrinter.raise_error(f"redeclaration of array {self.identifier}")
        if self.begin.number > self.end.number:
            ErrorPrinter.raise_error(f"array {self.identifier} cannot be declared,"
                                     f" wrong range ({self.begin.number}:{self.end.number})")
        self.generate_array()

    def generate_array(self):
        global memory_counter
        arrays[self.identifier] = (memory_counter - self.begin.number, self.begin.number, self.end.number)
        memory_counter += self.end.number - self.begin.number + 1


class Commands:
    commands = None

    def __init__(self, command):
        self.commands = command

    def add(self, command):
        self.commands.append(command)

    def generate(self):
        for command in self.commands:
            command.generate()


class Assign:
    identifier = None
    expression = None

    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression

    def generate(self):
        self.expression.generate()
        self.generate_rewrite()
        self.identifier.generate()
        if isinstance(self.identifier, Variable) and variables[self.identifier.variable] >= memory_pivot:
            ErrorPrinter.raise_error(f"cannot assign to iterator {self.identifier.variable}")
        self.generate_assign()

    @staticmethod
    def generate_rewrite():
        Printer.load(NUMBER_VALUE)
        Printer.store(ASSIGN_VALUE)

    @staticmethod
    def generate_assign():
        Printer.load(ASSIGN_VALUE)
        Printer.storeI(NUMBER_POSITION)


class If:
    condition = None
    commands = None

    def __init__(self, condition, commands):
        self.condition = condition
        self.commands = commands

    def generate(self):
        self.condition.generate()
        Printer.load(CONDITION)
        Printer.jzero(2)
        position = Printer.template()
        self.commands.generate()
        Printer.replace(position, "JUMP")


class IfElse:
    condition = None
    true_commands = None
    false_commands = None

    def __init__(self, condition, true_commands, false_commands):
        self.condition = condition
        self.true_commands = true_commands
        self.false_commands = false_commands

    def generate(self):
        self.condition.generate()
        Printer.load(CONDITION)
        Printer.jzero(2)
        position1 = Printer.template()
        self.true_commands.generate()
        position2 = Printer.template()
        Printer.replace(position1, "JUMP")
        self.false_commands.generate()
        Printer.replace(position2, "JUMP")


class WhileDo:
    condition = None
    commands = None

    def __init__(self, condition, commands):
        self.condition = condition
        self.commands = commands

    def generate(self):
        position1 = Printer.get_iterator()
        self.condition.generate()
        Printer.load(CONDITION)
        Printer.jzero(2)
        position2 = Printer.template()
        self.commands.generate()
        Printer.jump_abs(position1)
        Printer.replace(position2, "JUMP")


class DoWhile:
    commands = None
    condition = None

    def __init__(self, commands, condition):
        self.commands = commands
        self.condition = condition

    def generate(self):
        position = Printer.get_iterator()
        self.commands.generate()
        self.condition.generate()
        Printer.load(CONDITION)
        Printer.jzero_abs(position)


class For:
    iterator = None
    start = None
    end = None
    ascending = None
    commands = None

    def __init__(self, iterator, start,
                 end, ascending, commands):
        self.iterator = iterator
        self.start = start
        self.end = end
        self.ascending = ascending
        self.commands = commands

    def generate(self):
        global memory_counter
        iterator = memory_counter
        if self.iterator.variable in variables:
            ErrorPrinter.raise_error(f"cannot declare iterator {self.iterator.variable}, "
                                     f"already declared as variable")
        variables[self.iterator.variable] = memory_counter
        memory_counter += 1
        end = memory_counter
        memory_counter += 1
        self.start.generate()
        Printer.load(NUMBER_VALUE)
        Printer.store(iterator)
        self.end.generate()
        Printer.load(NUMBER_VALUE)
        Printer.store(end)
        position1 = Printer.get_iterator()
        Printer.load(end)
        Printer.sub(iterator)
        position2 = Printer.template()
        self.commands.generate()
        Printer.load(iterator)
        Printer.inc() if self.ascending else Printer.dec()
        Printer.store(iterator)
        Printer.jump_abs(position1)
        Printer.replace(position2, "JNEG" if self.ascending else "JPOS")
        del variables[self.iterator.variable]


class Read:
    identifier = None

    def __init__(self, identifier):
        self.identifier = identifier

    def generate(self):
        self.identifier.generate()
        if isinstance(self.identifier, Variable) and variables[self.identifier.variable] >= memory_pivot:
            ErrorPrinter.raise_error(f"cannot assign to iterator {self.identifier.variable}")
        self.generate_read()

    @staticmethod
    def generate_read():
        Printer.get()
        Printer.storeI(NUMBER_POSITION)


class Write:
    value = None

    def __init__(self, value):
        self.value = value

    def generate(self):
        self.value.generate()
        self.generate_write()

    @staticmethod
    def generate_write():
        Printer.load(NUMBER_VALUE)
        Printer.put()


class Operation:
    value1 = None
    operator = None
    value2 = None

    def __init__(self, value1, operator, value2):
        self.value1 = value1
        self.operator = operator
        self.value2 = value2

    def generate(self):
        self.value1.generate()
        self.generate_rewrite()
        self.value2.generate()
        self.generate_operation()

    @staticmethod
    def generate_rewrite():
        Printer.load(NUMBER_POSITION)
        Printer.store(MATH_POSITION)
        Printer.load(NUMBER_VALUE)
        Printer.store(MATH_VALUE)

    @staticmethod
    def generate_add():
        Printer.load(MATH_VALUE)
        Printer.add(NUMBER_VALUE)
        Printer.store(NUMBER_VALUE)

    @staticmethod
    def generate_subtract():
        Printer.load(MATH_VALUE)
        Printer.sub(NUMBER_VALUE)
        Printer.store(NUMBER_VALUE)

    @staticmethod
    def generate_multiply():
        Printer.load(ZERO_CONSTANT)
        Printer.store(MATH_RESULT_VALUE)
        Printer.load(NUMBER_VALUE)
        Printer.jzero(23)
        Printer.store(MATH_SECOND_VALUE)
        Printer.load(MATH_VALUE)
        Printer.jneg(2)
        Printer.jump(3)
        Printer.sub(0)
        Printer.sub(MATH_VALUE)
        Printer.store(MATH_FIRST_VALUE)
        Printer.jzero(15)
        Printer.shift(MINUS_ONE_CONSTANT)
        Printer.shift(ONE_CONSTANT)
        Printer.sub(MATH_FIRST_VALUE)
        Printer.jzero(4)
        Printer.load(MATH_RESULT_VALUE)
        Printer.add(MATH_SECOND_VALUE)
        Printer.store(MATH_RESULT_VALUE)
        Printer.load(MATH_SECOND_VALUE)
        Printer.shift(ONE_CONSTANT)
        Printer.store(MATH_SECOND_VALUE)
        Printer.load(MATH_FIRST_VALUE)
        Printer.shift(MINUS_ONE_CONSTANT)
        Printer.store(MATH_FIRST_VALUE)
        Printer.jump(-14)
        Printer.load(MATH_VALUE)
        Printer.jpos(4)
        Printer.sub(0)
        Printer.sub(MATH_RESULT_VALUE)
        Printer.jump(2)
        Printer.load(MATH_RESULT_VALUE)
        Printer.store(NUMBER_VALUE)

    @staticmethod
    def generate_divide_modulo():
        Printer.sub(0)
        Printer.store(MATH_RESULT_VALUE)
        Printer.store(MATH_THIRD_VALUE)
        Printer.load(NUMBER_VALUE)
        Printer.jzero(75)
        Printer.jpos(3)
        Printer.sub(0)
        Printer.sub(NUMBER_VALUE)
        Printer.store(MATH_SECOND_VALUE)
        Printer.store(MATH_FIFTH_VALUE)
        Printer.load(MATH_VALUE)
        Printer.jzero(68)
        Printer.jpos(3)
        Printer.sub(0)
        Printer.sub(MATH_VALUE)
        Printer.store(MATH_FIRST_VALUE)
        Printer.jzero(8)
        Printer.shift(MINUS_ONE_CONSTANT)
        Printer.store(MATH_FOURTH_VALUE)
        Printer.load(MATH_THIRD_VALUE)
        Printer.inc()
        Printer.store(MATH_THIRD_VALUE)
        Printer.load(MATH_FOURTH_VALUE)
        Printer.jump(-7)
        Printer.load(MATH_SECOND_VALUE)
        Printer.shift(MATH_THIRD_VALUE)
        Printer.store(MATH_SECOND_VALUE)
        Printer.load(MATH_FIRST_VALUE)
        Printer.sub(MATH_SECOND_VALUE)
        Printer.jneg(6)
        Printer.store(MATH_FIRST_VALUE)
        Printer.load(ONE_CONSTANT)
        Printer.shift(MATH_THIRD_VALUE)
        Printer.add(MATH_RESULT_VALUE)
        Printer.store(MATH_RESULT_VALUE)
        Printer.load(MATH_SECOND_VALUE)
        Printer.shift(MINUS_ONE_CONSTANT)
        Printer.store(MATH_SECOND_VALUE)
        Printer.load(MATH_THIRD_VALUE)
        Printer.dec()
        Printer.store(MATH_THIRD_VALUE)
        Printer.jneg(5)
        Printer.load(MATH_FIRST_VALUE)
        Printer.jneg(3)
        Printer.jzero(2)
        Printer.jump(-18)
        Printer.load(MINUS_ONE_CONSTANT)
        Printer.store(MATH_FOURTH_VALUE)
        Printer.load(MATH_VALUE)
        Printer.jpos(4)
        Printer.load(MATH_FOURTH_VALUE)
        Printer.inc()
        Printer.store(MATH_FOURTH_VALUE)
        Printer.load(NUMBER_VALUE)
        Printer.jpos(5)
        Printer.load(MATH_FOURTH_VALUE)
        Printer.inc()
        Printer.store(MATH_FOURTH_VALUE)
        Printer.jump(3)
        Printer.load(MATH_VALUE)
        Printer.jneg(3)
        Printer.jzero(2)
        Printer.jump(12)
        Printer.sub(0)
        Printer.sub(MATH_RESULT_VALUE)
        Printer.store(MATH_RESULT_VALUE)
        Printer.load(MATH_FIRST_VALUE)
        Printer.jzero(7)
        Printer.load(MATH_RESULT_VALUE)
        Printer.dec()
        Printer.store(MATH_RESULT_VALUE)
        Printer.load(MATH_FIFTH_VALUE)
        Printer.sub(MATH_FIRST_VALUE)
        Printer.store(MATH_FIRST_VALUE)
        Printer.load(NUMBER_VALUE)
        Printer.jpos(4)
        Printer.sub(0)
        Printer.sub(MATH_FIRST_VALUE)
        Printer.store(MATH_FIRST_VALUE)

    @staticmethod
    def generate_divide():
        Operation.generate_divide_modulo()
        Printer.load(MATH_RESULT_VALUE)
        Printer.store(NUMBER_VALUE)

    @staticmethod
    def generate_modulo():
        Operation.generate_divide_modulo()
        Printer.load(MATH_FIRST_VALUE)
        Printer.store(NUMBER_VALUE)

    def generate_operation(self):
        {
            "PLUS": self.generate_add,
            "MINUS": self.generate_subtract,
            "TIMES": self.generate_multiply,
            "DIV": self.generate_divide,
            "MOD": self.generate_modulo,
        }.get(self.operator)()


class Condition:
    value1 = None
    operator = None
    value2 = None

    def __init__(self, value1, operator, value2):
        self.value1 = value1
        self.operator = operator
        self.value2 = value2

    def generate(self):
        self.value1.generate()
        self.generate_rewrite()
        self.value2.generate()
        self.generate_operation()

    @staticmethod
    def generate_rewrite():
        Printer.load(NUMBER_VALUE)
        Printer.store(MATH_VALUE)

    @staticmethod
    def generate_equal():
        Printer.load(MATH_VALUE)
        Printer.sub(NUMBER_VALUE)
        Printer.jzero(2)
        Printer.load(ONE_CONSTANT)
        Printer.store(CONDITION)

    @staticmethod
    def generate_not_equal():
        Printer.load(MATH_VALUE)
        Printer.sub(NUMBER_VALUE)
        Printer.jzero(3)
        Printer.load(ZERO_CONSTANT)
        Printer.jump(2)
        Printer.load(ONE_CONSTANT)
        Printer.store(CONDITION)

    @staticmethod
    def generate_less():
        Printer.load(NUMBER_VALUE)
        Printer.sub(MATH_VALUE)
        Printer.jpos(3)
        Printer.load(ONE_CONSTANT)
        Printer.jump(2)
        Printer.load(ZERO_CONSTANT)
        Printer.store(CONDITION)

    @staticmethod
    def generate_greater():
        Printer.load(MATH_VALUE)
        Printer.sub(NUMBER_VALUE)
        Printer.jpos(3)
        Printer.load(ONE_CONSTANT)
        Printer.jump(2)
        Printer.load(ZERO_CONSTANT)
        Printer.store(CONDITION)

    @staticmethod
    def generate_less_equal():
        Printer.load(MATH_VALUE)
        Printer.sub(NUMBER_VALUE)
        Printer.jpos(3)
        Printer.load(ZERO_CONSTANT)
        Printer.jump(2)
        Printer.load(ONE_CONSTANT)
        Printer.store(CONDITION)

    @staticmethod
    def generate_greater_equal():
        Printer.load(NUMBER_VALUE)
        Printer.sub(MATH_VALUE)
        Printer.jpos(3)
        Printer.load(ZERO_CONSTANT)
        Printer.jump(2)
        Printer.load(ONE_CONSTANT)
        Printer.store(CONDITION)

    def generate_operation(self):
        {
            "EQ": self.generate_equal,
            "NEQ": self.generate_not_equal,
            "LE": self.generate_less,
            "GE": self.generate_greater,
            "LEQ": self.generate_less_equal,
            "GEQ": self.generate_greater_equal,
        }.get(self.operator)()


class Value:
    value = None

    def __init__(self, value):
        self.value = value

    def generate(self):
        self.value.generate()


class Number:
    number = None

    def __init__(self, value):
        self.number = value

    def generate(self):
        self.generate_number()

    def generate_number(self):
        generate_constant(self.number)
        Printer.load(GENERATED_VALUE)
        Printer.store(NUMBER_VALUE)


class Identifier:
    identifier = None

    def __init__(self, identifier):
        self.identifier = identifier

    def generate(self):
        self.identifier.generate()
        self.generate_identifier()

    @staticmethod
    def generate_identifier():
        Printer.loadI(NUMBER_POSITION)
        Printer.store(NUMBER_VALUE)


class Variable:
    variable = None

    def __init__(self, variable):
        self.variable = variable

    def generate(self):
        if self.variable not in variables:
            ErrorPrinter.raise_error(f"variable {self.variable} is not declared")
        self.generate_variable()

    def generate_variable(self):
        generate_constant(variables[self.variable])
        Printer.load(GENERATED_VALUE)
        Printer.store(NUMBER_POSITION)


class ArrayVariable:
    array = None
    variable = None

    def __init__(self, array, variable):
        self.array = array
        self.variable = variable

    def generate(self):
        if self.array not in arrays:
            ErrorPrinter.raise_error(f"array {self.array} is not declared")
        self.variable.generate()
        self.generate_array_variable()

    def generate_array_variable(self):
        generate_constant(arrays[self.array][0])
        Printer.loadI(NUMBER_POSITION)
        Printer.add(GENERATED_VALUE)
        Printer.store(NUMBER_POSITION)


class ArrayNumber:
    array = None
    number = None

    def __init__(self, array, number):
        self.array = array
        self.number = number

    def generate(self):
        if self.array not in arrays:
            ErrorPrinter.raise_error(f"array {self.array} is not declared")
        if arrays[self.array][1] > self.number.number or arrays[self.array][2] < self.number.number:
            ErrorPrinter.raise_error(f"{self.number.number} is not index of array {self.array},"
                                     f" correct range ({arrays[self.array][1]}:{arrays[self.array][2]})")
        self.number.generate()
        self.generate_array_number()

    def generate_array_number(self):
        generate_constant(arrays[self.array][0])
        Printer.load(GENERATED_VALUE)
        Printer.add(NUMBER_VALUE)
        Printer.store(NUMBER_POSITION)
