import re
import sys

def is_integer(s):
    return re.match(r'^[+-]?\d+$', s) is not None

def is_decimal(s):
    regex = r'^[+-]?\d+\.\d+$'
    return re.match(regex, s) is not None

def is_valid_string(s):
    regex = r'^\"[^\"\s]*\"$'
    return re.match(regex, s) is not None

def is_keyword(s):
    keywords = {'WRITE', '.', '[', ']', '(', ')', ';'}
    return s.upper() in keywords

def is_operator(s):
    operators = {':=', '~', '<', '>', '=', '#', '+', '-', '&', 'OR', '*', '/', 'AND'}
    return s.upper() in operators

def is_identifier(s):
    # Regular expression to match valid identifiers
    regex = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
    
    # Check if the string is a keyword
    keywords = {'WRITE', '.', '[', ']', '(', ')', ';', ':=', '~', '<', '>', '=', '#', '+', '-', '&', 'OR', '*', '/', 'AND',"ELSIF", "WHILE", "IF", "END", "END.", "FUNCTION", ",", "MOD", "DIV"}
    if s in keywords:
        return False
    
    # Check if the string matches the identifier pattern
    return re.match(regex, s) is not None


def is_relation(s):
    return s in {"<", ">", "=", "#"}

def is_AddOperator(s):
    return s in {"+", "-", "OR", "&"}
    
def is_MulOperator(s):
    return s in {"*", "/", "AND", "MOD", "DIV"}

def is_member_access(s):
    return s == "."

def is_assignment(s):
    return s == ":="

def error(message, token):
    raise ParserError(f'ERROR: "{message}" expected. got "{token}"')


def identifier_isnot_function(ident):
    raise ParserError(f"Variable '{ident}' used as function.")

def identifier_isnot_variable(ident):
    raise ParserError(f"Function '{ident}' used as variable.")

def identifier_isnot_defined(ident):
    raise ParserError(f"Undefined function {ident}")


class ParserError(Exception): pass


