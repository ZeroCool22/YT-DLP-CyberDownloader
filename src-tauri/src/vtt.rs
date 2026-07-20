use regex::Regex;

#[derive(Debug)]
struct Cue {
    start: String,
    end: String,
    text: String,
}

fn token_key(token: &str) -> String {
    token
        .to_lowercase()
        .chars()
        .filter(|character| character.is_alphanumeric() || *character == '_')
        .collect()
}

fn contains_sequence(haystack: &[String], needle: &[String]) -> bool {
    !needle.is_empty()
        && needle.len() <= haystack.len()
        && haystack
            .windows(needle.len())
            .any(|window| window == needle)
}

fn wrap_caption(tokens: &[String], width: usize) -> String {
    let mut lines = Vec::new();
    let mut line = String::new();
    for token in tokens {
        let projected =
            line.chars().count() + usize::from(!line.is_empty()) + token.chars().count();
        if !line.is_empty() && projected > width {
            lines.push(std::mem::take(&mut line));
        }
        if !line.is_empty() {
            line.push(' ');
        }
        line.push_str(token);
    }
    if !line.is_empty() {
        lines.push(line);
    }
    lines.join("\n")
}

/// Converts YouTube rolling captions to ordinary VTT cues. Manual/non-YouTube
/// VTT files are returned byte-for-byte unchanged.
pub fn clean_youtube_vtt(content: &str) -> (String, usize) {
    let inline_time = Regex::new(r"<(?:\d{2}:)?\d{2}:\d{2}\.\d{3}>").expect("valid regex");
    let karaoke = Regex::new(r"(?i)</?c(?:\.[^>]*)?>").expect("valid regex");
    if content.is_empty() || (!inline_time.is_match(content) && !karaoke.is_match(content)) {
        return (content.to_owned(), 0);
    }

    let normalized = content.replace("\r\n", "\n").replace('\r', "\n");
    let normalized = normalized.trim_start_matches('\u{feff}');
    let blocks: Vec<&str> = Regex::new(r"\n{2,}")
        .unwrap()
        .split(normalized)
        .filter(|block| !block.trim().is_empty())
        .collect();
    if blocks
        .first()
        .is_none_or(|block| !block.trim_start().starts_with("WEBVTT"))
    {
        return (content.to_owned(), 0);
    }

    let timing = Regex::new(r"^(?P<start>(?:\d{2}:)?\d{2}:\d{2}\.\d{3})\s*-->\s*(?P<end>(?:\d{2}:)?\d{2}:\d{2}\.\d{3})(?:\s+.*)?$").unwrap();
    let whitespace = Regex::new(r"\s+").unwrap();
    let mut headers = Vec::new();
    let mut cues = Vec::new();
    let mut header_finished = false;
    let mut pending: Option<(String, String)> = None;

    let append = |start: String, end: String, raw: &str, cues: &mut Vec<Cue>| {
        let without_time = inline_time.replace_all(raw, "");
        let without_tags = karaoke.replace_all(&without_time, "");
        let decoded = html_escape::decode_html_entities(&without_tags);
        let text = whitespace
            .replace_all(decoded.trim(), " ")
            .trim()
            .to_owned();
        if !text.is_empty() {
            cues.push(Cue { start, end, text });
        }
    };

    for block in blocks {
        let lines: Vec<&str> = block.lines().collect();
        let timing_index = lines.iter().position(|line| line.contains("-->"));
        let Some(index) = timing_index else {
            if let Some((start, end)) = pending.take() {
                append(start, end, block, &mut cues);
            } else if !header_finished {
                headers.push(block.to_owned());
            }
            continue;
        };
        let Some(captures) = timing.captures(lines[index].trim()) else {
            continue;
        };
        header_finished = true;
        let start = captures["start"].to_owned();
        let end = captures["end"].to_owned();
        let raw = lines[index + 1..].join("\n");
        if raw.trim().is_empty() {
            pending = Some((start, end));
        } else {
            append(start, end, &raw, &mut cues);
        }
    }
    if cues.is_empty() {
        return (content.to_owned(), 0);
    }

    let original_count = cues.len();
    let mut history = Vec::<String>::new();
    let mut cleaned = Vec::<Cue>::new();
    for cue in cues {
        let pairs: Vec<(String, String)> = cue
            .text
            .split_whitespace()
            .filter_map(|token| {
                let key = token_key(token);
                (!key.is_empty()).then(|| (token.to_owned(), key))
            })
            .collect();
        let keys: Vec<String> = pairs.iter().map(|(_, key)| key.clone()).collect();
        if keys.is_empty() {
            continue;
        }
        let overlap = (1..=history.len().min(keys.len()))
            .rev()
            .find(|size| history[history.len() - size..] == keys[..*size])
            .unwrap_or(0);
        let history_tail = &history[history.len().saturating_sub(100)..];
        if overlap == 0 && contains_sequence(history_tail, &keys) {
            continue;
        }
        let new_tokens: Vec<String> = pairs[overlap..]
            .iter()
            .map(|(token, _)| token.clone())
            .collect();
        let new_keys: Vec<String> = pairs[overlap..]
            .iter()
            .map(|(_, key)| key.clone())
            .collect();
        if new_tokens.is_empty() {
            continue;
        }
        history.extend(new_keys);
        cleaned.push(Cue {
            start: cue.start,
            end: cue.end,
            text: wrap_caption(&new_tokens, 44),
        });
    }
    if cleaned.is_empty() {
        return (content.to_owned(), 0);
    }
    let header = if headers.is_empty() {
        "WEBVTT".to_owned()
    } else {
        headers.join("\n\n")
    };
    let mut output = vec![header];
    output.extend(
        cleaned
            .iter()
            .map(|cue| format!("{} --> {}\n{}", cue.start, cue.end, cue.text)),
    );
    (
        format!("{}\n", output.join("\n\n")),
        original_count.saturating_sub(cleaned.len()),
    )
}

#[cfg(test)]
mod tests {
    use super::clean_youtube_vtt;

    #[test]
    fn leaves_manual_vtt_unchanged() {
        let input = "WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nHola mundo\n";
        assert_eq!(clean_youtube_vtt(input), (input.to_owned(), 0));
    }

    #[test]
    fn removes_rolling_overlap_and_html() {
        let input = "WEBVTT\nKind: captions\n\n00:00:00.000 --> 00:00:02.000\n<c>Hola <00:00:01.000>mundo</c>\n\n00:00:02.000 --> 00:00:04.000\n<c>Hola mundo &amp; chau</c>\n";
        let (cleaned, removed) = clean_youtube_vtt(input);
        assert!(cleaned.contains("Hola mundo"));
        // A punctuation-only token is discarded exactly like the Python source.
        assert!(cleaned.contains("chau"));
        assert!(!cleaned.contains("<c>"));
        assert_eq!(removed, 0);
    }

    #[test]
    fn drops_fully_repeated_cue() {
        let input = "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\n<c>uno dos</c>\n\n00:00:01.000 --> 00:00:02.000\n<c>uno dos</c>\n";
        let (cleaned, removed) = clean_youtube_vtt(input);
        assert_eq!(cleaned.matches("uno dos").count(), 1);
        assert_eq!(removed, 1);
    }
}
