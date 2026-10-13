//
//  CityBeautifulBuzzWidget.swift
//  CityBeautifulBuzzWidget
//
//  Native macOS WidgetKit extension displaying Chandigarh's 4-item news grid.
//  Adopts Le Corbusier's 4-quadrant sector geometry & architectural polychromy.
//

import WidgetKit
import SwiftUI
import AppIntents

// ── Widget Quadrant Card ───────────────────────────────────────────────────────
public struct WidgetQuadrantCard: View {
    public let item: NewsItem
    public let language: AppLanguage

    public init(item: NewsItem, language: AppLanguage = .english) {
        self.item = item
        self.language = language
    }

    private var themeColor: Color {
        CorbusierTheme.color(for: item.categoryId)
    }

    public var body: some View {
        Link(destination: URL(string: "citybuzz://news/\(item.id)") ?? URL(string: item.source.articleUrl)!) {
            VStack(alignment: .leading, spacing: 4) {
                // Top metadata line
                HStack(spacing: 4) {
                    // Sector tag pill
                    Text(item.sectorTag)
                        .font(.system(size: 8, weight: .black, design: .monospaced))
                        .foregroundColor(.white)
                        .padding(.horizontal, 5)
                        .padding(.vertical, 2)
                        .background(Color.black.opacity(0.32))
                        .clipShape(RoundedRectangle(cornerRadius: 4, style: .continuous))

                    Spacer()

                    Text(item.timeAgo(in: language))
                        .font(.system(size: 8, weight: .bold, design: .rounded))
                        .foregroundColor(Color.white.opacity(0.85))
                }

                // Headline
                Text(item.title)
                    .font(.system(size: 11, weight: .bold, design: .rounded))
                    .foregroundColor(.white)
                    .lineLimit(2)
                    .lineSpacing(1.5)
                    .multilineTextAlignment(.leading)
                    .frame(maxWidth: .infinity, alignment: .leading)

                Spacer(minLength: 2)

                // Micro bottom indicator
                HStack(spacing: 3) {
                    Circle()
                        .fill(Color.white)
                        .frame(width: 4, height: 4)
                    Text(item.source.name)
                        .font(.system(size: 8, weight: .semibold, design: .rounded))
                        .foregroundColor(Color.white.opacity(0.9))
                        .lineLimit(1)
                }
            }
            .padding(10)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(themeColor)
            .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 14, style: .continuous)
                    .stroke(Color.white.opacity(0.2), lineWidth: 1)
            )
        }
        .buttonStyle(.plain)
    }
}

// ── Timeline Entry ────────────────────────────────────────────────────────────
public struct CityBuzzWidgetEntry: TimelineEntry {
    public let date: Date
    public let items: [NewsItem]
    public let language: AppLanguage
}

// ── AppIntent Sector Filter Configuration ─────────────────────────────────────
public enum SectorFilterOption: String, AppEnum {
    case all = "ALL"
    case sec17 = "SEC 17"
    case sec22 = "SEC 22"
    case sec26 = "SEC 26"
    case sec35 = "SEC 35"
    case pgimer = "PGIMER"
    case police = "CHD POLICE"
    case alerts = "ALERTS"

    public static var typeDisplayRepresentation: TypeDisplayRepresentation = "Sector Focus"
    public static var caseDisplayRepresentations: [SectorFilterOption: DisplayRepresentation] = [
        .all: "All Chandigarh Sectors",
        .sec17: "Sector 17 (City Centre)",
        .sec22: "Sector 22 (Commercial)",
        .sec26: "Sector 26 (Mandi Hub)",
        .sec35: "Sector 35 (Commercial Hub)",
        .pgimer: "PGIMER (Medical Wire)",
        .police: "Chandigarh Police Wire",
        .alerts: "Civic Alerts (Water/Power/Road)"
    ]
}

public struct ConfigurationAppIntent: WidgetConfigurationIntent {
    public static var title: LocalizedStringResource = "Sector Focus"
    public static var description = IntentDescription("Prioritize stories from a specific Chandigarh sector or civic alert channel.")

    @Parameter(title: "Sector Focus", default: .all)
    public var sector: SectorFilterOption

    public init() {}
    public init(sector: SectorFilterOption) {
        self.sector = sector
    }
}

