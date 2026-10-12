//
//  SectorExtractor.swift
//  CityBeautifulBuzz
//
//  Extracts Chandigarh sector numbers and iconic landmark tags
//  from news titles and summaries for the architectural card badges.
//

import Foundation

public struct SectorExtractor {
    public static func extract(from title: String, summary: String) -> String {
        let combined = "\(title) \(summary)"

        // 1. Regex check for Sector numbers (English & Hindi)
        // Matches: "Sector 17", "Sec 22", "Sector-35", "Sec. 43", "सेक्टर 17"
        let sectorPatterns = [
            #"(?i)\b(?:Sector|Sec\.?)[-\s]*([0-9]{1,2}[A-Za-z]?)\b"#,
            #"(?i)सेक्टर[-\s]*([0-9]{1,2}[A-Za-z]?)"#
        ]

        for pattern in sectorPatterns {
            if let regex = try? NSRegularExpression(pattern: pattern, options: []) {
                let range = NSRange(combined.startIndex..<combined.endIndex, in: combined)
                if let match = regex.firstMatch(in: combined, options: [], range: range),
                   match.numberOfRanges > 1,
                   let sectorRange = Range(match.range(at: 1), in: combined) {
                    let secNumber = String(combined[sectorRange]).uppercased()
                    return "SEC \(secNumber)"
                }
            }
        }

        // 2. Check for iconic Chandigarh landmarks & hubs
        let landmarkMap: [(keywords: [String], tag: String)] = [
            (["sukhna", "सुखना"], "SUKHNA"),
            (["panjab university", "pu ", "पीयू"], "PU CAMPUS"),
            (["pgi", "pgimer", "पीजीआई"], "PGIMER"),
            (["rock garden", "रॉक गार्डन"], "ROCK GARDEN"),
            (["rose garden", "रोज गार्डन"], "ROSE GARDEN"),
            (["leisure valley", "लेज़र वैली"], "LEISURE VALLEY"),
            (["elante", "एलांते"], "ELANTE"),
            (["madhya marg", "मध्य मार्ग"], "MADHYA MARG"),
            (["dakshin marg", "दक्षिण मार्ग"], "DAKSHIN MARG"),
            (["it park", "आईटी पार्क"], "IT PARK"),
            (["mohali", "मोहाली"], "MOHALI"),
            (["panchkula", "पंचकूला"], "PANCHKULA"),
            (["high court", "हाई कोर्ट"], "HIGH COURT"),
            (["secretariat", "सचिवालय"], "CAPITOL"),
            (["gmc", "gmch", "जीएमसीएच"], "GMCH-32"),
            (["railway", "station", "स्टेशन"], "CHD JUNCTION")
        ]

        let lower = combined.lowercased()
        for item in landmarkMap {
            for kw in item.keywords {
                if lower.contains(kw) {
                    return item.tag
                }
            }
        }

        // 3. Fallback to Tri-City identifier
        return "TRI-CITY"
    }
}
