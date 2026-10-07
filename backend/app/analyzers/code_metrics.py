import io
import tokenize


def line_metrics(code: str) -> tuple[int, int, int, int]:
    lines = code.splitlines()
    total = len(lines)
    blank = sum(not line.strip() for line in lines)
    comment_rows: set[int] = set()
    code_rows: set[int] = set()
    try:
        for token in tokenize.generate_tokens(io.StringIO(code).readline):
            if token.type == tokenize.COMMENT:
                comment_rows.add(token.start[0])
            elif token.type not in {
                tokenize.ENCODING, tokenize.NL, tokenize.NEWLINE,
                tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER,
            }:
                code_rows.update(range(token.start[0], token.end[0] + 1))
    except tokenize.TokenError:
        pass
    comments = len(comment_rows - code_rows)
    return total, total - blank - comments, blank, comments
