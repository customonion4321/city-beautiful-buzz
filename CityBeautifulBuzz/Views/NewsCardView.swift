//
//  NewsCardView.swift
//  CityBeautifulBuzz
//
//  Modular squircle card view adopting Le Corbusier's architectural polychromy
//  and the clean, high-contrast aesthetics of the inspiration references.
//

import SwiftUI

public struct NewsCardView: View {
    public let item: NewsItem
    public let language: AppLanguage
    public let onSelect: (() -> Void)?

    @Environment(\.colorScheme) private var colorScheme
    @State private var isHovered: Bool = false

    public init(item: NewsItem, language: AppLanguage, onSelect: (() -> Void)? = nil) {
        self.item = item
        self.language = language
        self.onSelect = onSelect
    }

    private var cardColor: Color {
        CorbusierTheme.color(for: item.categoryId)
    }

    public var body: some View {
        Button(action: { onSelect?() }) {
            VStack(alignment: .leading, spacing: 12) {
                // ── 1. Header: Category Pill & Sector Badge ─────────────
                HStack(alignment: .center) {
                    // Category pill
                    Text(item.categoryLabel(for: language))
                        .font(.system(size: 11, weight: .bold, design: .rounded))
                        .foregroundColor(.white)
                        .padding(.horizontal, 9)
                        .padding(.vertical, 4.5)
                        .background(Color.white.opacity(0.22))
                        .clipShape(Capsule())

                    Spacer()

                    // Highlighted Chandigarh Sector / Landmark Tag
                    HStack(spacing: 3) {
                        Image(systemName: "mappin.circle.fill")
                            .font(.system(size: 9))
                        Text(item.sectorTag)
                            .font(.system(size: 10, weight: .black, design: .monospaced))
                    }
                    .foregroundColor(.white)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(Color.black.opacity(0.25))
                    .clipShape(RoundedRectangle(cornerRadius: CorbusierTheme.badgeCornerRadius, style: .continuous))
                }

                // ── 2. Headline: Bold, Architectural Typography ─────────
                Text(item.title)
                    .font(.system(size: 16, weight: .bold, design: .rounded))
                    .foregroundColor(.white)
                    .lineLimit(3)
                    .multilineTextAlignment(.leading)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .fixedSize(horizontal: false, vertical: true)

                Spacer(minLength: 4)

                // ── 3. Micro-Graphic Visual Accent (Inspiration Image 1) ─
                HStack {
                    CategoryMicroGraphicView(categoryId: item.categoryId)

                    Spacer()

                    // Optional importance pulse dot
                    if item.importance == "high" {
                        HStack(spacing: 4) {
                            Circle()
                                .fill(Color.white)
                                .frame(width: 6, height: 6)
                            Text("IMPORTANT")
                                .font(.system(size: 9, weight: .black, design: .monospaced))
                                .foregroundColor(.white)
                        }
                        .padding(.horizontal, 6)
                        .padding(.vertical, 3)
                        .background(Color.white.opacity(0.2))
                        .clipShape(Capsule())
                    }
                }

                // ── 4. Footer: Source & Recency ────────────────────────
                Divider()
                    .background(Color.white.opacity(0.25))

                HStack(alignment: .center) {
                    HStack(spacing: 5) {
                        Circle()
                            .fill(Color.white)
                            .frame(width: 5, height: 5)
                        Text(item.source.name)
                            .font(.system(size: 11, weight: .semibold, design: .rounded))
                        Text("•")
                        Text(item.timeAgo(in: language))
                            .font(.system(size: 11, weight: .medium, design: .rounded))
                    }
                    .foregroundColor(Color.white.opacity(0.9))

                    Spacer()

                    Image(systemName: "arrow.up.right")
                        .font(.system(size: 11, weight: .bold))
                        .foregroundColor(Color.white.opacity(0.85))
                }
            }
            .padding(18)
            .frame(minHeight: 220)
            .background(
                ZStack {
                    if colorScheme == .light {
                        cardColor
                    } else {
                        // Dark mode: Deep slate with subtle chromatic glow
                        CorbusierTheme.darkCardSurface
                        LinearGradient(
                            colors: [cardColor.opacity(0.55), cardColor.opacity(0.15)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    }
                }
            )
            .clipShape(RoundedRectangle(cornerRadius: CorbusierTheme.cardCornerRadius, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: CorbusierTheme.cardCornerRadius, style: .continuous)
                    .stroke(
                        colorScheme == .light ? Color.white.opacity(0.25) : cardColor.opacity(0.4),
                        lineWidth: 1.5
                    )
            )
            // Soft floating elevation shadow (matching Image 1)
            .shadow(
                color: cardColor.opacity(colorScheme == .light ? 0.35 : 0.25),
                radius: isHovered ? 18 : 10,
                x: 0,
                y: isHovered ? 8 : 4
            )
            .scaleEffect(isHovered ? 1.015 : 1.0)
            .animation(.spring(response: 0.28, dampingFraction: 0.75), value: isHovered)
        }
        .buttonStyle(.plain)
        .onHover { hovering in
            isHovered = hovering
        }
    }
}
