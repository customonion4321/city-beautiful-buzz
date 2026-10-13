//
//  StoryDeckView.swift
//  CityBeautifulBuzz
//
//  Interactive Card Deck / Story Reader for sequential story browsing.
//  Implements previous/next card flip, architectural typography,
//  and a circular source badge link as specified in the original vision.
//

import SwiftUI
import AppKit

public struct StoryDeckView: View {
    public let items: [NewsItem]
    @Binding public var currentIndex: Int
    public let onDismiss: () -> Void

    @Environment(\.openURL) private var openURL
    @Environment(\.colorScheme) private var colorScheme
    @State private var dragOffset: CGFloat = 0
    @State private var isSourceHovered: Bool = false

    public init(items: [NewsItem], currentIndex: Binding<Int>, onDismiss: @escaping () -> Void) {
        self.items = items
        self._currentIndex = currentIndex
        self.onDismiss = onDismiss
    }

    private var currentItem: NewsItem? {
        guard !items.isEmpty, currentIndex >= 0, currentIndex < items.count else { return nil }
        return items[currentIndex]
    }

    private var themeColor: Color {
        guard let item = currentItem else { return CorbusierTheme.terracotta }
        return CorbusierTheme.color(for: item.categoryId)
    }

    public var body: some View {
        ZStack {
            // Ambient Backdrop
            (colorScheme == .light ? CorbusierTheme.betonSand : CorbusierTheme.rawConcrete)
                .ignoresSafeArea()

            // Subtle chromatic ambient glow matching current card category
            RadialGradient(
                colors: [
                    themeColor.opacity(colorScheme == .light ? 0.18 : 0.28),
                    Color.clear
                ],
                center: .center,
                startRadius: 100,
                endRadius: 520
            )
            .ignoresSafeArea()

            VStack(spacing: 20) {
                // ── Top Bar: Story Progress Segments & Counter ──────────────
                topControlsBar

                Spacer(minLength: 10)

                // ── Central Interactive Card with Navigation ────────────────
                if let item = currentItem {
                    HStack(spacing: 24) {
                        // Previous Arrow Button
                        Button(action: previousCard) {
                            Image(systemName: "chevron.left.circle.fill")
                                .font(.system(size: 38))
                                .foregroundColor(currentIndex > 0 ? .primary.opacity(0.7) : .secondary.opacity(0.2))
                        }
                        .buttonStyle(.plain)
                        .disabled(currentIndex == 0)
                        .keyboardShortcut(.leftArrow, modifiers: [])

                        // Main Architectural Story Card
                        storyCard(item: item)
                            .frame(maxWidth: 620, maxHeight: 460)
                            .offset(x: dragOffset)
                            .gesture(
                                DragGesture()
                                    .onChanged { value in
                                        dragOffset = value.translation.width * 0.5
                                    }
                                    .onEnded { value in
                                        withAnimation(.spring(response: 0.35, dampingFraction: 0.8)) {
                                            if value.translation.width < -60 {
                                                nextCard()
                                            } else if value.translation.width > 60 {
                                                previousCard()
                                            }
                                            dragOffset = 0
                                        }
                                    }
                            )

                        // Next Arrow Button
                        Button(action: nextCard) {
                            Image(systemName: "chevron.right.circle.fill")
                                .font(.system(size: 38))
                                .foregroundColor(currentIndex < items.count - 1 ? .primary.opacity(0.7) : .secondary.opacity(0.2))
                        }
                        .buttonStyle(.plain)
                        .disabled(currentIndex >= items.count - 1)
                        .keyboardShortcut(.rightArrow, modifiers: [])
                    }
                }

                Spacer(minLength: 10)

                // ── Bottom Keyboard & Pagination Hint ───────────────────────
                HStack(spacing: 12) {
                    Text("← / →  Arrow Keys to Browse")
                        .font(.system(size: 11, weight: .semibold, design: .monospaced))
                        .foregroundColor(.secondary)
                    Text("•")
                        .foregroundColor(.secondary.opacity(0.4))
                    Text("ESC to Exit Deck")
                        .font(.system(size: 11, weight: .semibold, design: .monospaced))
                        .foregroundColor(.secondary)
                }
                .padding(.bottom, 14)
            }
            .padding(.horizontal, 28)
            .padding(.top, 20)
        }
        .frame(minWidth: 840, idealWidth: 920, minHeight: 620, idealHeight: 680)
        .onExitCommand(perform: onDismiss)
    }

