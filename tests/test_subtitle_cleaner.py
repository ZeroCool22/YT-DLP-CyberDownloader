import os
import tempfile
import unittest

from yt_dlp import YoutubeDL
from yt_dlp.postprocessor import FFmpegSubtitlesConvertorPP

from subtitle_cleaner import YoutubeSubtitleCleanerPP, clean_youtube_vtt


ROLLING_VTT = """WEBVTT
Kind: captions
Language: es

00:00:00.880 --> 00:00:02.149 align:start position:0%

Bueno<00:00:01.120><c> gente,</c><00:00:01.319><c> esto</c><00:00:01.480><c> es</c><00:00:01.640><c> a</c><00:00:01.760><c> pedido</c><00:00:02.000><c> de</c>

00:00:02.149 --> 00:00:02.159 align:start position:0%
Bueno gente, esto es a pedido de

00:00:02.159 --> 00:00:05.510 align:start position:0%
Bueno gente, esto es a pedido de
ustedes.<00:00:03.520><c> Este</c><00:00:03.639><c> es</c><00:00:03.760><c> un</c><00:00:03.919><c> video</c><00:00:04.520><c> sin</c><00:00:04.759><c> edición,</c>

00:00:05.510 --> 00:00:05.520 align:start position:0%
ustedes. Este es un video sin edición,

00:00:05.520 --> 00:00:08.030 align:start position:0%
ustedes. Este es un video sin edición,
sin<00:00:05.759><c> cortar,</c><00:00:07.000><c> así</c><00:00:07.240><c> que</c><00:00:07.399><c> que</c><00:00:07.560><c> salga</c><00:00:07.799><c> lo</c><00:00:07.919><c> que</c>
"""


class SubtitleCleanerTests(unittest.TestCase):
    def test_cleans_youtube_rolling_captions(self):
        cleaned, removed = clean_youtube_vtt(ROLLING_VTT)

        self.assertEqual(removed, 2)
        self.assertNotIn('<c>', cleaned)
        self.assertNotRegex(cleaned, r'<\d{2}:\d{2}:\d{2}\.\d{3}>')
        self.assertNotIn('align:start', cleaned)
        self.assertEqual(cleaned.count('Bueno gente, esto es a pedido de'), 1)
        self.assertEqual(cleaned.count('ustedes.'), 1)
        self.assertEqual(cleaned.count('sin cortar,'), 1)

    def test_leaves_regular_vtt_untouched(self):
        regular = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nTexto normal.\n"
        cleaned, removed = clean_youtube_vtt(regular)

        self.assertEqual(cleaned, regular)
        self.assertEqual(removed, 0)

    def test_clean_vtt_then_convert_to_srt(self):
        tools_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools')
        with tempfile.TemporaryDirectory() as temp_dir:
            vtt_path = os.path.join(temp_dir, 'sample.es.vtt')
            srt_path = os.path.join(temp_dir, 'sample.es.srt')
            with open(vtt_path, 'w', encoding='utf-8') as subtitle_file:
                subtitle_file.write(ROLLING_VTT)

            info = {
                'requested_subtitles': {
                    'es': {'ext': 'vtt', 'filepath': vtt_path, 'data': ROLLING_VTT},
                },
                '__files_to_move': {vtt_path: vtt_path},
            }
            with YoutubeDL({'quiet': True, 'ffmpeg_location': tools_dir}) as ydl:
                _, info = YoutubeSubtitleCleanerPP(ydl).run(info)
                FFmpegSubtitlesConvertorPP(ydl, format='srt').run(info)

            self.assertTrue(os.path.exists(srt_path))
            with open(srt_path, encoding='utf-8-sig') as subtitle_file:
                srt = subtitle_file.read()
            self.assertEqual(srt.count('Bueno gente, esto es a pedido de'), 1)
            self.assertEqual(srt.count('ustedes.'), 1)
            self.assertNotIn('<c>', srt)


if __name__ == '__main__':
    unittest.main()