// ── AppIntent Timeline Provider ───────────────────────────────────────────────
public struct CityBuzzAppIntentTimelineProvider: AppIntentTimelineProvider {
    public typealias Entry = CityBuzzWidgetEntry
    public typealias Intent = ConfigurationAppIntent

    private let feedURL = URL(string: "https://customonion4321.github.io/city-beautiful-buzz/Backend/data/news.json")!

    public func placeholder(in context: Context) -> CityBuzzWidgetEntry {
        CityBuzzWidgetEntry(date: Date(), items: loadInitialItems(), language: .english)
    }

    public func snapshot(for configuration: ConfigurationAppIntent, in context: Context) async -> CityBuzzWidgetEntry {
        let items = filter(items: loadInitialItems(), by: configuration.sector)
        return CityBuzzWidgetEntry(date: Date(), items: items, language: .english)
    }

    public func timeline(for configuration: ConfigurationAppIntent, in context: Context) async -> Timeline<CityBuzzWidgetEntry> {
        var fetchedItems = loadInitialItems()

        do {
            var request = URLRequest(url: feedURL)
            request.timeoutInterval = 10
            let (data, response) = try await URLSession.shared.data(for: request)
            if let http = response as? HTTPURLResponse, (200...299).contains(http.statusCode) {
                let feed = try JSONDecoder().decode(NewsFeedResponse.self, from: data)
                if !feed.items.isEmpty {
                    fetchedItems = feed.items
                }
            }
        } catch {
            print("⚠️ [Widget] Using bundled news.json: \(error.localizedDescription)")
        }

        let filtered = filter(items: fetchedItems, by: configuration.sector)
        let entry = CityBuzzWidgetEntry(date: Date(), items: filtered, language: .english)
        let nextRefresh = Calendar.current.date(byAdding: .minute, value: 15, to: Date()) ?? Date().addingTimeInterval(900)
        return Timeline(entries: [entry], policy: .after(nextRefresh))
    }

    private func filter(items: [NewsItem], by sector: SectorFilterOption) -> [NewsItem] {
        if sector == .all { return items }
        if sector == .alerts {
            let matches = items.filter { $0.categoryId == "alerts" || $0.importance == "high" }
            let rest = items.filter { !matches.contains($0) }
            return matches + rest
        }
        let tag = sector.rawValue.lowercased()
        let matches = items.filter { $0.sectorTag.lowercased().contains(tag) || $0.title.lowercased().contains(tag) }
        let rest = items.filter { !matches.contains($0) }
        return matches + rest
    }

    private func loadInitialItems() -> [NewsItem] {
        if let url = Bundle.main.url(forResource: "news", withExtension: "json"),
           let data = try? Data(contentsOf: url),
           let feed = try? JSONDecoder().decode(NewsFeedResponse.self, from: data) {
            return feed.items
        }
        return sampleFallbackItems()
    }

    private func sampleFallbackItems() -> [NewsItem] {
        return [
            NewsItem(
                id: "1",
                title: "Sector 17 road widening work commences",
                summary: "Municipal Corporation approves widening of main stretch.",
                categoryId: "infrastructure",
                categoryLabelEn: "🏗️ Infra",
                categoryLabelHi: "🏗️ ढांचा",
                source: NewsSource(id: "ht", name: "Hindustan Times", logoUrl: "", color: "#E8001D", articleUrl: "https://hindustantimes.com", language: "en", tier: 1),
                publishedAt: ISO8601DateFormatter().string(from: Date().addingTimeInterval(-3600)),
                importance: "high"
            ),
            NewsItem(
                id: "2",
                title: "Navratri Mela at Leisure Valley: Free entry Oct 20-29",
                summary: "Folk performances, food stalls, and garba nights.",
                categoryId: "events",
                categoryLabelEn: "🎭 Events",
                categoryLabelHi: "🎭 कार्यक्रम",
                source: NewsSource(id: "tribune", name: "The Tribune", logoUrl: "", color: "#0047AB", articleUrl: "https://tribuneindia.com", language: "en", tier: 1),
                publishedAt: ISO8601DateFormatter().string(from: Date().addingTimeInterval(-7200)),
                importance: "medium"
            ),
            NewsItem(
                id: "3",
                title: "Water supply maintenance in Sectors 22–26 on Oct 14",
                summary: "Scheduled interruption for pipeline overhaul.",
                categoryId: "alerts",
                categoryLabelEn: "⚠️ Alert",
                categoryLabelHi: "⚠️ अलर्ट",
                source: NewsSource(id: "jagran", name: "Dainik Jagran", logoUrl: "", color: "#FF6200", articleUrl: "https://jagran.com", language: "hi", tier: 2),
                publishedAt: ISO8601DateFormatter().string(from: Date().addingTimeInterval(-10800)),
                importance: "high"
            ),
            NewsItem(
                id: "4",
                title: "Panjab University announces inter-college sports calendar",
                summary: "Over 40 colleges competing across 18 sporting events.",
                categoryId: "education",
                categoryLabelEn: "🎓 Education",
                categoryLabelHi: "🎓 शिक्षा",
                source: NewsSource(id: "amar_ujala", name: "Amar Ujala", logoUrl: "", color: "#DD0000", articleUrl: "https://amarujala.com", language: "hi", tier: 2),
                publishedAt: ISO8601DateFormatter().string(from: Date().addingTimeInterval(-14400)),
                importance: "medium"
            )
        ]
    }
}

