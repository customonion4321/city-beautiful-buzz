//
//  NewsItem.swift
//  CityBeautifulBuzzWidget
//
//  Decodes the live JSON schema served by GitHub Pages.
//

import Foundation

public struct NewsFeedResponse: Codable, Sendable {
    public let schemaVersion: String
    public let project: String
    public let city: String
    public let lastUpdated: String
    public let itemCount: Int
    public let items: [NewsItem]

    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"
        case project
        case city
        case lastUpdated = "last_updated"
        case itemCount = "item_count"
        case items
    }
}

public struct NewsSource: Codable, Hashable, Sendable {
    public let id: String
    public let name: String
    public let logoUrl: String
    public let color: String
    public let articleUrl: String
    public let language: String
    public let tier: Int

    enum CodingKeys: String, CodingKey {
        case id
        case name
        case logoUrl = "logo_url"
        case color
        case articleUrl = "article_url"
        case language
        case tier
    }

    public init(id: String, name: String, logoUrl: String, color: String, articleUrl: String, language: String, tier: Int) {
        self.id = id
        self.name = name
        self.logoUrl = logoUrl
        self.color = color
        self.articleUrl = articleUrl
        self.language = language
        self.tier = tier
    }
}

public struct NewsItem: Identifiable, Codable, Hashable, Sendable {
    public let id: String
    public let title: String
    public let summary: String
    public let categoryId: String
    public let categoryLabelEn: String
    public let categoryLabelHi: String
    public let source: NewsSource
    public let publishedAt: String
    public let importance: String
    public let serverSectorTag: String?

    enum CodingKeys: String, CodingKey {
        case id
        case title
        case summary
        case categoryId = "category_id"
        case categoryLabelEn = "category_label_en"
        case categoryLabelHi = "category_label_hi"
        case source
        case publishedAt = "published_at"
        case importance
        case serverSectorTag = "sector_tag"
    }

    public init(
        id: String,
        title: String,
        summary: String,
        categoryId: String,
        categoryLabelEn: String,
        categoryLabelHi: String,
        source: NewsSource,
        publishedAt: String,
        importance: String,
        serverSectorTag: String? = nil
    ) {
        self.id = id
        self.title = title
        self.summary = summary
        self.categoryId = categoryId
        self.categoryLabelEn = categoryLabelEn
        self.categoryLabelHi = categoryLabelHi
        self.source = source
        self.publishedAt = publishedAt
        self.importance = importance
        self.serverSectorTag = serverSectorTag
    }

    /// Localized category display label
    public func categoryLabel(for language: AppLanguage) -> String {
        switch language {
        case .english:
            return categoryLabelEn
        case .hindi:
            return categoryLabelHi
        }
    }

    /// Detected Chandigarh sector or landmark tag
    public var sectorTag: String {
        if let s = serverSectorTag, !s.isEmpty, s != "CHANDIGARH" {
            return s
        }
        return SectorExtractor.extract(from: title, summary: summary)
    }

    /// Relative time string (e.g., "2h ago" or "2 घंटे पहले")
    public func timeAgo(in language: AppLanguage) -> String {
        guard let date = ISO8601DateFormatter().date(from: publishedAt) ?? parseFallbackDate(publishedAt) else {
            return language == .english ? "Today" : "आज"
        }
        let diff = Date().timeIntervalSince(date)
        let hours = Int(diff / 3600)
        let minutes = Int(diff / 60)

        if language == .english {
            if hours >= 24 {
                let days = hours / 24
                return "\(days)d ago"
            } else if hours > 0 {
                return "\(hours)h ago"
            } else if minutes > 5 {
                return "\(minutes)m ago"
            } else {
                return "Just now"
            }
        } else {
            if hours >= 24 {
                let days = hours / 24
                return "\(days) दिन पहले"
            } else if hours > 0 {
                return "\(hours) घंटे पहले"
            } else if minutes > 5 {
                return "\(minutes) मि. पहले"
            } else {
                return "अभी-अभी"
            }
        }
    }

    private func parseFallbackDate(_ string: String) -> Date? {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ssZZZZZ"
        if let d = formatter.date(from: string) { return d }
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss.SSSSSSZZZZZ"
        return formatter.date(from: string)
    }
}
