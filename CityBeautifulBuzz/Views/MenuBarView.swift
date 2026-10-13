//
//  MenuBarView.swift
//  CityBeautifulBuzz
//
//  Compact Menu Bar companion window popover.
//  Provides 1-click access to Chandigarh civic wire and sector quadrant cards
//  directly from the macOS status bar without keeping the main window open.
//

import SwiftUI
import AppKit

public struct MenuBarView: View {
    @StateObject private var service = NewsService.shared
    @State private var language: AppLanguage = .english
    @State private var selectedSector: String = "ALL"
    @Environment(\.colorScheme) private var colorScheme

    public init() {}

    private var availableSectors: [String] {
        var sectors = Set<String>()
        for item in service.items {
            let tag = item.sectorTag
            if tag != "CHANDIGARH" {
                sectors.insert(tag)
            }
        }
        return ["ALL"] + Array(sectors).sorted()
    }

    private var displayItems: [NewsItem] {
        if selectedSector == "ALL" {
            return Array(service.items.prefix(6))
        }
        return Array(service.items.filter { $0.sectorTag == selectedSector }.prefix(6))
    }

    public var body: some View {
        VStack(spacing: 0) {
            // ── Header Bar ───────────────────────────────────────────────
            HStack(spacing: 8) {
                Text("✋")
                    .font(.system(size: 20))

                VStack(alignment: .leading, spacing: 1) {
                    Text("City Beautiful Buzz")
                        .font(.system(size: 13, weight: .black, design: .rounded))
                        .foregroundColor(.primary)
                    Text(language == .english ? "CHANDIGARH • 24H WIRE" : "चंडीगढ़ • 24 घंटे वायर")
                        .font(.system(size: 8, weight: .bold, design: .monospaced))
                        .foregroundColor(.secondary)
                }

                Spacer()

                // Language toggle
                Button(action: {
                    withAnimation(.spring(response: 0.25, dampingFraction: 0.8)) {
                        language = (language == .english) ? .hindi : .english
                    }
                }) {
                    Text(language.flagIcon)
                        .font(.system(size: 12))
                        .padding(4)
                        .background(Color.primary.opacity(0.08))
                        .clipShape(Circle())
                }
                .buttonStyle(.plain)

                // Refresh button
                Button(action: {
                    Task { await service.fetchFeed() }
                }) {
                    Image(systemName: "arrow.clockwise")
                        .font(.system(size: 11, weight: .bold))
                        .rotationEffect(.degrees(service.isLoading ? 360 : 0))
                        .animation(service.isLoading ? .linear(duration: 1).repeatForever(autoreverses: false) : .default, value: service.isLoading)
                        .padding(5)
                        .background(Color.primary.opacity(0.08))
                        .clipShape(Circle())
                }
                .buttonStyle(.plain)
            }
            .padding(.horizontal, 14)
            .padding(.top, 12)
            .padding(.bottom, 8)

            // ── Sector Filter Pills ─────────────────────────────────────
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 6) {
                    ForEach(availableSectors.prefix(8), id: \.self) { sec in
                        let isSelected = selectedSector == sec
                        Button(action: {
                            withAnimation(.easeInOut(duration: 0.15)) {
                                selectedSector = sec
                            }
                        }) {
                            Text(sec)
                                .font(.system(size: 9, weight: .black, design: .monospaced))
                                .padding(.horizontal, 8)
                                .padding(.vertical, 4)
                                .background(isSelected ? Color.primary : Color.primary.opacity(0.08))
                                .foregroundColor(isSelected ? (colorScheme == .light ? .white : .black) : .primary)
                                .clipShape(Capsule())
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(.horizontal, 14)
                .padding(.vertical, 4)
            }

            Divider()
                .padding(.vertical, 4)

            // ── Card Feed ───────────────────────────────────────────────
            if displayItems.isEmpty {
                VStack(spacing: 8) {
                    Spacer()
                    Text("No updates for \(selectedSector)")
                        .font(.system(size: 11, weight: .medium, design: .rounded))
                        .foregroundColor(.secondary)
                    Spacer()
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
            } else {
                ScrollView {
                    VStack(spacing: 8) {
                        ForEach(displayItems) { item in
                            Button(action: {
                                if let url = URL(string: "cbb://news/\(item.id)") {
                                    NSWorkspace.shared.open(url)
                                }
                            }) {
                                HStack(alignment: .top, spacing: 8) {
                                    // Sector indicator tag
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(item.sectorTag)
                                            .font(.system(size: 8, weight: .black, design: .monospaced))
                                            .foregroundColor(.white)
                                            .padding(.horizontal, 5)
                                            .padding(.vertical, 3)
                                            .background(CorbusierTheme.color(for: item.categoryId))
                                            .clipShape(RoundedRectangle(cornerRadius: 5, style: .continuous))

                                        Text(item.timeAgo(in: language))
                                            .font(.system(size: 8, weight: .semibold, design: .rounded))
                                            .foregroundColor(.secondary)
                                    }
                                    .frame(width: 60, alignment: .leading)

                                    // Headline
                                    VStack(alignment: .leading, spacing: 2) {
                                        Text(item.title)
                                            .font(.system(size: 11, weight: .bold, design: .rounded))
                                            .foregroundColor(.primary)
                                            .lineLimit(2)
                                            .multilineTextAlignment(.leading)

                                        Text(item.source.name)
                                            .font(.system(size: 9, weight: .medium, design: .rounded))
                                            .foregroundColor(.secondary)
                                    }

                                    Spacer()
                                }
                                .padding(8)
                                .background(colorScheme == .light ? Color.white : CorbusierTheme.darkCardSurface)
                                .clipShape(RoundedRectangle(cornerRadius: 10, style: .continuous))
                                .overlay(
                                    RoundedRectangle(cornerRadius: 10, style: .continuous)
                                        .stroke(Color.primary.opacity(0.06), lineWidth: 1)
                                )
                            }
                            .buttonStyle(.plain)
                        }
                    }
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                }
            }

            Divider()

            // ── Footer Bar ──────────────────────────────────────────────
            HStack {
                Button(action: {
                    NSApp.activate(ignoringOtherApps: true)
                    if let window = NSApp.windows.first(where: { $0.canBecomeMain }) {
                        window.makeKeyAndOrderFront(nil)
                    }
                }) {
                    HStack(spacing: 4) {
                        Image(systemName: "macwindow")
                            .font(.system(size: 10))
                        Text(language == .english ? "Open Dashboard" : "डैशबोर्ड खोलें")
                            .font(.system(size: 10, weight: .semibold, design: .rounded))
                    }
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.primary.opacity(0.07))
                    .clipShape(Capsule())
                }
                .buttonStyle(.plain)

                Spacer()

                Button(action: {
                    NSApplication.shared.terminate(nil)
                }) {
                    Text(language == .english ? "Quit" : "बंद करें")
                        .font(.system(size: 10, weight: .medium, design: .rounded))
                        .foregroundColor(.secondary)
                }
                .buttonStyle(.plain)
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 8)
            .background(Color.primary.opacity(0.03))
        }
        .frame(width: 360, height: 440)
        .background(colorScheme == .light ? CorbusierTheme.betonSand : CorbusierTheme.rawConcrete)
    }
}
