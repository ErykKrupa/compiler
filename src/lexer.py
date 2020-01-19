from sly import Lexer


class CompilerLexer(Lexer):
    tokens = {"DECLARE", "BEGIN", "END",
              "IDENTIFIER", "NUMBER",
              "ASSIGN", "READ", "WRITE",
              "PLUS", "MINUS", "TIMES", "DIV", "MOD",
              "EQ", "NEQ", "LE", "GE", "LEQ", "GEQ",
              "IF", "THEN", "ELSE", "ENDIF",
              "FOR", "FROM", "TO", "DOWNTO", "ENDFOR",
              "WHILE", "DO", "ENDWHILE", "ENDDO"
              }
    literals = {"(", ")", ",", ":", ";"}
    ignore = " \t"
    ignore_comment = r"\[[^\]]*\]"
    IDENTIFIER = r"[_a-z]+"
    PLUS = r"PLUS"
    MINUS = r"MINUS"
    TIMES = r"TIMES"
    DIV = r"DIV"
    MOD = r"MOD"
    NEQ = r"NEQ"
    EQ = r"EQ"
    LEQ = r"LEQ"
    LE = r"LE"
    GEQ = r"GEQ"
    GE = r"GE"
    ASSIGN = r"ASSIGN"
    ENDWHILE = r"ENDWHILE"
    ENDFOR = r"ENDFOR"
    FOR = r"FOR"
    FROM = r"FROM"
    DOWNTO = r"DOWNTO"
    TO = r"TO"
    WHILE = r"WHILE"
    ENDDO = r"ENDDO"
    DO = r"DO"
    READ = r"READ"
    WRITE = r"WRITE"
    ENDIF = r"ENDIF"
    IF = r"IF"
    THEN = r"THEN"
    ELSE = r"ELSE"
    DECLARE = r"DECLARE"
    BEGIN = r"BEGIN"
    END = r"END"

    @_(r"-?\d+")
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    @_(r"\n+")
    def new_line(self, t):
        self.lineno += t.value.count("\n")

    def error(self, t):
        print(f"Illegal character '{t.value[0]}'")
        self.index += 1