def main():
    _tokens = sys.stdin.read().split()
    symbols = {}
        
    def error2(expected):
        raise ParserError(f"ERROR2: Expected {expected} expected. got '{_tokens[0]}'")

    def getToken():
        nonlocal _tokens
        _tokens = _tokens[1:]
    
    def token():
        return _tokens[0]

    def parse_SimpleExpression():
        parse_Term()
        while _tokens and is_AddOperator(token()):
            getToken()
            parse_Term()
        
    def parse_Term():
        parse_Factor()
        while _tokens and is_MulOperator(token()):
            getToken()
            parse_Factor()
    
    def parse_Expression():
        parse_SimpleExpression()
        if _tokens and is_relation(token()):
            getToken()
            parse_SimpleExpression()
        
    
    def parse_Selector():
        if is_member_access(token()):
            getToken()

            if is_identifier(token()):
                assert token() not in symbols
                symbols[token()] = "variable"

                getToken()
            else:
                error("Expected Identifier", token())
            return True
        elif token() == "[":
            getToken()
            parse_Expression()
            if token() == "]":
                getToken()
                return True
            else:
                error("Expected ]", token())
        else:
            return False
            
    
    def parse_Assignment():
        
        if is_identifier(token()):
            if token() not in symbols:
                symbols[token()] = "variable"
            elif symbols[token()] == "function":
                identifier_isnot_variable(token())
            

        if not parse_Designator():
            return False
        if is_assignment(token()):
            getToken()
            parse_Expression()
            return True
        else:
            return False
    
    def parse_WriteStatement():
        if token() == "WRITE":
            getToken()
            if token() == "(":
                getToken()
                parse_Expression()
                if token() == ")":
                    getToken()
                else:
                    error("Expected )", token())
            else:
                error("Expected (", token())
            return True
        else:
            return False


    def parse_Designator():
        if is_identifier(token()):
            getToken()


            while parse_Selector():
                pass
            return True
        else:
            return False

    def parse_Factor():
        if (is_integer(token())
            or is_decimal(token())
            or is_valid_string(token())
            or is_identifier(token())
        ):
            if not is_identifier(token()):
                getToken()
            else:

                if token() in symbols and symbols[token()] == "function":
                    identifier_isnot_variable(token())
                
                
                if _tokens[1] == "." or _tokens[1] == "[":
                    parse_Designator()
                elif _tokens[1] == "(":
                    parse_FunctionCall()
                else:
                    getToken()
                    #error("Expected '.', '[', or '('", _tokens[1])

        elif token() == "(":
            getToken()
            parse_Expression()
            if token() == ")":
                getToken()
            else:
                error(")", token())
        elif token() == "~":
            getToken()
            parse_Factor()    
          
        else:

            error("Factor", token())
    
    def parse_Statement():

        if token() == "IF":
            parse_IfStatement()
            return True
        elif token() == "WHILE":
            parse_WhileStatement()
            return True
        
        if len(_tokens) > 1 and _tokens[1] == "(" and token() != "WRITE":
            parse_FunctionCall()
            return True
        elif parse_Assignment():
            return True
        elif parse_WriteStatement():
            return True
        

    
        return False

    def parse_StatementSequence():
        if parse_Statement():
            while _tokens and token() == ";":               
                getToken()
                parse_Statement()
        else:
            error("Expected Statement", token())
    
    
    def parse_IfStatement():
        if token() == "IF":
            getToken()
            parse_Expression()
            if token() == "THEN":
                getToken()
                parse_StatementSequence()
                
                if token() == "ELSE":
                    getToken()
                    parse_StatementSequence()
                    if token() == "END":
                        getToken()
                        return True
                    else:
                        error("Expected 'END'", token())
                elif token() == "ELSIF":
                    
                    while token() == "ELSIF":
                        getToken()
                        parse_Expression()
                        if token() == "THEN":
                            getToken()
                            parse_StatementSequence()
                            

                    if token() == "END":
                        getToken()
                        return
                    elif token() == "ELSE":
                        getToken()
                        parse_StatementSequence()
                        if token() == "END":
                            getToken()
                            return True
                        else:
                            error("Expected 'END'", token())
                if token() == "END":
                    getToken()
                    return
                else:
                    error2("END")
                    

                
            else:
                error("Expected 'THEN'", token()) 
        else:
            error("Expected IF", token())
    
    def parse_FunctionBody():
        if token() == ";":
            getToken()
            return
        
        parse_StatementSequence()
        if token() == "RETURN":
            getToken()
            if token() == "(":
                getToken()
                if is_identifier(token()):
                    getToken()
                    if token() == ")":
                        getToken()
                    else:
                        error("Expected )", token())
                else:
                    error("Expected identifier", token())
            else:
                error("EXPECTED (", token())
        

        if token() == "END.":
            getToken()
            return
        else:
            error("Expected 'END.'", token())

    
    def parse_FunctionDeclaration():
        if token() == "FUNCTION":
            getToken()
            if is_identifier(token()):
                symbols[token()] = "function"
                getToken()
                if token() == "(":
                    getToken()
                    parse_ParamSequence()
                    if token() == ")":
                        getToken()
                    else:
                        error("Expected )", token())
                else:
                    error("Expected (", token())

                parse_FunctionBody()
            else:
                error("Expected Identifier", token())
        else:
            error("Expected 'FUNCTION'", token())

        
    def parse_DeclarationSequence():
        while _tokens and token() == "FUNCTION":
            parse_FunctionDeclaration()
        

    def parse_ParamSequence():
        if is_identifier(token()):
            if token() in symbols and symbols[token()] != "variable":
                identifier_isnot_variable(token())
            else:
                symbols[token()] = "variable"


            getToken()
            while token() == ",":
                getToken()
                if is_identifier(token()):
                    if token() in symbols and symbols[token()] != "variable":
                        identifier_isnot_variable(token())
                    else:
                        symbols[token()] = "variable"
                    getToken()
                else:
                    error("Expected identifier", token())
        



    def parse_FunctionCall():
        if is_identifier(token()):
            if token() not in symbols:
                identifier_isnot_defined(token())
            elif symbols[token()] == "variable":
                identifier_isnot_function(token())

            assert symbols[token()] == "function"

            getToken()
            if token() == "(":
                getToken()
                parse_ParamSequence()
                if token() == ")":
                    getToken()
                else:
                    error("Expected ')'", token())           
            else:
                error("Expected '('", token())
        else:
            error("Expected FunctionCall", token())

    def parse_WhileStatement():

        if token() == "WHILE":
            getToken()
            parse_Expression()
            if token() == "DO":
                getToken()
                parse_StatementSequence()
                if token() == "ELSIF":
                    getToken()
                    parse_Expression()
                    if token() == "DO":
                        getToken()
                        parse_StatementSequence()
                        if token() == "END":
                            getToken()
                        else:
                            error2("END")
                    else:
                        error2("DO")
                elif token() == "END":
                    getToken()
                else:
                    error2("ELSIF or END")
            else:
                error2("DO")
        else:
            error2("WHILE") 

    # parse_Assignment()
    try:
        parse_DeclarationSequence()
        if len(_tokens):
            error("Expected EOF", token())
            return
    except ParserError as e:
        print("INVALID!")
        print(e)
    except IndexError:
        raise EOFError("Unexpected EOF")
    else:
        print("CORRECT")
        print(f"Symbol Table : size {len(symbols)}")
        for s in symbols:
            print(f"{s:<11} {symbols[s]}")
    

if __name__ == "__main__":
    main()

   