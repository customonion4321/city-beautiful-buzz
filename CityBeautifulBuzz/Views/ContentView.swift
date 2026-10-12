//
//  ContentView.swift
//  CityBeautifulBuzz
//
//  Main companion app interface for macOS.
//

import SwiftUI

public struct ContentView: View {
    @StateObject private var service = NewsService.shared
    @State private var language: AppLanguage = .english
    @State private var selectedCategory: String = "all"
    @State private var searchText: String = ""
    @State private var selectedItem: NewsItem? = nil

    @Environment(\.colorScheme) private var colorScheme

    public init() {}

    // Filtered items based on category pill and search query
    private var filteredItems: [NewsItem] {
        var list = service.items

        if selectedCategory != "all" {
            list = list.filter { $0.categoryId.lowercased() == selectedCategory.lowercased() }
        }

        if !searchText.isEmpty {
            let q = searchText.lowercased()
            list = list.filter {
                $0.title.lowercased().contains(q) ||
                $0.summary.lowercased().contains(q) ||
                $0.sectorTag.lowercased().contains(q)
            }
        }

        return list
    }

    private let categories: [(id: String, en: String, hi: String, icon: String)] = [
        ("all", "All Updates", "सभी", "sparkles"),
        ("infrastructure", "Infrastructure", "बुनियादी ढांचा", "wrench.and.screwdriver.fill"),
        ("events", "Events", "कार्यक्रम", "party.popper.fill"),
        ("governance", "Governance", "प्रशासन", "building.columns.fill"),
        ("alerts", "Alerts", "अलर्ट", "exclamationmark.triangle.fill"),
        ("education", "Education", "शिक्षा", "graduationcap.fill"),
        ("lifestyle", "Lifestyle", "जीवनशैली", "cup.and.saucer.fill")
    ]