    // ── Top Navigation Bar ──────────────────────────────────────────────────
    private var topControlsBar: some View {
        VStack(spacing: 12) {
            // Story segmented progress bar
            HStack(spacing: 4) {
                ForEach(0..<min(items.count, 25), id: \.self) { idx in
                    Capsule()
                        .fill(idx <= currentIndex ? themeColor : Color.primary.opacity(0.12))
                        .frame(height: 3.5)
                        .animation(.easeInOut(duration: 0.2), value: currentIndex)
                }
            }

            HStack {
                // Card Counter
                HStack(spacing: 6) {
                    Text("✋")
                    Text("CHANDIGARH WIRE")
                        .font(.system(size: 10, weight: .black, design: .monospaced))
                        .foregroundColor(.secondary)
                    Text("•")
                        .foregroundColor(.secondary)
                    Text("STORY \(currentIndex + 1) OF \(items.count)")
                        .font(.system(size: 10, weight: .black, design: .monospaced))
                        .foregroundColor(themeColor)
                }

                Spacer()

                // Close Button
                Button(action: onDismiss) {
                    HStack(spacing: 4) {
                        Text("Exit Deck")
                            .font(.system(size: 12, weight: .bold, design: .rounded))
                        Image(systemName: "xmark.circle.fill")
                            .font(.system(size: 16))
                    }
                    .foregroundColor(.secondary)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 5)
                    .background(Color.primary.opacity(0.06))
                    .clipShape(Capsule())
                }
                .buttonStyle(.plain)
            }
        }
    }

    // ── Architectural Story Card ────────────────────────────────────────────
    private func storyCard(item: NewsItem) -> some View {
        VStack(alignment: .leading, spacing: 18) {
            // ── 1. Header Metadata ──────────────────────────────────────────
            HStack(alignment: .center) {
                // Category Pill
                Text(item.categoryLabel(for: .english))
                    .font(.system(size: 11, weight: .bold, design: .rounded))
                    .foregroundColor(.white)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 5)
                    .background(Color.white.opacity(0.24))
                    .clipShape(Capsule())

                // Highlighted Sector Tag
                HStack(spacing: 3) {
                    Image(systemName: "mappin.circle.fill")
                        .font(.system(size: 10))
                    Text(item.sectorTag)
                        .font(.system(size: 11, weight: .black, design: .monospaced))
                }
                .foregroundColor(.white)
                .padding(.horizontal, 9)
                .padding(.vertical, 5)
                .background(Color.black.opacity(0.32))
                .clipShape(RoundedRectangle(cornerRadius: CorbusierTheme.badgeCornerRadius, style: .continuous))

                Spacer()

                // Recency Indicator
                Text(item.timeAgo(in: .english))
                    .font(.system(size: 11, weight: .bold, design: .rounded))
                    .foregroundColor(Color.white.opacity(0.88))
            }

            // ── 2. Headline ─────────────────────────────────────────────────
            Text(item.title)
                .font(.system(size: 21, weight: .bold, design: .rounded))
                .foregroundColor(.white)
                .lineLimit(3)
                .lineSpacing(3)
                .multilineTextAlignment(.leading)
                .fixedSize(horizontal: false, vertical: true)

            // ── 3. Summary / Gist ───────────────────────────────────────────
            ScrollView {
                Text(item.summary)
                    .font(.system(size: 14, weight: .regular, design: .default))
                    .lineSpacing(5)
                    .foregroundColor(Color.white.opacity(0.92))
                    .frame(maxWidth: .infinity, alignment: .leading)
            }

            Spacer(minLength: 6)

            // ── 4. Circular Source Emblem Link (Point 4) ────────────────────
            Divider()
                .background(Color.white.opacity(0.24))

            HStack(alignment: .center, spacing: 12) {
                // Circular Source Logo Emblem
                circularSourceEmblem(source: item.source)

                VStack(alignment: .leading, spacing: 2) {
                    Text(item.source.name)
                        .font(.system(size: 13, weight: .bold, design: .rounded))
                        .foregroundColor(.white)
                    Text("Verified 24h Chandigarh Coverage")
                        .font(.system(size: 10, weight: .medium, design: .rounded))
                        .foregroundColor(Color.white.opacity(0.75))
                }

                Spacer()

                // "Read Full Source" Action Button
                if let url = URL(string: item.source.articleUrl), !item.source.articleUrl.isEmpty {
                    Button(action: { openURL(url) }) {
                        HStack(spacing: 6) {
                            Text("Open Source")
                                .font(.system(size: 12, weight: .bold, design: .rounded))
                            Image(systemName: "arrow.up.right")
                                .font(.system(size: 10, weight: .bold))
                        }
                        .padding(.horizontal, 14)
                        .padding(.vertical, 8)
                        .background(Color.white)
                        .foregroundColor(themeColor)
                        .clipShape(Capsule())
                    }
                    .buttonStyle(.plain)
                }
            }
        }
        .padding(26)
        .background(
            ZStack {
                if colorScheme == .light {
                    themeColor
                } else {
                    CorbusierTheme.darkCardSurface
                    LinearGradient(
                        colors: [themeColor.opacity(0.75), themeColor.opacity(0.25)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                }
            }
        )
        .clipShape(RoundedRectangle(cornerRadius: CorbusierTheme.cardCornerRadius, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: CorbusierTheme.cardCornerRadius, style: .continuous)
                .stroke(Color.white.opacity(0.22), lineWidth: 1.5)
        )
        .shadow(color: themeColor.opacity(0.4), radius: 24, x: 0, y: 10)
    }

    // ── Circular Source Emblem ──────────────────────────────────────────────
    private func circularSourceEmblem(source: NewsSource) -> some View {
        Button(action: {
            if let url = URL(string: source.articleUrl) {
                openURL(url)
            }
        }) {
            ZStack {
                Circle()
                    .fill(Color.white)
                    .frame(width: 40, height: 40)
                    .shadow(color: Color.black.opacity(0.15), radius: 4, x: 0, y: 2)

                // Monogram Initial or Emblem Icon
                Text(sourceMonogram(for: source.name))
                    .font(.system(size: 13, weight: .black, design: .serif))
                    .foregroundColor(themeColor)
            }
        }
        .buttonStyle(.plain)
        .help("Click to view full coverage on \(source.name)")
    }

    private func sourceMonogram(for name: String) -> String {
        let n = name.lowercased()
        if n.contains("tribune") { return "T" }
        if n.contains("hindustan") { return "HT" }
        if n.contains("express") { return "IE" }
        if n.contains("amar") { return "AU" }
        if n.contains("police") { return "CP" }
        if n.contains("mc") || n.contains("corporation") { return "MC" }
        if n.contains("admin") { return "UT" }
        return String(name.prefix(2)).uppercased()
    }

    // ── Actions ─────────────────────────────────────────────────────────────
    private func nextCard() {
        if currentIndex < items.count - 1 {
            withAnimation(.spring(response: 0.32, dampingFraction: 0.8)) {
                currentIndex += 1
            }
        }
    }

    private func previousCard() {
        if currentIndex > 0 {
            withAnimation(.spring(response: 0.32, dampingFraction: 0.8)) {
                currentIndex -= 1
            }
        }
    }
}
