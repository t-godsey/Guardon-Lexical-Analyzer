import re

# Helper Functions
def peek(chars, position):
    if position < len(chars):
        return chars[position]
    return None

def advance(chars, position):
    character = chars[position]
    return character, position + 1

def outputToken(tokenType, token, lineNumber):
    print(f"Token: {token}, Type: {tokenType}, Line: {lineNumber}")

def errorOutput(errorType, string):
    print(f"Error: Type - {errorType}, Error String - {string}, Line - {lineNumber}")

# File Input
print("Enter your file name:")
path = input()

try:
    with open(path, "r") as f:
        lines = f.readlines()
except FileNotFoundError:
    print("File not found")
    exit()

# Token Counters
lineNumber = 0
tokenCount = 0
identifierCount = 0
functionCallCount = 0
functionDeclCount = 0
keywordCount = 0
roleCount = 0
stringCount = 0
capabilityCount = 0
numberCount = 0
operatorCount = 0
symbolCount = 0
typeWrapperCount = 0
errorCount = 0

# Token Definitions
KEYWORDS = {
    "def": "KEYWORD_DEF",
    "if": "KEYWORD_IF",
    "return": "KEYWORD_RETURN",
    "requires": "KEYWORD_REQUIRES",
    "new": "KEYWORD_NEW",
    # Data type keywords
    "Int": "KEYWORD_INT",
    "Float": "KEYWORD_FLOAT",
    "String": "KEYWORD_STRING",
    "Char": "KEYWORD_CHAR",
    "Bool": "KEYWORD_BOOL",
    "Nonce": "KEYWORD_NONCE",
    "Capability": "KEYWORD_CAPABILITY",
    "Role": "KEYWORD_ROLE",
    "User": "KEYWORD_USER",
    "Void": "KEYWORD_VOID",
    "Key": "KEYWORD_KEY",
    # Cryptographic algorithms
    "AES256": "KEYWORD_CRYPTO_AES256",
    "RSA3072": "KEYWORD_CRYPTO_RSA3072",
    "HMAC_SHA256": "KEYWORD_CRYPTO_HMAC_SHA256",
}

# Capitalized type wrappers (Secret, Public, Tainted)
TYPE_WRAPPERS = {
    "Secret": "TYPE_MODIFIER_SECRET",
    "Public": "TYPE_MODIFIER_PUBLIC",
    "Tainted": "TYPE_MODIFIER_TAINTED"
}

ROLES = {
    "USER": "ROLE_USER",
    "ADMIN": "ROLE_ADMIN",
    "AUTHOR": "ROLE_AUTHOR",
    "FINANCIAL_ACCESS": "ROLE_FINANCIAL_ACCESS",
}

CAPABILITIES = {
    "CAPABILITY_SECRET_WRITE": "CAPABILITY_SECRET_WRITE",
    "CAPABILITY_KEY_USE": "CAPABILITY_KEY_USE",
    "CAPABILITY_SECRET_READ": "CAPABILITY_SECRET_READ",
    "CAPABILITY_RANDOM": "CAPABILITY_RANDOM",
    "CAPABILITY_FS_READ": "CAPABILITY_FS_READ",
    "CAPABILITY_FS_WRITE": "CAPABILITY_FS_WRITE",
    "CAPABILITY_FS_OPEN": "CAPABILITY_FS_OPEN",
    "CAPABILITY_NET_CONNECT": "CAPABILITY_NET_CONNECT",
    "CAPABILITY_AUDIT": "CAPABILITY_AUDIT",
}

SYMBOLS = {"(", ")", "{", "}", "[", "]", ",", "."}

MULTI_OPS = {"==", "!=", ">=", "<="}
SINGLE_OPS = {"+", "-", "*", "/", "=", ">", "<"}

identifierPattern = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
intPattern = re.compile(r"\d+")
floatPattern = re.compile(r"\d+\.\d+")

