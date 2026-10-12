//
//  DetailSheetView.swift
//  CityBeautifulBuzz
//
//  Full article reading sheet with source verification and direct link out.
//

import SwiftUI

public struct DetailSheetView: View {
    public let item: NewsItem
    public let language: AppLanguage
    public let onDismiss: () -> Void

    @Environment(\.openURL) private var openURL

    public init(item: NewsItem, language: AppLanguage, onDismiss: @escaping () -> Void) {
        self.item = item
        self.language = language
        self.onDismiss = onDismiss
    }

    private var themeColor: Color {
        CorbusierTheme.color(for: item.categoryId)
    }

    public var body: some View {
        VStack(spacing: 0) {
            // Header bar
            HStack {
                HStack(spacing: 6) {
                    Image(systemName: "mappin.circle.fill")
                        .foregroundColor(themeColor)
                    Text(item.sectorTag)
                        .font(.system(size: 13, weight: .bold, design: .monospaced))
                    Text("•")
                        .foregroundColor(.secondary)
                    Text(item.categoryLabel(for: language))
                        .font(.system(size: 13, weight: .semibold, design: .rounded))
                }

                Spacer()

                Button(action: onDismiss) {
                    Image(systemName: "xmark.circle.fill")
                        .font(.system(size: 20))
                        .foregroundColor(.secondary)
                }
                .buttonStyle(.plain)
            }
            .padding(20)

            Divider()

            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    // Headline
                    Text(item.title)
                        .font(.system(size: 22, weight: .bold, design: .rounded))
                        .foregroundColor(.primary)
                        .fixedSize(horizontal: false, vertical: true)

                    // Metadata row
                    HStack(spacing: 12) {
                        Text(item.source.name)
                            .font(.system(size: 12, weight: .bold, design: .rounded))
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(themeColor.opacity(0.15))
                            .foregroundColor(themeColor)
                            .clipShape(Capsule())

                        Text(item.timeAgo(in: language))
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(.secondary)

                        if item.source.tier == 1 {
                            HStack(spacing: 3) {
                                Image(systemName: "checkmark.seal.fill")
                                    .foregroundColor(.blue)
                                Text("Verified Source")
                                    .font(.system(size: 11, weight: .semibold))
                                    .foregroundColor(.secondary)
                            }
                        }
                    }

                    // Article Summary
                    Text(item.summary)
                        .font(.system(size: 15, weight: .regular, design: .default))
                        .lineSpacing(6)
                        .foregroundColor(.primary)
                        .fixedSize(horizontal: false, vertical: true)

                    Spacer(minLength: 20)

                    // Action buttons
                    HStack(spacing: 12) {
                        if let url = URL(string: item.source.articleUrl), !item.source.articleUrl.isEmpty {
                            Button(action: { openURL(url) }) {
                                HStack(spacing: 6) {
                                    Text(language == .english ? "Read Full Coverage" : "पूरी खबर पढ़ें")
                                        .font(.system(size: 14, weight: .bold, design: .rounded))
                                    Image(systemName: "arrow.up.right")
                                        .font(.system(size: 12, weight: .bold))
                                }
                                .padding(.horizontal, 18)
                                .padding(.vertical, 10)
                                .background(themeColor)
                                .foregroundColor(.white)
                                .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
                            }
                            .buttonStyle(.plain)
                        }

                        Button(action: onDismiss) {
                            Text(language == .english ? "Close" : "बंद करें")
                                .font(.system(size: 14, weight: .semibold, design: .rounded))
                                .padding(.horizontal, 18)
                                .padding(.vertical, 10)
                                .background(Color.secondary.opacity(0.15))
                                .foregroundColor(.primary)
                                .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
                        }
                        .buttonStyle(.plain)
                    }
                }
                .padding(24)
            }
        }
        .frame(minWidth: 480, idealWidth: 540, minHeight: 380, idealHeight: 460)
        .background(.background)
    }
}
