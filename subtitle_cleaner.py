import html
import re
import textwrap

from yt_dlp.postprocessor.common import PostProcessor


_TIME_LINE_RE = re.compile(
    r'^(?P<start>(?:\d{2}:)?\d{2}:\d{2}\.\d{3})\s*-->\s*'
    r'(?P<end>(?:\d{2}:)?\d{2}:\d{2}\.\d{3})(?:\s+.*)?$'
)
_INLINE_TIME_RE = re.compile(r'<(?:\d{2}:)?\d{2}:\d{2}\.\d{3}>')
_KARAOKE_TAG_RE = re.compile(r'</?c(?:\.[^>]*)?>', re.IGNORECASE)


def _token_key(token):
    """Normaliza un token sólo para compararlo, conservando el original al escribir."""
    return re.sub(r'[^\wáéíóúüñ]+', '', token.casefold(), flags=re.UNICODE)


def _contains_sequence(haystack, needle):
    if not needle or len(needle) > len(haystack):
        return False
    limit = len(haystack) - len(needle) + 1
    return any(haystack[index:index + len(needle)] == needle for index in range(limit))


def _wrap_caption(tokens, width=44):
    return '\n'.join(textwrap.wrap(
        ' '.join(tokens),
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    ))


def clean_youtube_vtt(content):
    """
    Convierte captions rodantes de YouTube en cues convencionales.

    Devuelve ``(contenido, cues_eliminados)``. Si el VTT no contiene marcas
    de karaoke de YouTube, se devuelve intacto para no alterar subtítulos
    manuales ni archivos de otros sitios.
    """
    if not content or not (
            _INLINE_TIME_RE.search(content) or _KARAOKE_TAG_RE.search(content)):
        return content, 0

    normalized = content.replace('\r\n', '\n').replace('\r', '\n').lstrip('\ufeff')
    blocks = [block.strip('\n') for block in re.split(r'\n{2,}', normalized) if block.strip()]
    if not blocks or not blocks[0].lstrip().startswith('WEBVTT'):
        return content, 0

    header_blocks = []
    cues = []
    pending_timing = None
    header_finished = False

    def append_cue(start, end, raw_text):
        text = _INLINE_TIME_RE.sub('', raw_text)
        text = _KARAOKE_TAG_RE.sub('', text)
        text = html.unescape(re.sub(r'\s+', ' ', text)).strip()
        if text:
            cues.append((start, end, text))

    for block in blocks:
        lines = block.splitlines()
        timing_index = next((i for i, line in enumerate(lines) if '-->' in line), None)
        if timing_index is None:
            if pending_timing:
                append_cue(*pending_timing, block)
                pending_timing = None
            elif not header_finished:
                header_blocks.append(block)
            continue

        match = _TIME_LINE_RE.match(lines[timing_index].strip())
        if not match:
            continue
        header_finished = True
        raw_text = '\n'.join(lines[timing_index + 1:])
        if raw_text.strip():
            append_cue(match.group('start'), match.group('end'), raw_text)
        else:
            pending_timing = (match.group('start'), match.group('end'))

    if not cues:
        return content, 0

    history_tokens = []
    history_keys = []
    cleaned_cues = []

    for start, end, text in cues:
        token_pairs = [
            (token, key) for token in text.split()
            if (key := _token_key(token))
        ]
        current_tokens = [token for token, _ in token_pairs]
        current_keys = [key for _, key in token_pairs]
        if not current_keys:
            continue

        max_overlap = min(len(history_keys), len(current_keys))
        overlap = 0
        for size in range(max_overlap, 0, -1):
            if history_keys[-size:] == current_keys[:size]:
                overlap = size
                break

        if overlap == 0 and _contains_sequence(history_keys[-100:], current_keys):
            continue

        new_tokens = current_tokens[overlap:]
        new_keys = current_keys[overlap:]
        if not new_tokens:
            continue

        cleaned_cues.append((start, end, _wrap_caption(new_tokens)))
        history_tokens.extend(new_tokens)
        history_keys.extend(new_keys)

    if not cleaned_cues:
        return content, 0

    header = '\n\n'.join(header_blocks) if header_blocks else 'WEBVTT'
    output_blocks = [header]
    output_blocks.extend(
        f'{start} --> {end}\n{text}' for start, end, text in cleaned_cues
    )
    cleaned = '\n\n'.join(output_blocks).rstrip() + '\n'
    return cleaned, max(0, len(cues) - len(cleaned_cues))


class YoutubeSubtitleCleanerPP(PostProcessor):
    """Limpia VTT automáticos antes de cualquier conversión de subtítulos."""

    def run(self, info):
        total_removed = 0
        cleaned_files = 0

        for subtitle in (info.get('requested_subtitles') or {}).values():
            filepath = subtitle.get('filepath')
            if subtitle.get('ext') != 'vtt' or not filepath:
                continue
            try:
                with open(filepath, encoding='utf-8-sig') as source:
                    original = source.read()
                cleaned, removed = clean_youtube_vtt(original)
                if cleaned == original:
                    continue
                with open(filepath, 'w', encoding='utf-8', newline='\n') as destination:
                    destination.write(cleaned)
                subtitle['data'] = cleaned
                cleaned_files += 1
                total_removed += removed
            except OSError as error:
                self.report_warning(f'No se pudo limpiar {filepath}: {error}')

        if cleaned_files:
            self.to_screen(
                f'Subtítulos limpiados: {cleaned_files} archivo(s), '
                f'{total_removed} bloque(s) repetido(s) eliminado(s)')
        return [], info
