# SHBAGT-data (Static JSON)

Dataset ready for GitHub Pages hosting and mobile clients.

## Layout
- `data/chapters.json`:
  - Top-level `{ meta, chapters: [...] }`
  - Each chapter includes: `id`, `chapter_number`, `slug`, `titles {hi,en}`, `summary {en,hi}`, `transliteration`, `name_meaning {en,hi}`, `verses_count`, `path` (folder: `data/verses/chapter_<n>/`).
- `data/verses/chapter_<n>/verse_<m>.json`: per-verse objects with `text`, `transliteration`, `translations` (english/hindi), `commentaries` (english/hindi).

## Validation
Run locally:
```bash
python3 scripts/validate.py
```
Expect: `Validation passed: chapters and verses are well-formed.`

## GitHub Pages
Enable Pages (branch: main, folder: root). Base URL:
- `https://<user>.github.io/<repo>/`

### Fetching (iOS Swift)
```swift
struct Chapter: Decodable {
    let id: Int
    let chapter_number: Int
    let slug: String
    let titles: Titles
    let summary: Summary
    let transliteration: String
    let name_meaning: Meaning
    let verses_count: Int
    let path: String // e.g., "data/verses/chapter_1/"
}
struct Titles: Decodable { let hi: String; let en: String }
struct Summary: Decodable { let en: String; let hi: String }
struct Meaning: Decodable { let en: String; let hi: String }

struct Verse: Decodable {
    let id: Int
    let verse_number: Int
    let chapter_number: Int
    let slug: String
    let text: String
    let transliteration: String
    let translations: [Entry]?
    let commentaries: [Entry]?
}
struct Entry: Decodable { let description: String; let author_name: String; let language: String }

final class API {
    let base = URL(string: "https://<user>.github.io/<repo>/")!

    func fetchChapters() async throws -> [Chapter] {
        let url = base.appendingPathComponent("data/chapters.json")
        let (data, _) = try await URLSession.shared.data(from: url)
        struct Root: Decodable { let chapters: [Chapter] }
        return try JSONDecoder().decode(Root.self, from: data).chapters
    }

    func fetchVerse(chapter: Chapter, verseNumber: Int) async throws -> Verse {
        let folder = chapter.path.hasSuffix("/") ? chapter.path : chapter.path + "/"
        let url = base.appendingPathComponent(folder + "verse_\(verseNumber).json")
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(Verse.self, from: data)
    }
}
```

### Fetching (curl)
```bash
curl -s https://<user>.github.io/<repo>/data/chapters.json | jq '.chapters[0]'
# Fetch verse 1 of chapter 1
curl -s https://<user>.github.io/<repo>/data/verses/chapter_1/verse_1.json | jq
```

## Notes
- Directory listings are disabled on Pages; rely on `data/chapters.json` + `verses_count`.
- For cache busting on client updates, append a query string (e.g., `?v=2025-09-15`).