// ── Widget Entry View ─────────────────────────────────────────────────────────
public struct CityBeautifulBuzzWidgetEntryView : View {
    @Environment(\.widgetFamily) var family
    public let entry: CityBuzzWidgetEntry

    public var body: some View {
        switch family {
        case .systemMedium:
            let displayItems = Array(entry.items.prefix(4))
            HStack(spacing: 8) {
                VStack(spacing: 8) {
                    if displayItems.indices.contains(0) {
                        WidgetQuadrantCard(item: displayItems[0], language: entry.language)
                    }
                    if displayItems.indices.contains(2) {
                        WidgetQuadrantCard(item: displayItems[2], language: entry.language)
                    }
                }
                VStack(spacing: 8) {
                    if displayItems.indices.contains(1) {
                        WidgetQuadrantCard(item: displayItems[1], language: entry.language)
                    }
                    if displayItems.indices.contains(3) {
                        WidgetQuadrantCard(item: displayItems[3], language: entry.language)
                    }
                }
            }
            .padding(10)

        case .systemLarge:
            let displayItems = Array(entry.items.prefix(4))
            VStack(spacing: 10) {
                HStack {
                    Text("✋ City Beautiful Buzz")
                        .font(.system(size: 13, weight: .black, design: .rounded))
                    Spacer()
                    Text("CHANDIGARH")
                        .font(.system(size: 9, weight: .bold, design: .monospaced))
                        .foregroundColor(.secondary)
                }

                HStack(spacing: 8) {
                    VStack(spacing: 8) {
                        if displayItems.indices.contains(0) {
                            WidgetQuadrantCard(item: displayItems[0], language: entry.language)
                        }
                        if displayItems.indices.contains(2) {
                            WidgetQuadrantCard(item: displayItems[2], language: entry.language)
                        }
                    }
                    VStack(spacing: 8) {
                        if displayItems.indices.contains(1) {
                            WidgetQuadrantCard(item: displayItems[1], language: entry.language)
                        }
                        if displayItems.indices.contains(3) {
                            WidgetQuadrantCard(item: displayItems[3], language: entry.language)
                        }
                    }
                }
            }
            .padding(14)

        default:
            if let topItem = entry.items.first {
                WidgetQuadrantCard(item: topItem, language: entry.language)
                    .padding(8)
            } else {
                Text("No news available")
                    .font(.caption)
            }
        }
    }
}

// ── Widget Configuration ──────────────────────────────────────────────────────
public struct CityBeautifulBuzzWidget: Widget {
    public let kind: String = "CityBeautifulBuzzWidget"

    public init() {}

    public var body: some WidgetConfiguration {
        AppIntentConfiguration(kind: kind, intent: ConfigurationAppIntent.self, provider: CityBuzzAppIntentTimelineProvider()) { entry in
            CityBeautifulBuzzWidgetEntryView(entry: entry)
                .containerBackground(CorbusierTheme.betonSand, for: .widget)
        }
        .configurationDisplayName("City Beautiful Buzz")
        .description("Chandigarh's 4-item live news and civic event grid. Long-press or right-click to edit sector focus.")
        .supportedFamilies([.systemMedium, .systemLarge, .systemSmall])
    }
}