    public var body: some View {
        ZStack {
            // Adaptive Canvas Background
            (colorScheme == .light ? CorbusierTheme.betonSand : CorbusierTheme.rawConcrete)
                .ignoresSafeArea()

            VStack(spacing: 0) {
                // ── Top Navigation Bar ─────────────────────────────────
                HStack(alignment: .center, spacing: 16) {
                    // Brand mark
                    HStack(spacing: 8) {
                        Text("✋")
                            .font(.system(size: 24))
                        VStack(alignment: .leading, spacing: 1) {
                            Text("City Beautiful Buzz")
                                .font(.system(size: 18, weight: .black, design: .rounded))
                                .foregroundColor(.primary)
                            Text(language == .english ? "CHANDIGARH • CIVIC WIRE" : "चंडीगढ़ • ताज़ा हलचल")
                                .font(.system(size: 9, weight: .bold, design: .monospaced))
                                .foregroundColor(.secondary)
                        }
                    }

                    Spacer()

                    // Search Field
                    HStack(spacing: 6) {
                        Image(systemName: "magnifyingglass")
                            .foregroundColor(.secondary)
                        TextField(language == .english ? "Search sectors, news..." : "सेक्टर या खबर खोजें...", text: $searchText)
                            .textFieldStyle(.plain)
                            .font(.system(size: 13))
                    }
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(Color.primary.opacity(0.06))
                    .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
                    .frame(maxWidth: 240)

                    // English / Hindi Toggle Button
                    HStack(spacing: 2) {
                        ForEach(AppLanguage.allCases) { lang in
                            Button(action: {
                                withAnimation(.spring(response: 0.25, dampingFraction: 0.8)) {
                                    language = lang
                                }
                            }) {
                                HStack(spacing: 4) {
                                    Text(lang.flagIcon)
                                    Text(lang.shortLabel)
                                        .font(.system(size: 12, weight: .bold, design: .rounded))
                                }
                                .padding(.horizontal, 10)
                                .padding(.vertical, 5)
                                .background(language == lang ? Color.accentColor : Color.clear)
                                .foregroundColor(language == lang ? .white : .primary)
                                .clipShape(Capsule())
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(3)
                    .background(Color.primary.opacity(0.07))
                    .clipShape(Capsule())

                    // Refresh Button
                    Button(action: {
                        Task { await service.fetchFeed() }
                    }) {
                        Image(systemName: "arrow.clockwise")
                            .font(.system(size: 13, weight: .bold))
                            .rotationEffect(.degrees(service.isLoading ? 360 : 0))
                            .animation(service.isLoading ? .linear(duration: 1).repeatForever(autoreverses: false) : .default, value: service.isLoading)
                            .padding(8)
                            .background(Color.primary.opacity(0.06))
                            .clipShape(Circle())
                    }
                    .buttonStyle(.plain)
                }
                .padding(.horizontal, 24)
                .padding(.top, 18)
                .padding(.bottom, 12)

                // ── Category Filter Bar ────────────────────────────────
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(categories, id: \.id) { cat in
                            let isSelected = selectedCategory == cat.id
                            Button(action: {
                                withAnimation(.easeInOut(duration: 0.2)) {
                                    selectedCategory = cat.id
                                }
                            }) {
                                HStack(spacing: 6) {
                                    Image(systemName: cat.icon)
                                        .font(.system(size: 11))
                                    Text(language == .english ? cat.en : cat.hi)
                                        .font(.system(size: 12, weight: .bold, design: .rounded))
                                }
                                .padding(.horizontal, 12)
                                .padding(.vertical, 7)
                                .background(isSelected ? Color.primary : Color.primary.opacity(0.06))
                                .foregroundColor(isSelected ? (colorScheme == .light ? .white : .black) : .primary)
                                .clipShape(Capsule())
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(.horizontal, 24)
                    .padding(.vertical, 8)
                }

                Divider()
                    .padding(.top, 4)

                // ── Main Content Area ──────────────────────────────────
                if service.isLoading && service.items.isEmpty {
                    VStack(spacing: 16) {
                        Spacer()
                        ProgressView()
                            .scaleEffect(1.3)
                        Text(language == .english ? "Fetching Chandigarh Civic Wire..." : "चंडीगढ़ की ताज़ा खबरें लोड हो रही हैं...")
                            .font(.system(size: 14, weight: .semibold, design: .rounded))
                            .foregroundColor(.secondary)
                        Spacer()
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else if filteredItems.isEmpty {
                    VStack(spacing: 14) {
                        Spacer()
                        Text("✋")
                            .font(.system(size: 44))
                        Text(language == .english ? "No Updates Found" : "कोई खबर नहीं मिली")
                            .font(.system(size: 18, weight: .bold, design: .rounded))
                            .foregroundColor(.primary)

                        if !searchText.isEmpty || selectedCategory != "all" {
                            Button(action: {
                                searchText = ""
                                selectedCategory = "all"
                            }) {
                                Text(language == .english ? "Reset Filters" : "फ़िल्टर हटाएं")
                                    .font(.system(size: 13, weight: .semibold, design: .rounded))
                                    .padding(.horizontal, 16)
                                    .padding(.vertical, 8)
                                    .background(Color.primary)
                                    .foregroundColor(colorScheme == .light ? .white : .black)
                                    .clipShape(Capsule())
                            }
                            .buttonStyle(.plain)
                        } else {
                            Button(action: {
                                Task { await service.fetchFeed() }
                            }) {
                                Text(language == .english ? "Retry Fetch" : "दोबारा प्रयास करें")
                                    .font(.system(size: 13, weight: .semibold, design: .rounded))
                                    .padding(.horizontal, 16)
                                    .padding(.vertical, 8)
                                    .background(CorbusierTheme.terracotta)
                                    .foregroundColor(.white)
                                    .clipShape(Capsule())
                            }
                            .buttonStyle(.plain)
                        }
                        Spacer()
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                } else {
                    ScrollView {
                        LazyVGrid(
                            columns: [
                                GridItem(.adaptive(minimum: 280, maximum: 340), spacing: 18)
                            ],
                            spacing: 18
                        ) {
                            ForEach(filteredItems) { item in
                                NewsCardView(
                                    item: item,
                                    language: language,
                                    onSelect: { selectedItem = item }
                                )
                            }
                        }
                        .padding(24)
                    }
                }
            }
        }
        .frame(minWidth: 840, idealWidth: 980, minHeight: 600, idealHeight: 700)
        .task {
            if service.items.isEmpty {
                await service.fetchFeed()
            }
        }
        .sheet(item: $selectedItem) { item in
            DetailSheetView(item: item, language: language) {
                selectedItem = nil
            }
        }
    }
}
