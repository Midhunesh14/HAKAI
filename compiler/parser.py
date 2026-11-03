"""Recursive-descent Parser for HAKAI."""

from __future__ import annotations

from typing import List, Optional, Tuple
from compiler.tokens import Token, TokenType
from compiler.ast_nodes import (
    Program,
    Stmt,
    Expr,
    VarDecl,
    Parameter,
    FunctionDecl,
    ClassDecl,
    IfStmt,
    WhileStmt,
    RepeatStmt,
    ReturnStmt,
    BreakStmt,
    ContinueStmt,
    ImportStmt,
    ExpressionStmt,
    Block,
    Literal,
    Identifier,
    Binary,
    Unary,
    Assign,
    Call,
    Get,
    Set,
    Index,
    IndexSet,
    ArrayLiteral,
    MapLiteral,
    TupleLiteral,
    SelfNode,
    SuperNode,
)
from compiler.errors import HakaiSyntaxError


class Parser:
    """Parses a sequence of HAKAI tokens into an Abstract Syntax Tree."""

    def __init__(self, tokens: List[Token], source_code: Optional[str] = None) -> None:
        self.tokens = tokens
        self.source_code = source_code or ""
        self.current = 0

    def parse(self) -> Program:
        statements: List[Stmt] = []
        has_boundaries = False

        if self._match(TokenType.HAKAI_START):
            has_boundaries = True
            while not self._check(TokenType.HAKAI_END) and not self._is_at_end():
                stmt = self._declaration()
                if stmt is not None:
                    statements.append(stmt)
            self._consume(
                TokenType.HAKAI_END,
                "Expected 'HAKAI END' to close program boundary.",
            )
        else:
            while not self._is_at_end():
                stmt = self._declaration()
                if stmt is not None:
                    statements.append(stmt)

        return Program(
            statements=statements,
            has_boundaries=has_boundaries,
            line=1,
            column=1,
            filename=self._current_token().source,
        )

    # -------------------------------------------------------------------------
    # Helper navigation
    # -------------------------------------------------------------------------

    def _is_at_end(self) -> bool:
        return self._peek().kind == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _current_token(self) -> Token:
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return self.tokens[-1]

    def _check(self, kind: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().kind == kind

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _match(self, *kinds: TokenType) -> bool:
        for kind in kinds:
            if self._check(kind):
                self._advance()
                return True
        return False

    def _consume(self, kind: TokenType, message: str) -> Token:
        if self._check(kind):
            return self._advance()
        token = self._peek()
        raise HakaiSyntaxError(
            message=f"{message} Found: {token.lexeme or token.kind.name!r}",
            filename=token.source,
            line=token.line,
            column=token.column,
            source_code=self.source_code,
        )

    # -------------------------------------------------------------------------
    # Declarations and Statements
    # -------------------------------------------------------------------------

    def _declaration(self) -> Stmt:
        if self._match(TokenType.LET):
            return self._var_declaration(is_const=False)
        if self._match(TokenType.CONST):
            return self._var_declaration(is_const=True)
        if self._match(TokenType.FUNCTION):
            return self._function_declaration()
        if self._match(TokenType.CLASS):
            return self._class_declaration()
        if self._match(TokenType.IMPORT):
            return self._import_declaration()
        if self._match(TokenType.FROM):
            return self._from_import_declaration()
        return self._statement()

    def _var_declaration(self, is_const: bool) -> Stmt:
        keyword_tok = self._previous()
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected variable name after declaration keyword.")
        initializer: Optional[Expr] = None

        if self._match(TokenType.EQUAL):
            initializer = self._expression()
        elif is_const:
            raise HakaiSyntaxError(
                message=f"Constant '{name_tok.lexeme}' must be initialized with a value.",
                filename=name_tok.source,
                line=name_tok.line,
                column=name_tok.column,
                source_code=self.source_code,
            )

        self._match(TokenType.SEMICOLON)  # Optional semicolon
        return VarDecl(
            name=name_tok.lexeme,
            initializer=initializer,
            is_const=is_const,
            line=keyword_tok.line,
            column=keyword_tok.column,
            filename=keyword_tok.source,
        )

    def _function_declaration(self, is_static: bool = False) -> FunctionDecl:
        fn_tok = self._previous()
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected function name.")

        self._consume(TokenType.LEFT_PAREN, "Expected '(' after function name.")
        parameters: List[Parameter] = []

        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                param_tok = self._consume(TokenType.IDENTIFIER, "Expected parameter name.")
                default_val: Optional[Expr] = None
                if self._match(TokenType.EQUAL):
                    default_val = self._expression()
                parameters.append(Parameter(name=param_tok.lexeme, default_value=default_val))
                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RIGHT_PAREN, "Expected ')' after parameter list.")
        self._consume(TokenType.LEFT_BRACE, "Expected '{' before function body.")
        body = self._block()

        return FunctionDecl(
            name=name_tok.lexeme,
            params=parameters,
            body=body,
            is_static=is_static,
            line=fn_tok.line,
            column=fn_tok.column,
            filename=fn_tok.source,
        )

    def _class_declaration(self) -> ClassDecl:
        class_tok = self._previous()
        name_tok = self._consume(TokenType.IDENTIFIER, "Expected class name.")

        superclass: Optional[str] = None
        if self._match(TokenType.EXTENDS):
            super_tok = self._consume(TokenType.IDENTIFIER, "Expected superclass name after 'extends'.")
            superclass = super_tok.lexeme

        self._consume(TokenType.LEFT_BRACE, "Expected '{' before class body.")

        methods: List[FunctionDecl] = []
        static_methods: List[FunctionDecl] = []

        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            is_static = False
            if self._match(TokenType.STATIC):
                is_static = True
            self._consume(TokenType.FUNCTION, "Expected 'function' inside class body.")
            method = self._function_declaration(is_static=is_static)
            if is_static:
                static_methods.append(method)
            else:
                methods.append(method)

        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after class body.")

        return ClassDecl(
            name=name_tok.lexeme,
            superclass=superclass,
            methods=methods,
            static_methods=static_methods,
            line=class_tok.line,
            column=class_tok.column,
            filename=class_tok.source,
        )

    def _import_declaration(self) -> ImportStmt:
        import_tok = self._previous()
        mod_tok = self._consume(TokenType.IDENTIFIER, "Expected module name to import.")
        alias: Optional[str] = None
        if self._match(TokenType.AS):
            alias_tok = self._consume(TokenType.IDENTIFIER, "Expected alias after 'as'.")
            alias = alias_tok.lexeme

        self._match(TokenType.SEMICOLON)
        return ImportStmt(
            module_name=mod_tok.lexeme,
            alias=alias,
            symbols=None,
            line=import_tok.line,
            column=import_tok.column,
            filename=import_tok.source,
        )

    def _from_import_declaration(self) -> ImportStmt:
        from_tok = self._previous()
        mod_tok = self._consume(TokenType.IDENTIFIER, "Expected module name after 'from'.")
        self._consume(TokenType.IMPORT, "Expected 'import' after module name.")

        symbols: List[str] = []
        while True:
            sym_tok = self._consume(TokenType.IDENTIFIER, "Expected symbol name to import.")
            symbols.append(sym_tok.lexeme)
            if not self._match(TokenType.COMMA):
                break

        self._match(TokenType.SEMICOLON)
        return ImportStmt(
            module_name=mod_tok.lexeme,
            alias=None,
            symbols=symbols,
            line=from_tok.line,
            column=from_tok.column,
            filename=from_tok.source,
        )

    def _statement(self) -> Stmt:
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.REPEAT):
            return self._repeat_statement()
        if self._match(TokenType.RETURN):
            return self._return_statement()
        if self._match(TokenType.BREAK):
            tok = self._previous()
            self._match(TokenType.SEMICOLON)
            return BreakStmt(line=tok.line, column=tok.column, filename=tok.source)
        if self._match(TokenType.CONTINUE):
            tok = self._previous()
            self._match(TokenType.SEMICOLON)
            return ContinueStmt(line=tok.line, column=tok.column, filename=tok.source)
        if self._match(TokenType.LEFT_BRACE):
            return self._block()
        return self._expression_statement()

    def _block(self) -> Block:
        brace_tok = self._previous()
        statements: List[Stmt] = []
        while not self._check(TokenType.RIGHT_BRACE) and not self._is_at_end():
            stmt = self._declaration()
            if stmt is not None:
                statements.append(stmt)
        self._consume(TokenType.RIGHT_BRACE, "Expected '}' after block.")
        return Block(
            statements=statements,
            line=brace_tok.line,
            column=brace_tok.column,
            filename=brace_tok.source,
        )

    def _if_statement(self) -> Stmt:
        if_tok = self._previous()
        condition = self._expression()
        self._consume(TokenType.LEFT_BRACE, "Expected '{' after if condition.")
        then_branch = self._block()

        else_branch: Optional[Stmt] = None
        if self._match(TokenType.ELSEIF):
            # Recurse as another if statement
            else_branch = self._if_statement()
        elif self._match(TokenType.ELSE):
            if self._match(TokenType.IF):
                # 'else if'
                else_branch = self._if_statement()
            else:
                self._consume(TokenType.LEFT_BRACE, "Expected '{' after 'else'.")
                else_branch = self._block()

        return IfStmt(
            condition=condition,
            then_branch=then_branch,
            else_branch=else_branch,
            line=if_tok.line,
            column=if_tok.column,
            filename=if_tok.source,
        )

    def _while_statement(self) -> Stmt:
        tok = self._previous()
        condition = self._expression()
        self._consume(TokenType.LEFT_BRACE, "Expected '{' after while condition.")
        body = self._block()
        return WhileStmt(
            condition=condition,
            body=body,
            line=tok.line,
            column=tok.column,
            filename=tok.source,
        )

    def _repeat_statement(self) -> Stmt:
        tok = self._previous()
        count = self._expression()
        self._consume(TokenType.LEFT_BRACE, "Expected '{' after repeat count.")
        body = self._block()
        return RepeatStmt(
            count=count,
            body=body,
            line=tok.line,
            column=tok.column,
            filename=tok.source,
        )

    def _return_statement(self) -> Stmt:
        tok = self._previous()
        value: Optional[Expr] = None
        if not self._check(TokenType.SEMICOLON) and not self._check(TokenType.RIGHT_BRACE):
            value = self._expression()
        self._match(TokenType.SEMICOLON)
        return ReturnStmt(
            value=value,
            line=tok.line,
            column=tok.column,
            filename=tok.source,
        )

    def _expression_statement(self) -> Stmt:
        expr = self._expression()
        self._match(TokenType.SEMICOLON)
        return ExpressionStmt(
            expression=expr,
            line=expr.line,
            column=expr.column,
            filename=expr.filename,
        )

    # -------------------------------------------------------------------------
    # Expressions
    # -------------------------------------------------------------------------

    def _expression(self) -> Expr:
        return self._assignment()

    def _assignment(self) -> Expr:
        expr = self._logic_or()

        if self._match(TokenType.EQUAL):
            equals = self._previous()
            value = self._assignment()

            if isinstance(expr, Identifier):
                return Assign(
                    name=expr.name,
                    value=value,
                    line=equals.line,
                    column=equals.column,
                    filename=equals.source,
                )
            elif isinstance(expr, Get):
                return Set(
                    obj=expr.obj,
                    name=expr.name,
                    value=value,
                    line=equals.line,
                    column=equals.column,
                    filename=equals.source,
                )
            elif isinstance(expr, Index):
                return IndexSet(
                    target=expr.target,
                    index=expr.index,
                    value=value,
                    line=equals.line,
                    column=equals.column,
                    filename=equals.source,
                )

            raise HakaiSyntaxError(
                message="Invalid assignment target.",
                filename=equals.source,
                line=equals.line,
                column=equals.column,
                source_code=self.source_code,
            )

        return expr

    def _logic_or(self) -> Expr:
        expr = self._logic_and()
        while self._match(TokenType.OR):
            op = self._previous()
            right = self._logic_and()
            expr = Binary(
                left=expr,
                operator=op.lexeme,
                right=right,
                line=op.line,
                column=op.column,
                filename=op.source,
            )
        return expr

    def _logic_and(self) -> Expr:
        expr = self._equality()
        while self._match(TokenType.AND):
            op = self._previous()
            right = self._equality()
            expr = Binary(
                left=expr,
                operator=op.lexeme,
                right=right,
                line=op.line,
                column=op.column,
                filename=op.source,
            )
        return expr

    def _equality(self) -> Expr:
        expr = self._comparison()
        while self._match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            op = self._previous()
            right = self._comparison()
            expr = Binary(
                left=expr,
                operator=op.lexeme,
                right=right,
                line=op.line,
                column=op.column,
                filename=op.source,
            )
        return expr

    def _comparison(self) -> Expr:
        expr = self._term()
        while self._match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            op = self._previous()
            right = self._term()
            expr = Binary(
                left=expr,
                operator=op.lexeme,
                right=right,
                line=op.line,
                column=op.column,
                filename=op.source,
            )
        return expr

    def _term(self) -> Expr:
        expr = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self._previous()
            right = self._factor()
            expr = Binary(
                left=expr,
                operator=op.lexeme,
                right=right,
                line=op.line,
                column=op.column,
                filename=op.source,
            )
        return expr

    def _factor(self) -> Expr:
        expr = self._power()
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self._previous()
            right = self._power()
            expr = Binary(
                left=expr,
                operator=op.lexeme,
                right=right,
                line=op.line,
                column=op.column,
                filename=op.source,
            )
        return expr

    def _power(self) -> Expr:
        expr = self._unary()
        if self._match(TokenType.STAR_STAR):
            op = self._previous()
            right = self._power()  # Right associative
            expr = Binary(
                left=expr,
                operator=op.lexeme,
                right=right,
                line=op.line,
                column=op.column,
                filename=op.source,
            )
        return expr

    def _unary(self) -> Expr:
        if self._match(TokenType.NOT, TokenType.BANG, TokenType.MINUS, TokenType.PLUS):
            op = self._previous()
            operand = self._unary()
            return Unary(
                operator=op.lexeme,
                operand=operand,
                line=op.line,
                column=op.column,
                filename=op.source,
            )
        return self._call()

    def _call(self) -> Expr:
        expr = self._primary()

        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            elif self._match(TokenType.DOT):
                name_tok = self._consume(TokenType.IDENTIFIER, "Expected property name after '.'.")
                expr = Get(
                    obj=expr,
                    name=name_tok.lexeme,
                    line=name_tok.line,
                    column=name_tok.column,
                    filename=name_tok.source,
                )
            elif self._match(TokenType.LEFT_BRACKET):
                index_expr = self._expression()
                bracket_tok = self._consume(TokenType.RIGHT_BRACKET, "Expected ']' after index.")
                expr = Index(
                    target=expr,
                    index=index_expr,
                    line=bracket_tok.line,
                    column=bracket_tok.column,
                    filename=bracket_tok.source,
                )
            else:
                break

        return expr

    def _finish_call(self, callee: Expr) -> Call:
        arguments: List[Expr] = []
        paren_tok = self._previous()

        if not self._check(TokenType.RIGHT_PAREN):
            while True:
                arguments.append(self._expression())
                if not self._match(TokenType.COMMA):
                    break

        close_paren = self._consume(TokenType.RIGHT_PAREN, "Expected ')' after argument list.")
        return Call(
            callee=callee,
            arguments=arguments,
            line=paren_tok.line,
            column=paren_tok.column,
            filename=close_paren.source,
        )

    def _primary(self) -> Expr:
        tok = self._peek()

        if self._match(TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING, TokenType.BOOLEAN, TokenType.NULL):
            prev = self._previous()
            return Literal(
                value=prev.literal,
                line=prev.line,
                column=prev.column,
                filename=prev.source,
            )

        if self._match(TokenType.SELF):
            prev = self._previous()
            return SelfNode(line=prev.line, column=prev.column, filename=prev.source)

        if self._match(TokenType.SUPER):
            prev = self._previous()
            self._consume(TokenType.DOT, "Expected '.' after 'super'.")
            method_tok = self._consume(TokenType.IDENTIFIER, "Expected superclass method name.")
            return SuperNode(
                method=method_tok.lexeme,
                line=prev.line,
                column=prev.column,
                filename=prev.source,
            )

        if self._match(TokenType.IDENTIFIER):
            prev = self._previous()
            return Identifier(
                name=prev.lexeme,
                line=prev.line,
                column=prev.column,
                filename=prev.source,
            )

        # Parenthesized expression or Tuple
        if self._match(TokenType.LEFT_PAREN):
            start_tok = self._previous()
            if self._match(TokenType.RIGHT_PAREN):
                # Empty tuple ()
                return TupleLiteral(elements=[], line=start_tok.line, column=start_tok.column, filename=start_tok.source)
            expr = self._expression()
            if self._match(TokenType.COMMA):
                # Tuple literal: (expr, ...)
                elements = [expr]
                if not self._check(TokenType.RIGHT_PAREN):
                    while True:
                        elements.append(self._expression())
                        if not self._match(TokenType.COMMA):
                            break
                self._consume(TokenType.RIGHT_PAREN, "Expected ')' after tuple elements.")
                return TupleLiteral(elements=elements, line=start_tok.line, column=start_tok.column, filename=start_tok.source)

            self._consume(TokenType.RIGHT_PAREN, "Expected ')' after expression.")
            return expr

        # Array literal: [ ... ]
        if self._match(TokenType.LEFT_BRACKET):
            start_tok = self._previous()
            elements: List[Expr] = []
            if not self._check(TokenType.RIGHT_BRACKET):
                while True:
                    elements.append(self._expression())
                    if not self._match(TokenType.COMMA):
                        break
            self._consume(TokenType.RIGHT_BRACKET, "Expected ']' after array elements.")
            return ArrayLiteral(elements=elements, line=start_tok.line, column=start_tok.column, filename=start_tok.source)

        # Map literal: { key: value, ... }
        if self._match(TokenType.LEFT_BRACE):
            start_tok = self._previous()
            pairs: List[Tuple[Expr, Expr]] = []
            if not self._check(TokenType.RIGHT_BRACE):
                while True:
                    key_expr = self._expression()
                    self._consume(TokenType.COLON, "Expected ':' after map key.")
                    val_expr = self._expression()
                    pairs.append((key_expr, val_expr))
                    if not self._match(TokenType.COMMA):
                        break
            self._consume(TokenType.RIGHT_BRACE, "Expected '}' after map pairs.")
            return MapLiteral(pairs=pairs, line=start_tok.line, column=start_tok.column, filename=start_tok.source)

        raise HakaiSyntaxError(
            message=f"Unexpected token: {tok.lexeme or tok.kind.name!r}. Expected an expression.",
            filename=tok.source,
            line=tok.line,
            column=tok.column,
            source_code=self.source_code,
        )
