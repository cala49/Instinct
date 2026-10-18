class InstinctError(Exception):
    """Errores Basicos de Instic"""

    def __init__(self, message:str, line:int |None = None):
        self.message = message
        self.line = line

        if line is not None:
            super().__init__(f"Error en la línea {line}: {message}")
        else:
            super().__init__(message)

class LexerError(InstinctError):
    pass

class ParserError(InstinctError):
    pass

class SemanticError(InstinctError):
    pass

class InstinctRuntimeError(InstinctError):
    pass