# Main Lexer Loop
for line in lines:
    chars = list(line)
    lineNumber += 1
    position = 0

    while peek(chars, position) is not None:
        ch = peek(chars, position)

        # Skip whitespace
        if ch.isspace():
            _, position = advance(chars, position)
            continue

        # Skip comments (#)
        if ch == "#":
            break  # ignore rest of line

        # Strings
        if ch == '"':
            string = ""
            _, position = advance(chars, position)
            while peek(chars, position) is not None and peek(chars, position) != '"':
                char, position = advance(chars, position)
                string += char
            if peek(chars, position) == '"':
                _, position = advance(chars, position)
                stringCount += 1
                tokenCount += 1
                outputToken("STRING", f'"{string}"', lineNumber)
            else:
                errorCount += 1
                errorOutput("Unterminated String", string, lineNumber)
            continue

        # Identifiers / Keywords / Type Wrappers / Roles / Capabilities / Function calls
        if ch.isalpha() or ch == "_":
            string = ""
            while peek(chars, position) is not None and (peek(chars, position).isalnum() or peek(chars, position) == "_"):
                char, position = advance(chars, position)
                string += char

            # Check for keywords first
            if string in KEYWORDS:
                keywordCount += 1
                tokenCount += 1
                outputToken(KEYWORDS[string], string, lineNumber)

            # Check for type modifiers
            elif string in TYPE_WRAPPERS:
                typeWrapperCount += 1
                tokenCount += 1
                outputToken(TYPE_WRAPPERS[string], string, lineNumber)

            # Check for roles
            elif string in ROLES:
                roleCount += 1
                tokenCount += 1
                outputToken(ROLES[string], string, lineNumber)

            # Check for capabilities
            elif string in CAPABILITIES:
                capabilityCount += 1
                tokenCount += 1
                outputToken("CAPABILITY", string, lineNumber)

            # Otherwise it's an identifier (variable name, function name, etc.)
            elif re.fullmatch(identifierPattern, string):
                # Check if next non-space char is '(' → function call
                temp_pos = position
                while temp_pos < len(chars) and chars[temp_pos].isspace():
                    temp_pos += 1
                if temp_pos < len(chars) and chars[temp_pos] == "(":
                    functionCallCount += 1
                    tokenCount += 1
                    outputToken("FUNCTION_CALL", string, lineNumber)
                else:
                    identifierCount += 1
                    tokenCount += 1
                    outputToken("IDENTIFIER", string, lineNumber)
                    last_was_def = False
            else:
                errorCount += 1
                errorOutput("Invalid Identifier", string, lineNumber)
                last_was_def = False
            continue

        # Numbers
        if ch.isdigit():
            string = ""
            while peek(chars, position) is not None and (peek(chars, position).isdigit() or peek(chars, position) == "."):
                char, position = advance(chars, position)
                string += char
            if re.fullmatch(floatPattern, string):
                numberCount += 1
                tokenCount += 1
                outputToken("NUMBER_FLOAT", string, lineNumber)
            elif re.fullmatch(intPattern, string):
                numberCount += 1
                tokenCount += 1
                outputToken("NUMBER_INT", string, lineNumber)
            else:
                errorCount += 1
                errorOutput("Invalid Number", string, lineNumber)
            continue

        # Operators
        two_char = "".join(chars[position:position+2])
        if two_char in MULTI_OPS:
            operatorCount += 1
            tokenCount += 1
            outputToken("OPERATOR", two_char, lineNumber)
            _, position = advance(chars, position)
            _, position = advance(chars, position)
            continue
        if ch in SINGLE_OPS:
            operatorCount += 1
            tokenCount += 1
            char, position = advance(chars, position)
            outputToken("OPERATOR", char, lineNumber)
            continue

        # Symbols
        if ch in SYMBOLS:
            symbolCount += 1
            tokenCount += 1
            char, position = advance(chars, position)
            outputToken("SYMBOL", char, lineNumber)
            continue

        # Invalid Character
        errorCount += 1
        char, position = advance(chars, position)
        errorOutput("Invalid Character", char, lineNumber)

# Summary
print("\n--- Lexer Summary ---")
print("Total Tokens:", tokenCount)
print("Keywords:", keywordCount)
print("Identifiers:", identifierCount)
print("Function Calls:", functionCallCount)
print("Numbers:", numberCount)
print("Strings:", stringCount)
print("Roles:", roleCount)
print("Capabilities:", capabilityCount)
print("Type Wrappers:", typeWrapperCount)
print("Operators:", operatorCount)
print("Symbols:", symbolCount)
print("Errors:", errorCount)