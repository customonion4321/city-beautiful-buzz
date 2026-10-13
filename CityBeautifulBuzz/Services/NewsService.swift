//
//  NewsService.swift
//  CityBeautifulBuzz
//
//  Fetches news asynchronously from the live GitHub Pages API,
//  with offline disk caching and bundled fallback support.
//

import Foundation
import Combine
import WidgetKit

@MainActor
public final class NewsService: ObservableObject {
    public static let shared = NewsService()

    @Published public var items: [NewsItem] = []
    @Published public var isLoading: Bool = false
    @Published public var lastUpdated: String = ""
    @Published public var errorMessage: String? = nil

    private let liveFeedURL = URL(string: "https://customonion4321.github.io/city-beautiful-buzz/Backend/data/news.json")!
    private let cacheKey = "cbb_cached_feed_v1"

    public init() {
        loadInitialFeed()
    }

    /// Load from cache or bundled news.json so items are immediately visible
    private func loadInitialFeed() {
        loadCachedFeed()
        if items.isEmpty {
            loadBundledFeed()
        }
    }

    /// Refresh news feed from the live GitHub Pages API
    public func fetchFeed() async {
        isLoading = true
        errorMessage = nil

        do {
            var request = URLRequest(url: liveFeedURL)
            request.cachePolicy = .reloadIgnoringLocalCacheData
            request.timeoutInterval = 15

            let (data, response) = try await URLSession.shared.data(for: request)

            guard let httpResponse = response as? HTTPURLResponse, (200...299).contains(httpResponse.statusCode) else {
                throw URLError(.badServerResponse)
            }

            let decoder = JSONDecoder()
            let feed = try decoder.decode(NewsFeedResponse.self, from: data)

            self.items = feed.items
            self.lastUpdated = feed.lastUpdated

            // Persist to local cache for offline/widget use
            UserDefaults.standard.set(data, forKey: cacheKey)
            print("✅ [NewsService] Successfully fetched and cached \(feed.items.count) live items from GitHub Pages.")

            // Check for new civic alerts and reload desktop widget timelines
            NotificationService.shared.checkAndNotify(for: feed.items)
            WidgetCenter.shared.reloadAllTimelines()
        } catch {
            print("⚠️ [NewsService] Network fetch error: \(error.localizedDescription). Falling back to cached/bundled data.")
            self.errorMessage = error.localizedDescription
            if items.isEmpty {
                loadInitialFeed()
            }
        }

        isLoading = false
    }

    /// Load persisted items from offline cache
    private func loadCachedFeed() {
        guard let data = UserDefaults.standard.data(forKey: cacheKey) else { return }
        if let feed = try? JSONDecoder().decode(NewsFeedResponse.self, from: data) {
            self.items = feed.items
            self.lastUpdated = feed.lastUpdated
            print("📦 [NewsService] Loaded \(feed.items.count) items from local UserDefaults cache.")
        }
    }

    /// Load fallback news.json bundled inside the app
    private func loadBundledFeed() {
        guard let url = Bundle.main.url(forResource: "news", withExtension: "json"),
              let data = try? Data(contentsOf: url) else {
            print("⚠️ [NewsService] news.json not found in app bundle.")
            return
        }
        if let feed = try? JSONDecoder().decode(NewsFeedResponse.self, from: data) {
            self.items = feed.items
            self.lastUpdated = feed.lastUpdated
            print("📂 [NewsService] Loaded \(feed.items.count) items from bundled news.json.")
        }
    }
}
