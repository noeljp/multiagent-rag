import re
from langchain.text_splitter import RecursiveCharacterTextSplitter

class SmartTextSplitter:
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.fallback_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def split_text(self, text: str):
        blocks = self._split_by_block_type(text)
        smart_chunks = []

        for block_type, block in blocks:
            if block_type in ["json", "code"]:
                # Si bloc raisonnablement court, ne pas le couper
                if len(block) <= self.chunk_size:
                    smart_chunks.append(block)
                else:
                    smart_chunks += self.fallback_splitter.split_text(block)
            else:
                smart_chunks += self.fallback_splitter.split_text(block)

        return smart_chunks

    def _split_by_block_type(self, text: str):
        """
        Identifie les blocs : JSON, code, ou texte libre.
        Retourne une liste de tuples (type, contenu).
        """
        pattern = re.compile(r"(```.*?```)|({.*?})", re.DOTALL)
        matches = list(pattern.finditer(text))

        result = []
        last_index = 0

        for match in matches:
            start, end = match.span()
            before = text[last_index:start]
            if before.strip():
                result.append(("text", before.strip()))

            content = match.group()
            if content.startswith("```"):
                result.append(("code", content.strip("`").strip()))
            elif content.startswith("{"):
                result.append(("json", content.strip()))
            last_index = end

        remaining = text[last_index:]
        if remaining.strip():
            result.append(("text", remaining.strip()))

        return result
