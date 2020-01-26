from sly import Parser
from lexer import CompilerLexer
from abstract_syntax_tree import *


class CompilerParser(Parser):
    tokens = CompilerLexer.tokens

    @_("DECLARE declarations BEGIN commands END")
    def program(self, p):
        return Program(p.declarations, p.commands)

    @_("BEGIN commands END")
    def program(self, p):
        return Program(Declarations([]), p.commands)

    @_("declarations ',' IDENTIFIER")
    def declarations(self, p):
        p.declarations.add(DeclareVariable(p.IDENTIFIER))
        return p.declarations

    @_("declarations ',' IDENTIFIER '(' NUMBER ':' NUMBER ')'")
    def declarations(self, p):
        p.declarations.add(DeclareArray(p.IDENTIFIER,
                                        Number(int(p.NUMBER0)),
                                        Number(int(p.NUMBER1))))
        return p.declarations

    @_("IDENTIFIER")
    def declarations(self, p):
        return Declarations([DeclareVariable(p.IDENTIFIER)])

    @_("IDENTIFIER '(' NUMBER ':' NUMBER ')'")
    def declarations(self, p):
        return Declarations([DeclareArray(p.IDENTIFIER, Number(int(p.NUMBER0)),
                                          Number(int(p.NUMBER1)))])

    @_("commands command")
    def commands(self, p):
        p.commands.add(p.command)
        return p.commands

    @_("command")
    def commands(self, p):
        return Commands([p.command])

    @_("identifier ASSIGN expression ';'")
    def command(self, p):
        return Assign(p.identifier, p.expression)

    @_("IF condition THEN commands ENDIF")
    def command(self, p):
        return If(p.condition, p.commands)

    @_("IF condition THEN commands ELSE commands ENDIF")
    def command(self, p):
        return IfElse(p.condition, p.commands0, p.commands1)

    @_("WHILE condition DO commands ENDWHILE")
    def command(self, p):
        return WhileDo(p.condition, p.commands)

    @_("DO commands WHILE condition ENDDO")
    def command(self, p):
        return DoWhile(p.commands, p.condition)

    @_("FOR IDENTIFIER FROM value TO value DO commands ENDFOR")
    def command(self, p):
        return For(Variable(p.IDENTIFIER), Value(p.value0), Value(p.value1), True, p.commands)

    @_("FOR IDENTIFIER FROM value DOWNTO value DO commands ENDFOR")
    def command(self, p):
        return For(Variable(p.IDENTIFIER), Value(p.value0), Value(p.value1), False, p.commands)

    @_("READ identifier ';'")
    def command(self, p):
        return Read(p.identifier)

    @_("WRITE value ';'")
    def command(self, p):
        return Write(Value(p.value))

    @_("value")
    def expression(self, p):
        return Value(p.value)

    @_("value PLUS value",
       "value MINUS value",
       "value TIMES value",
       "value DIV value",
       "value MOD value")
    def expression(self, p):
        return Operation(Value(p.value0), p[1], Value(p.value1))

    @_("value EQ value",
       "value NEQ value",
       "value LE value",
       "value GE value",
       "value LEQ value",
       "value GEQ value")
    def condition(self, p):
        return Condition(Value(p.value0), p[1], Value(p.value1))

    @_("NUMBER")
    def value(self, p):
        return Number(int(p.NUMBER))

    @_("identifier")
    def value(self, p):
        return Identifier(p.identifier)

    @_("IDENTIFIER")
    def identifier(self, p):
        return Variable(p.IDENTIFIER)

    @_("IDENTIFIER '(' IDENTIFIER ')'")
    def identifier(self, p):
        return ArrayVariable(p.IDENTIFIER0, Variable(p.IDENTIFIER1))

    @_("IDENTIFIER '(' NUMBER ')'")
    def identifier(self, p):
        return ArrayNumber(p.IDENTIFIER, Number(int(p.NUMBER)))
